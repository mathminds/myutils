from csci_utils.io import atomic_write
from os import path
import pandas as pd


def get_parquet_file_name(file):
    """
    Given a filename return the filename with the
    parquet extension

    :param file: filename with path
    :return: filename with parquet extension
    """
    dir_path, filename = path.split(file)
    name, ext = path.splitext(filename)
    parquet_filename = name + ".parquet"
    return path.join(dir_path, parquet_filename)


def convert_xls_to_parquet(xls_file, sheet):
    """
    Convert the provided xls sheet to a parquet file

    :param xls_file:
    :param sheet:
    :return: parquet file name
    """
    with open(xls_file, "r+b") as fp:
        df = pd.read_excel(fp, sheet_name=sheet)
        parquet_file = get_parquet_file_name(xls_file)
        with atomic_write(parquet_file, as_file=False) as pf:
            df.to_parquet(pf)

        return parquet_file


def get_parquet_column(parquet_file, column_name):
    """
    Return an array of values for specific column in a parquet file

    :param parquet_file: filename for parquet file
    :param column_name: column name
    :return: numpy array of column values
    """
    with open(parquet_file, "r+b") as fp:
        df = pd.read_parquet(fp, columns=[column_name])
        return df.iloc[:, 0].to_numpy()
