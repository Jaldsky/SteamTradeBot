from settings import webdriver_settings

from abc import ABC, abstractmethod
from typing import Optional, Union
from dataclasses import dataclass

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class DriverSettingsBase(ABC):
    settings: Options = Options()

    @property
    @abstractmethod
    def get_settings(self):
        pass


@dataclass
class DriverSettings(DriverSettingsBase):
    custom_settings: Optional[tuple] = None

    def __post_init__(self):
        settings = webdriver_settings
        if custom_settings := self.custom_settings:
            settings += custom_settings
        _ = [self.settings.add_argument(i) for i in settings]

    @property
    def get_settings(self):
        return self.settings


@dataclass
class DriverBase(ABC):
    settings: DriverSettings = DriverSettings()
    driver_type: str = 'chrome'
    driver: Optional[WebDriver] = None


@dataclass
class Driver(DriverBase):
    custom_settings: Optional[tuple] = None

    def __post_init__(self) -> None:
        if self.driver_type.lower() == 'chrome':
            self.driver = Chrome(
                options=DriverSettings(
                    custom_settings=self.custom_settings
                ).get_settings
            )
            return None
        raise Exception('Driver not found')

    @property
    def get_driver(self):
        return self.driver


def get_user_agent(driver: Optional[Union[Driver, WebDriver]]):
    return driver.execute_script("return navigator.userAgent;")
