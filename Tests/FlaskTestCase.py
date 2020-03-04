import unittest, sys
sys.path.append("/home/xmppweb/XmppChat/xmppchat/")
sys.path.append("/home/xmppweb/XmppChat/")
from xmppchat.api import app


class UserRegistrationTests(unittest.TestCase):

    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.tester = app.test_client(self)

    def test_login(self):
        response = self.tester.get('/login', content_type="html/text")
        self.assertEqual(response.status_code, 200)

    def test_gochat_without_login(self):
        response = self.tester.get('/gochat', content_type="html/text")
        self.assertEqual(response.status_code, 302) # redirect to /login (code: 302)
        self.assertIn(b"Redirecting", response.data)

"""
    def test_login_post(self):
        response = self.tester.post('/login', data=dict(username="testuser8", password="hallo123", remember=False))
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"CSRF", response.data)
"""         

if __name__ == "__main__":
    unittest.main()