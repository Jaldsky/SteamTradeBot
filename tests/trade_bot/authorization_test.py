from datetime import datetime
from os import path, remove
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from lib.database_manipulator import DataBaseManipulator, DatabaseManager
from trade_bot.authorization import AuthorizationManager

from settings import DB_PATH_TEST


class TestAuthorizationManager(TestCase):
    _db_manager_patcher = None
    _date_patcher = None

    current_date: datetime = datetime(2024, 1, 1, 10, 0, 0)

    @classmethod
    def setUpClass(cls) -> None:
        cls._db_manager_patcher = patch.object(
            DataBaseManipulator, 'db_manager', new=PropertyMock(return_value=DatabaseManager(DB_PATH_TEST))
        )
        cls._date_patcher = patch.object(
            AuthorizationManager, 'get_current_date', new=PropertyMock(return_value=cls.current_date)
        )
        cls._db_manager_patcher.start()
        cls._date_patcher.start()

    def setUp(self) -> None:
        # driver settings are taken from settings.py
        self.instance = AuthorizationManager()
        self.instance.table_name = 'test_auth_table'

    def tearDown(self) -> None:
        self.instance.db_manipulator.delete_table(self.instance.table_name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._db_manager_patcher.stop()
        cls._date_patcher.stop()
        if path.exists(DB_PATH_TEST):
            remove(DB_PATH_TEST)

    def test_create_auth_table(self):
        self.instance.create_auth_table()
        self.assertTrue(self.instance.db_manipulator.check_table_exist(self.instance.table_name))

    def test_get_valid_creds(self):
        table_name = self.instance.table_name
        current_date = self.current_date

        self.instance.create_auth_table()

        with self.subTest('With user-agent, with cookies'):
            user_agent = 'Mozilla/5.0'
            cookies = '[{"domain": ".steam.com"}]'
            data = {
                'user_agent': user_agent, 'cookies': cookies, 'update_date': current_date, 'create_date': current_date
            }
            self.instance.db_manipulator.create_table_data(table_name, data)
            self.assertTrue(self.instance.get_valid_creds)
            self.instance.db_manipulator.delete_table_data(table_name)

        with self.subTest('Without user-agent, with cookies'):
            cookies = '[{"domain": ".steam.com"}]'
            data = {
                'user_agent': '', 'cookies': cookies, 'update_date': current_date, 'create_date': current_date
            }
            self.instance.db_manipulator.create_table_data(table_name, data)
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manipulator.delete_table_data(table_name)

        with self.subTest('With user-agent, without cookies'):
            user_agent = 'Mozilla/5.0'
            data = {
                'user_agent': user_agent, 'cookies': '', 'update_date': current_date, 'create_date': current_date
            }
            self.instance.db_manipulator.create_table_data(table_name, data)
            self.assertIsNone(self.instance.get_valid_creds)
            self.instance.db_manipulator.delete_table_data(table_name)

        with self.subTest('With user-agent, without cookies - empty list'):
            user_agent = 'Mozilla/5.0'
            data = {
                'user_agent': user_agent, 'cookies': '[]', 'update_date': current_date, 'create_date': current_date
            }
            self.instance.db_manipulator.create_table_data(table_name, data)
            self.assertIsNone(self.instance.get_valid_creds)

    def test_create_or_update_cred(self):
        table_name: str = self.instance.table_name
        current_date: datetime = self.current_date

        with self.subTest('Create data'):
            user_agent = 'Mozilla/5.0'
            cookies = '[{"domain": ".steam.com"}]'
            search_condition: dict[str, str] = {'user_agent': user_agent}

            self.instance.create_auth_table()
            self.instance.create_or_update_cred(user_agent, cookies)
            self.assertEqual(
                [(1, '2024-01-01 10:00:00', '2024-01-01 10:00:00', 'Mozilla/5.0', '[{"domain": ".steam.com"}]')],
                self.instance.db_manipulator.get_table_data(table_name, search_condition)
            )
            self.instance.db_manipulator.delete_table_data(table_name)

        with self.subTest('Update data'):
            user_agent = 'Mozilla/5.0'
            cookies = '[{"domain": ".steam.com"}]'
            search_condition: dict[str, str] = {'user_agent': user_agent}
            data = {
                'user_agent': user_agent, 'cookies': cookies, 'update_date': current_date, 'create_date': current_date
            }
            cookies_updated = '[{"update_domain": ".steam.com"}]'

            self.instance.create_auth_table()
            self.instance.db_manipulator.create_table_data(table_name, data)
            self.instance.create_or_update_cred(user_agent, cookies_updated)
            self.assertEqual(
                [(1, '2024-01-01 10:00:00', '2024-01-01 10:00:00', 'Mozilla/5.0', '[{"update_domain": ".steam.com"}]')],
                self.instance.db_manipulator.get_table_data(table_name, search_condition)
            )
            self.instance.db_manipulator.delete_table_data(table_name)
