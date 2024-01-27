import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union

from selenium.common import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from settings import STEAM_LOGIN, STEAM_PASSWORD, STEAM_MAIN

from trade_bot.util import get_current_date
from lib.database_manipulator import DataBaseManipulator
from trade_bot.web_elements import LOGIN_FIELD, PASSWORD_FIELD, AUTH_BUTTON, GLOBAL_LOGIN_BUTTON
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
        self.driver.get(f'{STEAM_MAIN}/login/home')
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
        self.db_manipulator = DataBaseManipulator()

    def create_auth_table(self) -> None:
        db_fields = {'create_date': 'DATE', 'update_date': 'DATE', 'user_agent': 'TEXT', 'cookies': 'TEXT'}
        self.db_manipulator.create_table(self.table_name, db_fields)

    @property
    def get_data_from_table(self) -> list[tuple]:
        return self.db_manipulator.get_table_data(self.table_name, limit=self.table_limit)

    @property
    def get_valid_creds(self, ) -> Optional[list[tuple]]:
        records: list[tuple] = self.get_data_from_table
        valid_creds = [i for i in records if i[3] and i[4] not in '[]']
        if valid_creds:
            return valid_creds

    def create_or_update_cred(self, user_agent: str, cookies: Optional[str]) -> None:
        current_date = str(get_current_date())
        search_condition = {'user_agent': user_agent}
        data = {'user_agent': user_agent, 'cookies': cookies, 'update_date': current_date}
        additional_column = {'create_date': current_date}

        self.db_manipulator.create_or_update_table_data(self.table_name, data, search_condition, additional_column)

    def exec(self, ) -> Union[Driver, WebDriver]:
        self.create_auth_table()

        #  in the future you can add multithreading here
        if valid_creds := self.get_valid_creds:
            first_record = valid_creds[0]
            table_user_agent: tuple[str] = (f'user-agent={first_record[3]}',)  # first_record[3] - user_agent column
            driver = Driver(custom_settings=table_user_agent).get_driver
            if table_cookies := first_record[4]:  # first_record[4] - cookie column
                cookies = json.loads(table_cookies)
                driver = Authorization(driver=driver).exec(cookies=cookies)
        else:
            driver = Driver().get_driver
            driver = Authorization(driver=driver).exec()

        user_agent = get_user_agent(driver)
        cookies = json.dumps(driver.get_cookies())
        self.create_or_update_cred(user_agent, cookies)
        return driver
