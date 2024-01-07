from abc import ABC
from typing import Union, Optional
from dataclasses import dataclass

from selenium.webdriver.remote.webdriver import WebDriver

from settings import DEBUG
from lib.authorization import AuthorizationManager
from lib.webdriver import Driver


@dataclass
class TradeBotBase(ABC):
    pass


@dataclass
class TradeBot(TradeBotBase):

    # def __post_init__(self) -> None:
    #     db_name = ''
    #     if DEBUG:
    #         db_name = path.join(getcwd(), 'tests', 'TestDB.db')
    #
    #     self.db_manager = DatabaseManager(db_name)
    #     if self.db_manager is None:
    #         raise Exception('DB Manager is missing')

    def exec(self):
        driver: Union[Driver, WebDriver] = AuthorizationManager().exec()
        print(driver.current_url)
        x = driver.get('https://steamcommunity.com/market/')
        print(x)


