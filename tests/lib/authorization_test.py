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

    def test_get_valid_creds(self):
        self.instance.create_auth_table()

        with self.subTest('With user-agent, with cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.assertTrue(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without user-agent, with cookies'):
            self.instance.insert_cred('', '[{"domain": ".steam.com"}]')
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, without cookies'):
            self.instance.insert_cred('Mozilla/5.0', '')
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, without cookies - empty list'):
            self.instance.insert_cred('Mozilla/5.0', '[]')
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_insert_cred(self):
        self.instance.create_auth_table()

        with self.subTest('Without user-agent, without cookies'):
            self.instance.insert_cred('', '')
            self.assertEqual(0, len(self.instance.get_data_from_table))
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, with cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.assertEqual(5, len(self.instance.get_data_from_table[0]))
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, without cookies'):
            self.instance.insert_cred('Mozilla/5.0', '')
            self.assertEqual(0, len(self.instance.get_data_from_table))
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without user-agent, with cookies'):
            self.instance.insert_cred('', '[{"domain": ".steam.com"}]')
            self.assertEqual(0, len(self.instance.get_data_from_table))
            self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_update_cred(self):
        self.instance.create_auth_table()
        self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without user-agent, without cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.assertIsNone(self.instance.update_cred('', ''))
            self.assertEqual(('Mozilla/5.0', '[{"domain": ".steam.com"}]'), self.instance.get_data_from_table[0][3:])
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('Without user-agent, with cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.instance.update_cred('', '[{"test": ".steam.com"}]')
            self.assertEqual(('Mozilla/5.0', '[{"domain": ".steam.com"}]'), self.instance.get_data_from_table[0][3:])
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, with cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.instance.update_cred('Mozilla/5.0', '[{"test": ".steam.com"}]')
            self.assertEqual(('Mozilla/5.0', '[{"test": ".steam.com"}]'), self.instance.get_data_from_table[0][3:])
            self.instance.db_manager.clear_table_data(self.instance.table_name)

        with self.subTest('With user-agent, without cookies'):
            self.instance.insert_cred('Mozilla/5.0', '[{"domain": ".steam.com"}]')
            self.instance.update_cred('Mozilla/5.0', '')
            self.assertEqual(('Mozilla/5.0', '[{"domain": ".steam.com"}]'), self.instance.get_data_from_table[0][3:])
            self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_check_user_agent_at_table(self):
        self.instance.create_auth_table()

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
