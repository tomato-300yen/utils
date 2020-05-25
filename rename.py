import argparse
import datetime
import glob
import os
import shutil

import pandas as pd
from tqdm import tqdm

now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_OUTPUT_DIR = os.path.join(ROOT_DIR, "pdf_output", now)
PDF_INPUT_DIR = os.path.join(ROOT_DIR, "pdf_input")
CSV_INPUT_DIR = os.path.join(ROOT_DIR, "csv_here")
LOG_DIR = os.path.join(ROOT_DIR, "log")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_INPUT_DIR, exist_ok=True)
os.makedirs(CSV_INPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

csv_failure = os.path.join(LOG_DIR, f'failure_{now}.txt')
csv_success = os.path.join(LOG_DIR, f'success_{now}.txt')


def main(csv_path, from_column, to_column):
    # search pdf and read csv
    try:
        df = pd.read_csv(csv_path, usecols=[from_column, to_column], dtype=str, encoding="CP932")
    except FileNotFoundError:
        input(f'csvを読み込めませんでした。正しいcsv名を"-i"オプションで指定してください。(default:"relational_data.csv")')
        exit(-1)
    pdf_list = glob.glob(os.path.join(PDF_INPUT_DIR, "**/*.pdf"), recursive=True)

    # copy and rename
    for src_path in tqdm(pdf_list):
        pdf_name = os.path.basename(src_path)

        # get filename
        try:
            df_trg_pdf_name = df[df[from_column] == pdf_name]
            if len(df_trg_pdf_name) != 1:
                raise KeyError
        except KeyError:
            with open(csv_failure, mode="a") as f:
                f.write(pdf_name)
            continue

        trg_pdf_name = df_trg_pdf_name.iloc[0, 0]
        trg_pdf_name += ".pdf"

        # copy
        trg_path = os.path.join(PDF_OUTPUT_DIR, trg_pdf_name)
        shutil.copy(src_path, trg_path)

        with open(csv_success, mode="a") as f:
            f.write(pdf_name)


if __name__ == '__main__':
    # make parser
    parser = argparse.ArgumentParser(description='汎用的なリネームプログラム。"before"と"after"なる列を持ったcsvを読み込ませられる。')

    # add arguments
    parser.add_argument('-i', '--input_csv', default="relational_data.csv",
                        help="読み込むcsvの名前。ex)csv_here/relational_data.csvにあるcsvの場合は'relational_data.csv'")
    parser.add_argument('-f', '--from_column', default="before", help="変換前のファイル名が格納されている列名")
    parser.add_argument('-t', '--to_column', default="after", help="変換後のファイル名が格納されている列名")

    # parse arguments
    args = parser.parse_args()

    main(os.path.join(CSV_INPUT_DIR, args.input_csv), args.from_column, args.to_column)
