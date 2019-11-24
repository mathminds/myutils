from os import path
from tempfile import TemporaryDirectory, TemporaryFile
from unittest import TestCase
from csci_utils.io.enhancedwrite import atomic_write


class FakeFileFailure(IOError):
    pass


class AtomicWriteTests(TestCase):
    def test_atomic_write(self):
        """Ensure file exists after being written successfully"""

        with TemporaryDirectory() as tmp:
            fp = path.join(tmp, "asdf.txt")

            with atomic_write(fp, "w") as f:
                assert not path.exists(fp)
                tmpfile = f.name
                f.write("asdf")

            assert not path.exists(tmpfile)
            assert path.exists(fp)

            with open(fp) as f:
                self.assertEqual(f.read(), "asdf")

    def test_atomic_failure(self):
        """Ensure that file does not exist after failure during write"""

        with TemporaryDirectory() as tmp:
            fp = path.join(tmp, "asdf.txt")

            with self.assertRaises(FakeFileFailure):
                with atomic_write(fp, "w") as f:
                    tmpfile = f.name
                    assert path.exists(tmpfile)
                    raise FakeFileFailure()

            assert not path.exists(tmpfile)
            assert not path.exists(fp)

    def test_file_exists(self):
        """Ensure an error is raised when a file exists"""

        with TemporaryFile() as tf:
            tf.write(b"already here!")
            with self.assertRaises(FileExistsError):
                with atomic_write(tf.name) as f:
                    raise AssertionError("File exists was not properly detected!")

    def test_atomic_write_by_name(self):
        """Ensure file name is correctly returned vs file object"""

        with TemporaryDirectory() as tmp:
            fp = path.join(tmp, "asdf.txt")
            _, filename = path.split(fp)
            with atomic_write(fp, "w", False) as f:
                _, temp_filename = path.split(f)
                _, ext = path.splitext(temp_filename)
                self.assertTrue(type(temp_filename) == str)
                self.assertEqual(".txt", ext)
