from unittest import TestCase
from unittest.mock import patch

from lib.authorization import AuthorizationManager


class TestAuthorizationManager(TestCase):

    @patch('lib.authorization.DEBUG', True)
    def setUp(self) -> None:
        # driver settings are taken from settings.py
        self.instance = AuthorizationManager()
        self.instance.table_name = 'test_auth'

    def test_create_auth_table(self):
        self.instance.create_auth_table()
        self.assertTrue(self.instance.db_manager.check_table_exist(self.instance.table_name))

    def test_check_records(self):
        self.instance.create_auth_table()
        self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Empty table'):
            self.assertFalse(self.instance.check_records)

        with self.subTest('Table with records'):
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
            cookies = '''[{'domain': 'store.steampowered.com', 'expiry': 1736249629, 'httpOnly': False}]'''
            self.instance.insert_cred(user_agent, cookies)
            self.assertTrue(self.instance.check_records)

        self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_get_valid_creds(self):
        self.instance.create_auth_table()
        self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Valid creds'):
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
            cookies = '''[{'domain': 'store.steampowered.com', 'expiry': 1736249629, 'httpOnly': False}]'''
            self.instance.insert_cred(user_agent, cookies)
            self.assertTrue(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without user_agent'):
            user_agent = ''
            cookies = '''[{'domain': 'store.steampowered.com', 'expiry': 1736249629, 'httpOnly': False}]'''
            self.instance.insert_cred(user_agent, cookies)
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without cookies'):
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
            cookies = ''
            self.instance.insert_cred(user_agent, cookies)
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without cookies, empty list'):
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
            cookies = '[]'
            self.instance.insert_cred(user_agent, cookies)

            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_(self):
        self.instance.exec()
