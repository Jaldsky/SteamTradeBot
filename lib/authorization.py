import json
from abc import ABC, abstractmethod
from os import getcwd, path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from selenium.common import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from settings import STEAM_LOGIN, STEAM_PASSWORD, DEBUG, DATE_FORMAT
from lib.database_manager import DatabaseManager
from lib.web_elements import LOGIN_FIELD, PASSWORD_FIELD, AUTH_BUTTON, GLOBAL_LOGIN_BUTTON
from lib.webdriver import Driver, get_user_agent, add_cookies

DRIVER_TIMEOUT = 10


@dataclass
class AuthorizationBase(ABC):
    driver: Optional[Union[Driver, WebDriver]] = None

    @abstractmethod
    def exec(self):
        if self.driver is None:
            raise Exception('Driver is missing')


@dataclass
class Authorization(AuthorizationBase):
    driver_timeout: int = DRIVER_TIMEOUT

    @staticmethod
    def find_element(waiter: WebDriverWait, locator: tuple[str, str]) -> WebElement:
        return waiter.until(presence_of_element_located(locator))

    def find_field_send_text(self, waiter: WebDriverWait, locator: tuple[str, str], text: str) -> None:
        field = self.find_element(waiter, locator)
        field.send_keys(text)

    def exec(self, cookies: Optional[list[dict]] = None) -> Union[Driver, WebDriver]:
        super().exec()
        self.driver.get('https://store.steampowered.com/login/')
        waiter = WebDriverWait(self.driver, self.driver_timeout)

        if cookies:
            self.driver.delete_all_cookies()
            add_cookies(self.driver, cookies)

            global_login_button = self.find_element(waiter, (By.XPATH, GLOBAL_LOGIN_BUTTON))
            global_login_button.click()

            try:
                self.find_element(waiter, (By.XPATH, AUTH_BUTTON))
            except TimeoutException:
                return self.driver

        try:
            self.find_field_send_text(waiter, (By.XPATH, LOGIN_FIELD), STEAM_LOGIN)
            self.find_field_send_text(waiter, (By.XPATH, PASSWORD_FIELD), STEAM_PASSWORD)

            auth_button = self.find_element(waiter, (By.XPATH, AUTH_BUTTON))
            auth_button.click()
        except TypeError:
            raise TypeError('Enter steam login and password')

        print('Take breakpoint and confirm session')

        return self.driver


@dataclass
class AuthorizationManagerBase(ABC):
    table_name: str = 'auth'
    table_limit: int = 50

    @abstractmethod
    def exec(self):
        pass


@dataclass
class AuthorizationManager(AuthorizationManagerBase):

    def __post_init__(self) -> None:
        db_name = 'SteamTrade.db'
        if DEBUG:
            db_name = path.join(getcwd(), 'tests', 'TestDB.db')

        self.db_manager = DatabaseManager(db_name)
        if self.db_manager is None:
            raise Exception('DB Manager is missing')

    @property
    def get_current_date(self):
        return datetime.now().strftime(DATE_FORMAT)

    def create_auth_table(self) -> None:
        if not self.db_manager.check_table_exist(self.table_name):
            db_fields = ['create_date DATE', 'update_date DATE', 'user_agent TEXT', 'cookies TEXT']
            self.db_manager.create_table(self.table_name, db_fields)

    @property
    def get_data_from_table(self) -> list[tuple]:
        return self.db_manager.get_table_data(self.table_name, self.table_limit)

    @property
    def get_valid_creds(self, ) -> Optional[list[tuple]]:
        records: list[tuple] = self.get_data_from_table
        valid_creds = [i for i in records if i[3] and i[4] not in '[]']
        if valid_creds:
            return valid_creds

    def check_user_agent_at_table(self, user_agent: str) -> bool:
        records: list[tuple] = self.get_data_from_table
        return bool(any(i for i in records if i[3] == user_agent)) if records else False

    def update_cred(self, user_agent: str, cookies: Optional[str]) -> None:
        if not user_agent:
            return

        set_data = [f'update_date = \'{self.get_current_date}\'']
        if cookies:
            set_data.append(f'cookies = \'{cookies}\'')

        set_data = ','.join(set_data)
        search_condition = f'user_agent = \'{user_agent}\''
        self.db_manager.update_record_at_table(self.table_name, set_data, search_condition)

    def insert_cred(self, user_agent: str, cookies: str) -> None:
        if user_agent and cookies:
            current_date = self.get_current_date
            data = {
                'create_date': current_date,
                'update_date': current_date,
                'user_agent': user_agent,
                'cookies': cookies
            }
            self.db_manager.insert_table_data(self.table_name, data)

    def create_or_update_cred(self, user_agent: Optional[str] = None, cookies: Optional[str] = None) -> None:
        if user_agent is None or cookies is None:
            return
        if self.check_user_agent_at_table(user_agent):
            self.update_cred(user_agent, cookies)
        else:
            self.insert_cred(user_agent, cookies)

    def exec(self, ) -> Union[Driver, WebDriver]:
        self.create_auth_table()

        #  in the future you can add multithreading here
        if valid_creds := self.get_valid_creds:
            first_record = valid_creds[0]
            table_user_agent: tuple[str] = (f'user-agent={first_record[2]}',)  # first_record[2] - user_agent column
            driver = Driver(custom_settings=table_user_agent).get_driver
            if table_cookies := first_record[3]:  # first_record[3] - cookie column
                cookies = json.loads(table_cookies)
                driver = Authorization(driver=driver).exec(cookies=cookies)
        else:
            driver = Driver().get_driver
            driver = Authorization(driver=driver).exec()

        user_agent = get_user_agent(driver)
        cookies = json.dumps(driver.get_cookies())
        self.create_or_update_cred(user_agent, cookies)
        return driver
