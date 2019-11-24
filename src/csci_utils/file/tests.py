import os
from csci_utils.io.enhancedwrite import atomic_write
from csci_utils.file.parquet import (
    get_parquet_column,
    get_parquet_file_name,
    convert_xls_to_parquet,
)
from tempfile import TemporaryDirectory
from unittest import TestCase
from pandas import DataFrame


class ParquetTests(TestCase):
    def test_get_parquet_file_name_with_path(self):
        """Ensure filename changes to appropriate extension"""
        filename = "/data/fakefile.txt"
        self.assertEqual("/data/fakefile.parquet", get_parquet_file_name(filename))

    def test_get_parquet_file_name_no_path(self):
        """Ensure filename changes to appropriate extension"""
        filename = "fakefile.txt"
        self.assertEqual("fakefile.parquet", get_parquet_file_name(filename))

    def test_get_parquet_column(self):
        """Ensure a column can be retrieved from a parquet file"""

        # create a data frame for testing
        test_list = [1, 2]
        test_column = "test_1"
        test_dict = {test_column: test_list, "test_2": [3, 4]}
        test_dict = DataFrame(data=test_dict)

        # create a temporary directory and write the df as a parquet file for test
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "test.parquet")
            with atomic_write(fp, as_file=False) as pf:
                test_dict.to_parquet(pf)

            self.compare_columns(fp, test_column, test_list)

    def test_convert_xls_to_parquet(self):
        """Ensure a Parquet file can be created from and Excel file"""

        # create a data frame for testing
        test_list = [1, 2]
        test_column = "test_1"
        test_dict = {test_column: test_list, "test_2": [3, 4]}
        test_dict = DataFrame(data=test_dict)

        # create a temporary directory and write the df as a parquet file for test
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "test.xls")

            with atomic_write(fp, as_file=False) as pf:
                test_dict.to_excel(pf, "Sheet1")

            parquet_file = convert_xls_to_parquet(fp, "Sheet1")
            self.assertTrue(os.path.exists(parquet_file))
            self.compare_columns(parquet_file, test_column, test_list)

    def compare_columns(self, file, test_column, test_list):
        column_values = get_parquet_column(file, test_column).tolist()
        # compare the test list against what was retrieved from parquet file
        for i, j in zip(column_values, test_list):
            if i != j:
                self.fail("Values do not match")
