#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `csci_utils` package."""

import os
import pandas as pd
from tempfile import TemporaryDirectory
from unittest import TestCase
from contextlib import contextmanager

from csci_utils.hash_str import hash_str, get_csci_salt, get_user_id
from csci_utils.io import atomic_write
from csci_utils.io import (
    get_user_hash,
    convert_excel_to_parquet,
    read_parquet_columns,
)

@contextmanager
def set_env(**kwargs):
    """context manager used for temporarily setting os environment variables"""
    _environ = dict(os.environ)
    os.environ.update(kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(_environ)


class FakeFileFailure(IOError):
    """Class used to define a fake file failure that can be raised to mimic a real error"""

    pass


class HashTests(TestCase):
    # Tests for 'hash_str'
    def test_basic(self):
        """basic test to ensure hash is computed properly"""
        self.assertEqual(hash_str("world!", salt="hello, ").hex()[:6], "68e656")

    def test_empty_string(self):
        """ensure empty string and salt return a valid hash"""
        self.assertEqual(hash_str("", salt="").hex()[:6], "e3b0c4")

    def test_nonstring_input(self):
        """ensure invalid input types raise an error"""
        # invalid input type to hash
        self.assertRaises(TypeError, hash_str, 12345.6789)
        # invalid salt type
        self.assertRaises(TypeError, hash_str, "hello", salt=-57)

    def test_diff_inputs_diff_hash(self):
        """ensure different inputs lead to different hashes"""
        # same strings, different salts
        self.assertNotEqual(
            hash_str("mystring", salt="mysalt1").hex(),
            hash_str("mystring", salt="mysalt2").hex(),
        )
        # different strings, same salts
        self.assertNotEqual(
            hash_str("mystring1", salt="mysalt").hex(),
            hash_str("mystring2", salt="mysalt").hex(),
        )

    # Tests for 'get_user_hash'
    def test_user_hash_with_salt(self):
        """ensure user hash is computed properly when username and salt are provided"""
        self.assertEqual(get_user_hash("johndoe", salt="jane").hex()[:6], "fb0bf4")

    def test_user_hash_without_salt(self):
        """ensure user hash is computed properly when username alone is provided"""
        salt_bytes = "my salt".encode()
        salt_hex = salt_bytes.hex()
        with set_env(CSCI_SALT=salt_hex):
            expected = hash_str("johndoe", salt=salt_bytes).hex()[:6]
            actual = get_user_hash("johndoe").hex()[:6]
            self.assertEqual(expected, actual)

    def test_user_hash_empty_salt(self):
        """ensure user hash is computed properly with empty string as salt"""
        salt_bytes = "my salt".encode()
        salt_hex = salt_bytes.hex()
        with set_env(CSCI_SALT=salt_hex):
            expected = hash_str("johndoe", salt=salt_bytes).hex()[:6]
            actual = get_user_hash("johndoe", salt="").hex()[:6]
            self.assertEqual(expected, actual)

    # Tests for 'get_user_id'
    def test_basic_user_id_hash(self):
        """ensure user id hash is computed properly and the same regardless of letter case"""
        salt_bytes = "my salt".encode()
        salt_hex = salt_bytes.hex()
        with set_env(CSCI_SALT=salt_hex):
            # ensure we get the correct hash regardless of the letter case used
            self.assertEqual(get_user_id("johndoe"), "7d324c87")
            self.assertEqual(get_user_id("JohnDoe"), "7d324c87")
            self.assertEqual(get_user_id("johndoe".upper()), "7d324c87")


class SaltTests(TestCase):
    def test_csci_salt(self):
        """ensure SALT environment variable is properly retrieved"""
        salt_bytes = "my csci salt".encode()
        salt_hex = salt_bytes.hex()
        with set_env(CSCI_SALT=salt_hex):
            self.assertEqual(get_csci_salt(), salt_bytes)


class AtomicWriteTests(TestCase):
    def test_atomic_write(self):
        """Ensure file exists after being written successfully"""
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "asdf.txt")

            # perform an atomic write
            with atomic_write(fp, "w") as f:
                assert not os.path.exists(fp)
                tmpfile = f.name
                f.write("asdf")

            # ensure tmp file has been deleted
            assert not os.path.exists(tmpfile)
            # ensure file to write to exists
            assert os.path.exists(fp)

            # ensure content of destination file is what we expect
            with open(fp) as f:
                self.assertEqual(f.read(), "asdf")

    def test_atomic_failure(self):
        """Ensure that file does not exist after failure during write"""
        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "asdf.txt")

            # raise fake error while writing file atomically
            with self.assertRaises(FakeFileFailure):
                with atomic_write(fp, "w") as f:
                    tmpfile = f.name
                    assert os.path.exists(tmpfile)
                    raise FakeFileFailure()

            # ensure both the temp and destination files do not exist
            assert not os.path.exists(tmpfile)
            assert not os.path.exists(fp)

    def test_file_exists(self):
        """Ensure an error is raised when file already exists"""
        with TemporaryDirectory() as tmp:
            # define path to file
            fp = os.path.join(tmp, "asdf.txt")

            # write atomically to file
            with atomic_write(fp, "w") as f:
                f.write("asdf")

            # ensure file exists
            assert os.path.exists(fp)

            # ensure atomic_write to same file raises an error as it already exists
            try:
                with atomic_write(fp, "w") as f:
                    f.write("asdf")
            except FileExistsError as e:
                self.assertIsInstance(e, FileExistsError)

    def test_as_file_false(self):
        """To ensure a path to a temporary file is returned when parameter as_file is False."""
        with TemporaryDirectory() as tmp:
            # define path to file
            fp = os.path.join(tmp, "asdf.txt")

            # invoke atomic_write with param as_file set to False
            # this should return a temporary file path string
            with atomic_write(fp, as_file=False) as f:
                self.assertIsInstance(f, str)


class ParquetTests(TestCase):
    def test_read_cols(self):
        """ensure only requested cols are read and returned"""
        with TemporaryDirectory() as tmp:
            parquet_file = os.path.join(tmp, "myfile.parquet")

            # create dataframe with some data
            df = pd.DataFrame({"a": [1, 2], "b": ["hello", "world"]})

            # save df to parquet file
            with atomic_write(parquet_file, as_file=False) as f:
                df.to_parquet(f, engine="pyarrow")

            # read specific columns using the read_parquet_columns function
            col_a = read_parquet_columns(parquet_file, ["a"])
            col_b = read_parquet_columns(parquet_file, ["b"])
            col_a_and_b = read_parquet_columns(parquet_file, ["a", "b"])

            # ensure we are getting dataframe instances
            for tmp_df in [col_a, col_b, col_a_and_b]:
                self.assertIsInstance(tmp_df, pd.DataFrame)

            # ensure content of extracted columns match expected values
            for col, result in zip(
                [["a"], ["b"], ["a", "b"]], [col_a, col_b, col_a_and_b]
            ):
                self.assertTrue(df[col].equals(result))

    def test_convert_xlsx_to_parquet(self):
        """ensure xlsx can be converted to equivalent parquet file"""
        # use temp dir where files will be created for testing purposes
        # the underlying context manager will remove the temp dir and all its content when it closes
        with TemporaryDirectory() as tmp:
            # define path to files
            fp_xlsx = os.path.join(tmp, "myfile.xlsx")
            fp_parquet = os.path.join(tmp, "myfile.parquet")

            # create dataframe with some data
            df_xlsx = pd.DataFrame({"a": [1, 2], "b": ["hello", "world"]})

            # save df to xlsx file
            with atomic_write(fp_xlsx, as_file=False) as f:
                df_xlsx.to_excel(f)

            # invoked function 'convert_excel_to_parquet' to convert the xlsx file to a parquet file
            parquet_filepath = convert_excel_to_parquet(fp_xlsx)

            # verify filename returned match filepath specified
            self.assertEqual(fp_parquet, parquet_filepath)
            # verify the parquet file was created
            self.assertTrue(os.path.exists(fp_parquet))
            # ensure contents of xlsx and parquet files match
            df_parquet = pd.read_parquet(fp_parquet, engine="pyarrow")
            self.assertTrue(df_xlsx.equals(df_parquet))
