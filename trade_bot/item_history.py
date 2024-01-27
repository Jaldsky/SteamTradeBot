import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta

from pandas import DataFrame, to_datetime
from requests import get
from urllib.parse import quote

from lib.database_manipulator import DataBaseManipulator
from trade_bot.util import CategoryTrade, get_current_date
from settings import STEAM_MAIN


@dataclass
class ItemHistoryBase(ABC):
    category: CategoryTrade
    item_name: str

    @abstractmethod
    def exec(self):
        pass


@dataclass
class ItemHistory(ItemHistoryBase):
    items_table_name: str = 'items_table'
    global_history_table_name: str = 'global_history_table'
    local_history_table_name: str = 'local_history_table'

    def __post_init__(self) -> None:
        self.db_manipulator = DataBaseManipulator()
        self.item_name_id_regexp = 'Market_LoadOrderSpread\((.*)\);'
        self.prise_history_regexp = 'var line1=(.*);'

    @property
    def get_item_link(self) -> str:
        return f'{STEAM_MAIN}/market/listings/{self.category}/{quote(self.item_name)}'

    @property
    def get_html(self):
        return get(self.get_item_link).text

    def create_items_table(self) -> None:
        db_fields = {'create_date': 'DATE', 'category': 'TEXT', 'name': 'TEXT'}
        self.db_manipulator.create_table(self.items_table_name, db_fields)

    def create_or_update_items_table_data(self, item_name_id: int, category: CategoryTrade, name: str) -> None:
        data = {
            'id': item_name_id,
            'create_date': str(get_current_date()),
            'category': str(category.name),
            'name': name
        }
        search_condition = {'id': item_name_id}
        self.db_manipulator.create_or_update_table_data(self.items_table_name, data, search_condition)
        self.db_manipulator.create_table_data(self.items_table_name, data)

    def exec(self):
        html = self.get_html
        if item_name_id := re.findall(self.item_name_id_regexp, html):
            item_name_id = item_name_id[0]
            self.create_items_table()
            self.create_or_update_items_table_data(item_name_id, self.category, self.item_name)

        if prise_history := re.findall(self.prise_history_regexp, html):
            df = DataFrame(json.loads(prise_history[0]), columns=['date', 'price', 'volume'])
            df.date = to_datetime(df.date.str.replace(': +0', ''), format='%b %d %Y %H')
            df.volume = df.volume.astype(int)
            df['item_id'] = int(item_name_id)

            condition = df.date > to_datetime(df.date.max()) - timedelta(days=31)
            #  the most current date in the table subtract 31 days
            df_recent_month_hourly = df.loc[condition].copy()
            df = df.loc[~condition]

            self.db_manipulator.dataframe_to_table(df, self.global_history_table_name,
                                                   {'index': False, 'if_exists': 'replace'})

            self.db_manipulator.dataframe_to_table(df_recent_month_hourly, self.local_history_table_name,
                                                   {'index': False, 'if_exists': 'replace'})

            # inaccurate data for the last 31 days
            # df_recent_month = df_recent_month_hourly.groupby(df['date'].dt.date).mean()
            # # calculating daily averages
            # df_recent_month.volume = df_recent_month.volume.astype(int)
            # df_recent_month.date = df_recent_month.date.dt.floor('D') + timedelta(hours=1)
            # # to format %Y-%m-%d 01:00:00
            # concat([df, df_recent_month], ignore_index=True)

        # https://steamcommunity.com/market/itemordershistogram?language=english&currency=3&item_nameid=2384820
