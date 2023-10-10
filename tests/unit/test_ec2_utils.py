import os
import unittest

from nixops.util import fetch_aws_secret_key


class TestEc2Utils(unittest.TestCase):
    def test_session_token(self):
        session_token = "DUMMY_SESSION_TOKEN"
        security_token = "DUMMY_SECURITY_TOKEN"
        self.assertIsNone(fetch_aws_secret_key("DUMMY_ACCESS_KEY")[2])

        os.environ["AWS_SECURITY_TOKEN"] = security_token
        self.assertIsEqual(fetch_aws_secret_key("DUMMY_ACCESS_KEY")[2], security_token)

        # SESSION_TOKEN should take priority if it's set
        os.environ["AWS_SESSION_TOKEN"] = session_token
        self.assertIsEqual(fetch_aws_secret_key("DUMMY_ACCES_KEY")[2], session_token)
