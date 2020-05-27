
import unittest, sys
from unittest.mock import patch
sys.path.insert(0, "/home/xmppweb/XmppChat/xmppchat/")

from UserManagement import UserManagement

class UserRegistrationTests(unittest.TestCase):

    def setUp(self):
        self.user_reg_obj = UserManagement("30.30.30.30", "xmppweb", priv_key="/home/xmppweb/.ssh/id_ejabberd-server", sudo_passwd="hallo123")

    @patch("UserManagement.subprocess.Popen")
    def test_register_remotely(self, mocked_popen):
        """
            test if user can be created via subprocess
        """
        mocked_popen.return_value.communicate.return_value = ('output', 'error')
        mocked_popen.return_value.returncode = 0
        return_code = self.user_reg_obj.create_user_remotely("testuser2", "hallo123", "ejabberd-server")
        self.assertEqual(return_code, 0)


    @patch("UserManagement.subprocess.Popen")
    def test_register_remotely_unsuccessfull(self, mocked_popen):
        """
            test if return_code != 0 if command is not successfully executed on remote machine
        """
        mocked_popen.return_value.communicate.return_value = ('output', 'error')
        mocked_popen.return_value.returncode = 1
        return_code = self.user_reg_obj.create_user_remotely("testuser2", "hallo123", "ejabberd-server")
        self.assertEqual(return_code, 1)

    @patch("UserManagement.subprocess.Popen")
    def test_delete_user_remotely(self, mocked_popen):
        """
            test if return_code != 0 if command is not successfully executed on remote machine
        """
        mocked_popen.return_value.communicate.return_value = ('output', 'error')
        mocked_popen.return_value.returncode = 0
        return_code = self.user_reg_obj.delete_user_remotely("testuser2", "ejabberd-server")
        self.assertEqual(return_code, 0)

    @patch("UserManagement.subprocess.Popen")
    def test_delete_user_remotely_unsuccessfull(self, mocked_popen):
        """
            test if return_code != 0 if command is not successfully executed on remote machine
        """
        mocked_popen.return_value.communicate.return_value = ('output', 'error')
        mocked_popen.return_value.returncode = 1
        return_code = self.user_reg_obj.delete_user_remotely("testuser2", "ejabberd-server")
        self.assertEqual(return_code, 1)

if __name__ == "__main__":
    unittest.main()