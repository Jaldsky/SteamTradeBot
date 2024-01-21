from unittest import TestCase
from os import getcwd, path

from lib.database_manager import DatabaseManager


class TestDatabaseManager(TestCase):

    def setUp(self) -> None:
        self.instance = DatabaseManager(path.join(getcwd(), 'tests', 'TestDB.db'))

    def test_create_table(self):
        self.instance.create_table('test_table', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        with self.subTest('Table exist'):
            self.assertTrue(self.instance.check_table_exist('test_table'))
        with self.subTest('Table not exist'):
            self.assertFalse(self.instance.check_table_exist('test_'))

    def test_insert_table_data(self):
        self.instance.create_table('test_table', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])

        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test_table', insert_data)
        with self.subTest('Data is already in the table'):
            self.assertTrue(self.instance.check_table_data_exist('test_table', insert_data))
        with self.subTest('No data in the table'):
            insert_data['firstname'] = 'Alex'
            self.assertFalse(self.instance.check_table_data_exist('test_table', insert_data))

        self.instance.clear_table_data('test_table')

    def test_get_table_data(self):
        self.instance.create_table('test_table', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test_table', insert_data)

        with self.subTest('Without search condition'):
            self.assertEqual([(1, 'Bob', 'Orange', 101)], self.instance.get_table_data('test_table'))

        with self.subTest('With search condition'):
            self.assertEqual([(1, 'Bob', 'Orange', 101)], self.instance.get_table_data('test_table', 'age=101'))

        self.instance.clear_table_data('test_table')

    def test_clear_table_data(self):
        self.instance.create_table('test_table', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test_table', insert_data)

        with self.subTest('Checking that the data has been added to the table'):
            self.assertTrue(self.instance.check_table_data_exist('test_table', insert_data))

        with self.subTest('Checking that data has been deleted from the table'):
            self.instance.clear_table_data('test_table')
            self.assertFalse(self.instance.get_table_data('test_table'))

        self.instance.clear_table_data('test_table')

    def test_update_record_at_table(self):
        self.instance.create_table('test_table', ['firstname TEXT', 'lastname TEXT', 'age INTEGER'])
        insert_data = {'firstname': 'Bob', 'lastname': 'Orange', 'age': 101}
        self.instance.insert_table_data('test_table', insert_data)

        self.instance.update_record_at_table('test_table', 'firstname = \'Max\'', 'lastname = \'Orange\'')

        self.assertIn('Max', self.instance.get_table_data('test_table')[0][1])
        self.instance.clear_table_data('test_table')
