import unittest, sys
from unittest.mock import patch
import json
sys.path.append("/home/xmppweb/XmppChat/xmppchat/")
sys.path.append("/home/xmppweb/XmppChat/")
from xmppchat.api import app
from xmppchat.models import User

class TestFlaskApplication(unittest.TestCase):

    def setUp(self):
        """
        Method to set up things for testing
        creates flask test client and important settings e.g. no csrf
        """
        app.config['WTF_CSRF_ENABLED'] = False
        self.tester = app.test_client(self)

    def test_login(self):
        """
        test correct get request on login page
        """
        response = self.tester.get('/login', content_type="html/text")
        self.assertEqual(response.status_code, 200)

    def test_gochat_without_login(self):
        """
        test if gochat' s route redirects to login if user is not logged in
        """
        response = self.tester.get('/gochat', content_type="html/text")
        self.assertEqual(response.status_code, 302) # redirect to /login (code: 302)
        self.assertIn(b"Redirecting", response.data)

    @patch("xmppchat.api.User")
    def test_login_post_with_valid_credentials(self, mock_u):
        """
            test successfull login and responses
        """
        mock_u.query.filter_by.return_value.first.return_value = User("testuser", "testuser@web.de", "hallo123")
        with app.test_request_context("/login"):
            response = self.tester.post('/login', data=json.dumps(dict(username="testuser", password="hallo123", remember=False)), content_type="application/json")
            resp_data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            if "feedback" in resp_data:
                self.assertEqual(resp_data["feedback"], "login successfull.")


    @patch("xmppchat.api.User")
    def test_login_post_without_valid_credentials(self, mock_u):
        """
        test api return value if login credentials are not valid
        """
        mock_u.query.filter_by.return_value.first.return_value = None
        with app.test_request_context("/login"):
            response = self.tester.post('/login', data=json.dumps(dict(username="testuser", password="hallo123", remember=False)), content_type="application/json")
            resp_data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            if "feedback" in resp_data:
                self.assertEqual(resp_data["feedback"], "invalid login credentials.")

    @patch("xmppchat.api.User")
    def test_login_post_with_key_error(self, mock_u):
        """
        tests api return value if json keys are manipulated wrong
        """
        mock_u.query.filter_by.return_value.first.return_value = None
        with app.test_request_context("/login"):
            response = self.tester.post('/login', data=json.dumps(dict(wrongkey1="testuser", wrongkey2="hallo123", wrongkey3=False)), content_type="application/json")
            resp_data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            if "feedback" in resp_data:
                self.assertEqual(resp_data["feedback"], "invalid login credentials.")

if __name__ == "__main__":
    unittest.main()