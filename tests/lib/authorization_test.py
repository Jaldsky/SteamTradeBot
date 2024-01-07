from unittest import TestCase
from unittest.mock import patch
from datetime import datetime
from os import getcwd, path

from lib.webdriver import Driver
from lib.authorization import Authorization, AuthorizationManager

settings = (
    '--headless',
    '--window-size=1200x600',
)


# class TestAuthorization(TestCase):
#
#     @patch('lib.webdriver.webdriver_settings', settings)
#     @patch('lib.authorization.DEBUG', True)
#     def setUp(self) -> None:
#         driver = Driver()
#         self.instance = Authorization(driver=driver)
#
#     def test_create_auth_table(self):
#         self.instance.create_auth_table()
#         self.assertTrue(self.instance.db_manager.check_table_exist(self.instance.table_name))
#
#     def test_insert_user_agent_to_table(self):
#         self.instance.create_auth_table()
#         user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.6099.131'
#         self.instance.insert_user_agent_to_table(user_agent)
#
#         self.instance.g
#
#
#     def test_authorization(self) -> None:
#         pass
#         #  don't forget to add to environment variables steam login and password
#         # self.instance.exec()


class TestAuthorizationManager(TestCase):

    @patch('lib.webdriver.webdriver_settings', settings)
    @patch('lib.authorization.DEBUG', True)
    def setUp(self) -> None:
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

