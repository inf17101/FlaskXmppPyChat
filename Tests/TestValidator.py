import unittest, sys
sys.path.insert(0, "/home/xmppweb/XmppChat/xmppchat/")


import re
class Validator:
    @staticmethod
    def contains_invalid_characters(string, search=re.compile(r"^[a-zA-Z][a-zA-Z0-9]+$").search):
        return not bool(search(string))

class TestValidator(unittest.TestCase):

    def setUp(self):
        self.valid_strings = ["testuser3","hallo123", "user2ultimate", "user234user123"]
        self.invalid_strings = ["123user", "asldjf-(asdf", "\\asdf\\asdf.", ".asfsasf"]

    def test_contains_invalid_characters_false(self):
        result = [Validator.contains_invalid_characters(name) for name in self.valid_strings]
        self.assertFalse(all(result))

    def test_contains_invalid_characters_true(self):
        result = [Validator.contains_invalid_characters(name) for name in self.invalid_strings]
        self.assertTrue(all(result))

if __name__ == "__main__":
    unittest.main()