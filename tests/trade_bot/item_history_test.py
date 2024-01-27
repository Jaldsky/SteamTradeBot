from os import getcwd, path
from unittest import TestCase
from unittest.mock import patch, PropertyMock

from lib.database_manipulator import DataBaseManipulator, DatabaseManager
from settings import DB_PATH_TEST
from trade_bot.item_history import ItemHistory, CategoryTrade


def mock_html():
    html_test_path = path.join(getcwd(), 'tests', 'test_data', 'M4A1-S Boreal Forest Field-Tested.html')
    with open(html_test_path, 'r', encoding='cp1251') as html:
        html = html.read()
    return html


class TestItemHistory(TestCase):
    _patcher = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._patcher = patch.object(
            DataBaseManipulator, 'db_manager', new=PropertyMock(return_value=DatabaseManager(DB_PATH_TEST))
        )
        cls._patcher.start()

    def setUp(self) -> None:
        self.item_name = 'M4A1-S | Boreal Forest (Field-Tested)'
        self.instance = ItemHistory(CategoryTrade.CS, self.item_name)
        self.instance.items_table_name = 'test_items_table'

    def test_get_item_link(self):
        self.assertEqual(
            'https://steamcommunity.com/market/listings/730/M4A1-S%20%7C%20Boreal%20Forest%20%28Field-Tested%29',
            self.instance.get_item_link
        )

    def test_create_items_table(self):
        self.instance.create_items_table()
        self.assertTrue(self.instance.db_manipulator.check_table_exist(self.instance.items_table_name))

    def test_create_or_update_items_table_data(self):
        self.instance.create_items_table()
        self.instance.create_or_update_items_table_data(20333, CategoryTrade.CS, self.item_name)

    @patch.object(ItemHistory, 'get_html', new=PropertyMock(return_value=mock_html()))
    def test_exec(self):
        print(self.instance.exec())



















