import unittest, sys
from unittest.mock import patch
import json
sys.path.append("/home/xmppweb/XmppChat/xmppchat/")
sys.path.append("/home/xmppweb/XmppChat/")
from xmppchat.api import app
from xmppchat.models import User



class TestFlaskRegisterCase(unittest.TestCase):

    def setUp(self):
        """
        Method to set up things for testing
        creates flask test client and important settings e.g. no csrf
        """
        app.config['WTF_CSRF_ENABLED'] = False
        self.tester = app.test_client(self)

    def test_register_page_get(self):
        """
        test correct get request on register page
        """
        response = self.tester.get('/register', content_type="html/text")
        self.assertEqual(response.status_code, 200)



if __name__ == "__main__":
    unittest.main()