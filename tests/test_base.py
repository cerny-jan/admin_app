import unittest
from flask import current_app
from admin_app import create_app, db
from admin_app.models import User


class ModelsTestCase(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        user = User(username='Tester', email='test@test.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

    @classmethod
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.post('/', data=dict(
            email='test@test.com',
            password='pass'
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/portal' in response.headers['location'])

    # TODO test the rest of the view
