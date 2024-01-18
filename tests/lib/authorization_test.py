from unittest import TestCase
from unittest.mock import patch, PropertyMock

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

    def test_check_user_agent_at_table(self):
        self.instance.create_auth_table()
        self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Empty table'):
            data = []
            with patch.object(AuthorizationManager, 'get_data_from_table', new=PropertyMock(return_value=data)):
                self.assertFalse(self.instance.check_user_agent_at_table('Mozilla/5.0'))

        with self.subTest('Table with one row'):
            data = [
                (1, '2024-01-01 10:40:00', '2024-01-01 10:40:00', 'Mozilla/5.0', '[{"domain": ".steam.com"}]')
            ]
            with patch.object(AuthorizationManager, 'get_data_from_table', new=PropertyMock(return_value=data)):
                self.assertTrue(self.instance.check_user_agent_at_table('Mozilla/5.0'))

        with self.subTest('Table with one row, user-agent not found'):
            data = [
                (1, '2024-01-01 10:40:00', '2024-01-01 10:40:00', 'Mozilla/5.0', '[{"domain": ".steam.com"}]')
            ]
            with patch.object(AuthorizationManager, 'get_data_from_table', new=PropertyMock(return_value=data)):
                self.assertFalse(self.instance.check_user_agent_at_table('Chrome'))

        with self.subTest('Table with one and more rows'):
            data = [
                (1, '2024-01-01 10:40:00', '2024-01-01 16:40:00', 'Mozilla/4.0', '[{"domain": ".steam.com"}]'),
                (2, '2024-01-01 10:45:00', '2024-01-01 16:45:00', 'Mozilla/5.0', '[{"domain": ".steam.com"}]'),
                (3, '2024-01-01 10:50:00', '2024-01-01 16:50:00', 'Mozilla/6.0', '[{"domain": ".steam.com"}]')
            ]
            with patch.object(AuthorizationManager, 'get_data_from_table', new=PropertyMock(return_value=data)):
                self.assertTrue(self.instance.check_user_agent_at_table('Mozilla/6.0'))

    def test_(self):
        self.instance.exec()
