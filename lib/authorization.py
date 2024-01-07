import json
from abc import ABC, abstractmethod
from os import getcwd, path
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from typing import Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from settings import STEAM_LOGIN, STEAM_PASSWORD, DEBUG, DATE_FORMAT
from lib.database_manager import DatabaseManager
from lib.web_elements import LOGIN_PATH, PASSWORD_PATH, AUTH_BUTTON, AUTH_CODE
from lib.webdriver import Driver, get_user_agent, add_cookies

DRIVER_TIMEOUT = 300


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

    def exec(self) -> None:
        super().exec()
        self.driver.get('https://store.steampowered.com/login/')

        waiter = WebDriverWait(self.driver, self.driver_timeout)
        try:
            self.find_field_send_text(waiter, (By.XPATH, LOGIN_PATH), STEAM_LOGIN)
            self.find_field_send_text(waiter, (By.XPATH, PASSWORD_PATH), STEAM_PASSWORD)

            auth_button = self.find_element(waiter, (By.XPATH, AUTH_BUTTON))
            auth_button.click()
        except TypeError:
            raise TypeError('Enter steam login and password')

        auth_code_panel = self.find_element(waiter, (By.XPATH, AUTH_CODE))
        if auth_code_panel:
            print('Confirm session')
            sleep(300)

        if auth_code_panel:
            raise Exception('You must enter a confirmation code')


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
        db_name = ''
        if DEBUG:
            db_name = path.join(getcwd(), 'tests', 'TestDB.db')

        self.db_manager = DatabaseManager(db_name)
        if self.db_manager is None:
            raise Exception('DB Manager is missing')

    def create_auth_table(self) -> None:
        if not self.db_manager.check_table_exist(self.table_name):
            db_fields = ['date DATE', 'user_agent TEXT', 'cookies TEXT', 'authorized BOOLEAN']
            self.db_manager.create_table(self.table_name, db_fields)

    def update_session_auth_table(self, driver: Union[Driver, WebDriver]) -> None:
        cookies: str = json.dumps(driver.get_cookies())
        user_agent: str = get_user_agent(driver)
        self.db_manager.update_record_at_table(
            self.table_name, f'authorized = 1, cookies = \'{cookies}\'', f'user_agent = \'{user_agent}\'')

    @property
    def get_user_agent_from_table(self) -> list[tuple]:
        return self.db_manager.get_table_data(self.table_name, self.table_limit)

    def check_user_agent_record_at_table(self, user_agent: str):
        records: list[tuple] = self.get_user_agent_from_table
        return bool(i for i in records if i[2] == user_agent) if bool(records) else False

    def insert_user_agent_to_table(self, user_agent: str, authorized: bool = False) -> None:
        if not self.check_user_agent_record_at_table(user_agent):
            current_date = datetime.now().strftime(DATE_FORMAT)
            data = {'date': current_date, 'user_agent': user_agent, 'authorized': authorized}
            self.db_manager.insert_table_data(self.table_name, data)

    def exec(self) -> Union[Driver, WebDriver]:
        self.create_auth_table()

        #  in the future you can add multithreading here
        if self.check_user_agent_record_at_table(self.table_name):
            first_record = self.get_user_agent_from_table[0]
            table_user_agent: tuple[str] = (f'user-agent={first_record[2]}',)  # first_record[2] - user_agent column
            driver = Driver(custom_settings=table_user_agent).get_driver
            if table_cookies := first_record[3]:  # first_record[3] - cookie column
                driver.get('https://store.steampowered.com/login/')
                # driver.delete_all_cookies()
                add_cookies(driver, json.loads(table_cookies))
        else:
            driver = Driver().get_driver
            current_user_agent = get_user_agent(driver)
            self.insert_user_agent_to_table(current_user_agent)

            Authorization(driver=driver).exec()
            self.update_session_auth_table(driver)

        return driver
