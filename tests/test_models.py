import unittest
from flask import current_app
from admin_app import create_app
from admin_app.models import User


class ModelsTestCase(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    @classmethod
    def tearDown(self):
        self.app_context.pop()

    def test_password_set(self):
        user = User(username='Tester', email='test@test.com')
        user.set_password('pass')
        self.assertTrue(user.password_hash is not None)

    def test_password_check(self):
        user = User(username='Tester2', email='test2@test.com')
        user.set_password('pass')
        self.assertTrue(user.check_password('pass'))
        self.assertFalse(user.check_password('word'))
