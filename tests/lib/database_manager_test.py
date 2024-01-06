from unittest import TestCase
from os import getcwd, path

from lib.database_manager import DatabaseManager


class TestDatabaseManager(TestCase):

    def setUp(self) -> None:
        self.instance = DatabaseManager(path.join(getcwd(), 'tests', 'TestDB.db'))

    def test_create_table(self):
        self.instance.create_table('test', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        with self.subTest('Table exist'):
            self.assertTrue(self.instance.check_table_exist('test'))
        with self.subTest('Table not exist'):
            self.assertFalse(self.instance.check_table_exist('test_'))

    def test_insert_table_data(self):
        self.instance.create_table('test', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])

        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test', insert_data)
        with self.subTest('Data is already in the table'):
            self.assertTrue(self.instance.check_table_data_exist('test', insert_data))
        with self.subTest('No data in the table'):
            insert_data['firstname'] = 'Alex'
            self.assertFalse(self.instance.check_table_data_exist('test', insert_data))

    def test_get_table_data(self):
        self.instance.create_table('test', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test', insert_data)

        self.assertEqual([(1, 'Bob', 'Orange', 101)], self.instance.get_table_data('test'))
