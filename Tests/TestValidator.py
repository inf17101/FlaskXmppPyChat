import unittest, sys, pytest
from unittest.mock import patch
sys.path.append("/home/xmppweb/XmppChat/xmppchat/")
sys.path.append("/home/xmppweb/XmppChat/")
from xmppchat.api import app
from xmppchat.models import User
from xmppchat.Validator import Validator

class TestValidator(unittest.TestCase):

    def setUp(self):
        """
            set up valid and invalid strings for each unit test case.
        """
        self.valid_strings = ["testuser3","hallo123", "user2ultimate", "user234user123"]
        self.invalid_strings = ["123user", "asldjf-(asdf", "\\asdf\\asdf.", ".asfsasf"]

    def test_contains_invalid_characters_false(self):
        """
            test: username contains valid characters.
        """
        result = [Validator.contains_invalid_characters(name) for name in self.valid_strings]
        self.assertFalse(all(result))

    def test_contains_invalid_characters_true(self):
        """
            test: username contains invalid characters e.g. .-/ or starts with digits. -> behaviour defined as regex
        """
        result = [Validator.contains_invalid_characters(name) for name in self.invalid_strings]
        self.assertTrue(all(result))

    def test_contains_invalid_characters_true(self):
        """
            test: username is None
        """
        username = None
        result = Validator.contains_invalid_characters(username)
        self.assertTrue(result)

    @patch("xmppchat.Validator.User")
    def test_validate_username_false(self, mock_u):
        """
            test: username does already exist in database.
        """
        from xmppchat.CustomValidatonError import CustomValidationError

        mock_u.query.filter_by.return_value.first.return_value = User("testuser", "testuser@web.de", "hallo123", "topic-id1")
        with pytest.raises(CustomValidationError):
            Validator.validate_username("testuser")       

    @patch("xmppchat.Validator.User")
    def test_validate_username_true(self, mock_u):
        """
            test: username does not already exist in database.
        """
        mock_u.query.filter_by.return_value.first.return_value = None
        self.assertIsNone(Validator.validate_username("testuserunkown"))

    @patch("xmppchat.Validator.User")
    def test_validate_email_false(self, mock_u):
        """
            test: email does already exist in database.
        """
        from xmppchat.CustomValidatonError import CustomValidationError

        mock_u.query.filter_by.return_value.first.return_value = User("testuser", "testuser@web.de", "hallo123", "topic-id1")
        with pytest.raises(CustomValidationError):
            Validator.validate_email("testuser@web.de")

    @patch("xmppchat.Validator.User")
    def test_validate_email_true(self, mock_u):
        """
            test: email does not already exist in database.
        """
        mock_u.query.filter_by.return_value.first.return_value = None
        self.assertIsNone(Validator.validate_email("testuserUnkown@web.de"))

if __name__ == "__main__":
    unittest.main()