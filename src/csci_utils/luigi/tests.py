import os
import boto3

from unittest import TestCase
from tempfile import TemporaryDirectory, NamedTemporaryFile

from pandas import DataFrame
from dask import dataframe as dd

from csci_utils.io import atomic_write
from csci_utils.luigi.dask.target import CSVTarget
from csci_utils.luigi.target import SuffixPreservingLocalTarget
from csci_utils.luigi.task import Download, TargetOutput
from luigi import Parameter, ExternalTask
from luigi.format import Nop
from luigi.contrib.s3 import S3Target, S3Client

from moto import mock_s3


class SuffixPreservingLocalTargetTest(TestCase):
    test_file = "test.txt"

    def create_target(self, path, format=None):
        return SuffixPreservingLocalTarget(path, format=format)

    def test_file_exists(self):
        """
        Test that file is created as expected and temporary
        file is removed
        :return:
        """
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, self.test_file)
            t = self.create_target(fp)
            p = t.open("w")
            self.assertEqual(t.exists(), os.path.exists(fp))
            p.close()
            self.assertEqual(t.exists(), os.path.exists(fp))
            self.assertFalse(os.path.exists(p.name))

    def test_temp_file_extension(self):
        """
        Test that temporary file maintains extension
        :return:
        """
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, self.test_file)
            t = self.create_target(fp)
            p = t.open("w")
            parent_dir, filename = os.path.split(p.name)
            filename, ext = os.path.splitext(filename)
            self.assertEqual(ext, ".txt")


class MockSaveFileTask(ExternalTask):
    downloadFile = Parameter()
    contentFile = Parameter()

    def output(self):
        return S3Target("s3://mybucket/{}".format(self.downloadFile), format=Nop)


class MockDownload(Download):
    downloadFile = Parameter()
    LOCAL_ROOT = Parameter()
    contentFile = Parameter()

    def requires(self):
        return MockSaveFileTask(
            downloadFile=self.downloadFile, contentFile=self.contentFile
        )


@mock_s3
class DownloadTest(TestCase):
    AWS_ACCESS_KEY = "XXXXXXXXXXXXXXXXXXXX"
    AWS_SECRET_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    def setUp(self):
        f = NamedTemporaryFile(mode="wb", delete=False)
        self.tempFileContents = (
            b"I'm a temporary file for testing\nAnd this is the second line\n"
            b"This is the third."
        )
        self.tempFilePath = f.name
        f.write(self.tempFileContents)
        f.close()
        self.addCleanup(os.remove, self.tempFilePath)

    def test_run(self):
        test_file = "testme.text"
        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="mybucket")
        client = S3Client(self.AWS_ACCESS_KEY, self.AWS_SECRET_KEY)
        client.put(self.tempFilePath, "s3://mybucket/{}".format(test_file))

        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, test_file)
            mock = MockDownload(
                contentFile=self.tempFilePath, downloadFile=test_file, LOCAL_ROOT=tmp
            )
            mock.run()
            self.assertTrue(os.path.exists(fp))
            with open(fp, "r") as f:
                content = f.read()
            self.assertTrue(self.tempFileContents, content)


class TargetOutputTest(TestCase):
    """
    Test Target Output to ensure targets are retrieved and written as expected
    """

    def test_read_target(self):
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "test.csv")
            tempFileContents = b"a,b,c,d\n" b"1,2,3,4\n" b"5,6,7,8\n"

            class MockTargetOutputTask(ExternalTask):
                output = TargetOutput(
                    target_class=CSVTarget,
                    file_pattern=tmp,
                    ext="",
                    flag=None,
                    glob="*.csv",
                )

            with atomic_write(fp, "wb") as f:
                f.write(tempFileContents)

            target = MockTargetOutputTask()
            csv_target = target.output()
            self.assertTrue(isinstance(csv_target, CSVTarget))
            df = csv_target.read_dask()
            rows, cols = df.compute().shape
            self.assertEqual(rows, 2)
            self.assertEqual(cols, 4)

    def test_write_target(self):
        test_dict = {"test 1": [1, 2], "test_2": [3, 4]}
        test_dict = DataFrame(data=test_dict)
        with TemporaryDirectory() as tmp:
            class MockTargetOutputTask(ExternalTask):
                output = TargetOutput(
                    target_class=CSVTarget,
                    file_pattern=tmp+"/{task.__class__.__name__}",
                    ext=".csv",
                    glob="*.csv",
                )
            target = MockTargetOutputTask()
            csv_target = target.output()
            self.assertTrue(isinstance(csv_target, CSVTarget))
            out = dd.from_pandas(test_dict, npartitions=1)
            csv_target.write_dask(out, compute=True, index=False)
            df = csv_target.read_dask()
            panda = df.compute()
            rows, cols = panda.shape
            self.assertEqual(rows, 2)
            self.assertEqual(cols, 2)
