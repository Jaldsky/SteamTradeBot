from unittest import TestCase
from unittest.mock import patch, PropertyMock
from os import path, remove

from lib.database_manipulator import (
    DataBaseManipulator, DatabaseManager, TableNameException, DataCreateTableException, DataTableException,
    SearchConditionException,
)

from settings import DB_PATH_TEST


class TestDataBaseManipulator(TestCase):
    patcher = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.patcher = patch.object(
            DataBaseManipulator, 'db_manager', new=PropertyMock(return_value=DatabaseManager(DB_PATH_TEST))
        )
        cls.patcher.start()

    def setUp(self) -> None:
        self.instance = DataBaseManipulator()

    def tearDown(self) -> None:
        table_name = 'test_table'
        self.instance.delete_table(table_name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.patcher.stop()
        if path.exists(DB_PATH_TEST):
            remove(DB_PATH_TEST)

    def test_check_table_exist(self) -> None:
        table_name = 'test_table'
        data = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}

        self.instance.create_table(table_name, data)

        with self.subTest('Table exists'):
            self.assertTrue(self.instance.check_table_exist(table_name))

        with self.subTest('Table not exists'):
            self.assertFalse(self.instance.check_table_exist('test_'))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.check_table_exist(123)

    def test_create_table(self) -> None:
        table_name = 'test_table'
        data = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}

        with self.subTest('Create table'):
            self.instance.create_table(table_name, data)
            self.assertTrue(self.instance.check_table_exist(table_name))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.create_table(1.01, data)

        with self.subTest('Wrong field arg'):
            with self.assertRaises(DataCreateTableException):
                self.instance.create_table(table_name, '')

    def test_delete_table(self) -> None:
        table_name = 'test_table'
        data = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}

        with self.subTest('Table exists and is deleted'):
            self.instance.create_table(table_name, data)
            self.instance.delete_table(table_name)
            self.assertFalse(self.instance.check_table_exist(table_name))

        with self.subTest('Table not exists and is not deleted'):
            self.instance.delete_table('test_')
            self.assertFalse(self.instance.check_table_exist('test_'))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.delete_table(1.01)

    def test_check_table_data_exist(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}

        self.instance.create_table(table_name, data_create_table)
        self.instance.create_table_data(table_name, data)

        with self.subTest('Table data exists'):
            self.assertTrue(self.instance.check_table_data_exist(table_name, {'lastname': 'Orange'}))

        with self.subTest('Table data not exists'):
            self.assertFalse(self.instance.check_table_data_exist(table_name, {'age': 0}))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.check_table_data_exist(1, {'lastname': 'Orange'})

        with self.subTest('Wrong data arg'):
            with self.assertRaises(DataTableException):
                self.instance.check_table_data_exist(table_name, 1.01)

    def test_create_table_data(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}

        self.instance.create_table(table_name, data_create_table)

        with self.subTest('Create table data'):
            self.instance.create_table_data(table_name, data)
            self.assertTrue(self.instance.check_table_data_exist(table_name, data))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.create_table_data(1.01, data)

        with self.subTest('Wrong data arg'):
            with self.assertRaises(DataTableException):
                self.instance.create_table_data(table_name, None)

    def test_get_table_data(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 102}

        self.instance.create_table(table_name, data_create_table)
        self.instance.create_table_data(table_name, data)

        with self.subTest('Get table data'):
            self.assertEqual([(1, 'Bob', 'Orange', 102)], self.instance.get_table_data(table_name))

        with self.subTest('Get table data by search condition'):
            self.assertEqual([(1, 'Bob', 'Orange', 102)], self.instance.get_table_data(table_name, {'age': 102}))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.get_table_data(1.01)

    def test_update_table_data(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 104}
        update_data = {'firstname': 'Alex'}
        search_condition = {'lastname': 'Orange'}

        self.instance.create_table(table_name, data_create_table)
        self.instance.create_table_data(table_name, data)

        with self.subTest('Update table data'):
            self.instance.update_table_data(table_name, update_data, search_condition)
            self.assertEqual([(1, 'Alex', 'Orange', 104)], self.instance.get_table_data(table_name, {'age': 104}))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.update_table_data('', update_data, search_condition)

        with self.subTest('Wrong data arg'):
            with self.assertRaises(DataTableException):
                self.instance.update_table_data(table_name, None, search_condition)

        with self.subTest('Wrong search_condition arg'):
            with self.assertRaises(SearchConditionException):
                self.instance.update_table_data(table_name, update_data, '')

    def test_delete_table_data(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 104}

        self.instance.create_table(table_name, data_create_table)
        self.instance.create_table_data(table_name, data)

        with self.subTest('Delete table data'):
            self.assertTrue(self.instance.get_table_data(table_name))
            self.instance.delete_table_data(table_name)
            self.assertFalse(self.instance.get_table_data(table_name))

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.delete_table_data(None)

    def test_create_or_update_table_data(self) -> None:
        table_name = 'test_table'
        data_create_table = {'firstname': 'TEXT', 'lastname': 'TEXT', 'age': 'INTEGER'}
        data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 104}
        search_condition = {'lastname': 'Orange'}
        update_data = {'age': 105}

        self.instance.create_table(table_name, data_create_table)

        with self.subTest('Create data'):
            self.instance.create_or_update_table_data(table_name, data, search_condition)
            self.assertEqual([(1, 'Bob', 'Orange', 104)], self.instance.get_table_data(table_name, search_condition))
            self.instance.delete_table_data(table_name)

        with self.subTest('Update data'):
            self.instance.create_table_data(table_name, data)
            self.instance.create_or_update_table_data(table_name, update_data, search_condition)
            self.assertEqual([(1, 'Bob', 'Orange', 105)], self.instance.get_table_data(table_name, search_condition))
            self.instance.delete_table_data(table_name)

        with self.subTest('Data already at table'):
            self.instance.create_table_data(table_name, data)
            self.instance.create_or_update_table_data(table_name, data, search_condition)
            self.assertEqual([(1, 'Bob', 'Orange', 104)], self.instance.get_table_data(table_name, search_condition))
            self.instance.delete_table_data(table_name)

        with self.subTest('Wrong table_name arg'):
            with self.assertRaises(TableNameException):
                self.instance.create_or_update_table_data(None, data, search_condition)

        with self.subTest('Wrong data arg'):
            with self.assertRaises(DataTableException):
                self.instance.create_or_update_table_data(table_name, None, search_condition)

        with self.subTest('Wrong search_condition arg'):
            with self.assertRaises(SearchConditionException):
                self.instance.create_or_update_table_data(table_name, update_data, None)
