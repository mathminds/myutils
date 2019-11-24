from csci_utils.io.enhancedwrite import atomic_write
from csci_utils.luigi.dask.target import ParquetTarget, CSVTarget
from dask import dataframe as dd
from pandas import DataFrame
from tempfile import TemporaryDirectory
from unittest import TestCase

import os


def create_csv_target(path):
    return CSVTarget(path, glob="*.csv")


def create_parquet_target(path):
    return ParquetTarget(path)


class BaseDaskTargetTest(TestCase):
    def create_dataframe(self):
        test_dict = {
            "test_1": [1, 2, 3, 4],
            "test_2": [5, 6, 7, 8],
            "test_3": [9, 10, 11, 12],
        }
        return DataFrame(data=test_dict)

    def test_read_parquet(self):
        test_dict = self.create_dataframe()
        with TemporaryDirectory() as tmp:
            fp1 = os.path.join(tmp, "test-1.parquet")
            fp2 = os.path.join(tmp, "test-2.parquet")

            with atomic_write(fp1, as_file=False) as pf1:
                test_dict.to_parquet(pf1)

            with atomic_write(fp2, as_file=False) as pf2:
                test_dict.to_parquet(pf2)

            t = create_parquet_target(tmp)
            df = t.read_dask(check_complete=False)
            v = df["test_1"]
            self.assertEqual(len(v), 8)

    def test_write_parquet(self):
        df = self.create_dataframe()
        dask_df = dd.from_pandas(df, npartitions=3)
        with TemporaryDirectory() as tmp:
            t = create_parquet_target(tmp)
            t.write_dask(collection=dask_df, compute=True)
            assert os.path.exists(os.path.join(tmp, "_SUCCESS"))
            for n in range(2):
                assert os.path.exists(os.path.join(tmp, "part.{}.parquet".format(n)))

    def test_read_csv(self):
        test_dict = self.create_dataframe()
        with TemporaryDirectory() as tmp:
            fp1 = os.path.join(tmp, "test-1.csv")
            fp2 = os.path.join(tmp, "test-2.csv")

            with atomic_write(fp1, as_file=False) as pf1:
                test_dict.to_csv(pf1)

            with atomic_write(fp2, as_file=False) as pf2:
                test_dict.to_csv(pf2)

            t = create_csv_target(tmp)
            df = t.read_dask(check_complete=False)
            v = df["test_1"]
            self.assertEqual(len(v), 8)

    def test_write_csv(self):
        df = self.create_dataframe()
        dask_df = dd.from_pandas(df, npartitions=3)
        with TemporaryDirectory() as tmp:
            t = create_csv_target(tmp)
            t.write_dask(collection=dask_df)
            assert os.path.exists(os.path.join(tmp, "_SUCCESS"))
            for n in range(2):
                assert os.path.exists(os.path.join(tmp, "{}.csv".format(n)))
