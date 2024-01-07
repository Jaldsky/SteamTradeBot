from unittest import TestCase
from unittest.mock import patch

from lib.authorization import AuthorizationManager


class TestAuthorizationManager(TestCase):

    @patch('lib.authorization.DEBUG', True)
    def setUp(self) -> None:
        # driver settings are taken from settings.py
        self.instance = AuthorizationManager()

    def test_create_auth_table(self):
        self.instance.create_auth_table()
        self.assertTrue(self.instance.db_manager.check_table_exist(self.instance.table_name))

    def test_insert_user_agent_to_table(self):
        self.instance.create_auth_table()

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
        self.instance.insert_user_agent_to_table(user_agent)

        with self.subTest('Insert data'):
            self.assertTrue(self.instance.get_user_agent_from_table)

        with self.subTest('Data already at table'):
            self.assertFalse(self.instance.insert_user_agent_to_table(user_agent))

        self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_check_user_agent_record_at_table(self):
        self.instance.create_auth_table()
        self.instance.db_manager.clear_table_data(self.instance.table_name)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'

        with self.subTest('Without record'):
            self.assertFalse(self.instance.check_user_agent_record_at_table(user_agent))

        with self.subTest('With record'):
            self.instance.insert_user_agent_to_table(user_agent)
            self.assertTrue(self.instance.check_user_agent_record_at_table(user_agent))

        self.instance.db_manager.clear_table_data(self.instance.table_name)

    def test_(self):
        self.instance.exec()

