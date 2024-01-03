from settings import webdriver_settings

from abc import ABC, abstractmethod
from typing import Optional
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
    settings: Options = Options()

    def __post_init__(self):
        _ = [self.settings.add_argument(i) for i in webdriver_settings]

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
    settings: DriverSettings = DriverSettings()
    driver_type: str = 'chrome'
    driver: Optional[WebDriver] = None

    def __post_init__(self) -> None:
        if self.driver_type.lower() == 'chrome':
            self.driver = Chrome(options=DriverSettings().get_settings)
            return None
        raise Exception('Driver not found')

    def __new__(cls) -> WebDriver:
        cls.__post_init__(cls)
        return cls.driver
