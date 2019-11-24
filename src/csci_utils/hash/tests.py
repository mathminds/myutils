from csci_utils.hash.hash_str import hash_str, get_csci_salt, get_user_id
from contextlib import contextmanager
from unittest import TestCase
import os


@contextmanager
def mock_env(variable, value):
    """
    Context Manager that replaces environment with a test environment context.
    This allows test execution to occur using specific environment variables
    :param variable:
    :param value:
    :return:
    """
    current_value = os.getenv(variable)
    try:
        if value:
            os.environ[variable] = bytes(value, "utf-8").hex()
        elif variable in os.environ:
            del os.environ[variable]

        yield

    finally:
        if current_value:
            os.environ[variable] = current_value
        elif variable in os.environ:
            del os.environ[variable]


class HashTests(TestCase):
    test_salt = "test"

    def test_basic(self):
        self.assertEqual(hash_str("world!", salt="hello, ").hex()[:6], "68e656")

    def test_no_value_available(self):
        """Test no value provided for hash"""
        with self.assertRaises(ValueError):
            hash_str(None, salt=self.test_salt)

    def test_no_value_provided_for_salt(self):
        """Test no salt provided for hash"""
        with self.assertRaises(ValueError):
            hash_str("world!", salt=None)

    def test_env_salt_no_os_var(self):
        """Test environment contains no salt"""
        with mock_env(variable="CSCI_SALT", value=None):
            self.assertEqual(get_csci_salt(), None)

    def test_env_salt_with_os_var(self):
        """Test environment contains expected salt value"""
        with mock_env("CSCI_SALT", self.test_salt):
            self.assertEqual(get_csci_salt(), bytes(self.test_salt, "utf-8"))

    def test_get_user_id(self):
        """Test get user id with salt value"""
        with mock_env("CSCI_SALT", self.test_salt):
            username = "TestUser"
            self.assertEqual(
                get_user_id(username),
                hash_str(username.lower(), self.test_salt).hex()[:8],
            )

    def test_get_user_id_no_salt_available(self):
        """Test get user with no salt available"""
        with mock_env("CSCI_SALT", None):
            with self.assertRaises(ValueError):
                get_user_id("fakeuser")
