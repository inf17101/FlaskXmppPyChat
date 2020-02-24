
import unittest, sys
from unittest.mock import patch
sys.path.insert(0, "/home/xmppweb/XmppChat/xmppchat/")

from UserRegistration import UserRegistration

class UserRegistrationTests(unittest.TestCase):

    def setUp(self):
        self.user_reg_obj = UserRegistration("10.10.8.5", "xmppweb", priv_key="/home/xmppweb/.ssh/id_ejabberd-server", sudo_passwd="hallo123")

    @patch("UserRegistration.subprocess.Popen")
    def test_register_remotely(self, mocked_popen):
        mocked_popen.return_value.communicate.return_value = ('output', 'error')
        mocked_popen.return_value.returncode = 0
        return_code = self.user_reg_obj.register_remotely("testuser2", "hallo123", "ejabberd-server")
        self.assertEqual(return_code, 0)

if __name__ == "__main__":
    unittest.main()