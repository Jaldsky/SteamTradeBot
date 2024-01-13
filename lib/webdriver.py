from settings import webdriver_settings

from abc import ABC, abstractmethod
from typing import Optional, Union
from dataclasses import dataclass

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class DriverSettingsBase(ABC):
    """Base class for interacting with driver options."""
    settings: Options = Options()

    @property
    @abstractmethod
    def get_settings(self):
        pass


@dataclass
class DriverSettings(DriverSettingsBase):
    """Class for interacting with driver options."""
    custom_settings: Optional[tuple] = None

    def __post_init__(self) -> None:
        """Post initialization."""
        settings = webdriver_settings
        if custom_settings := self.custom_settings:
            settings += custom_settings
        _ = [self.settings.add_argument(i) for i in settings]

    @property
    def get_settings(self) -> Options:
        """Method for getting an instance of the browser settings class.

        Returns:
            An instance of the browser settings class with the settings applied.
        """
        return self.settings


@dataclass
class DriverBase(ABC):
    """Base class for getting an instance of the driver class."""
    settings: DriverSettings = DriverSettings()
    driver_type: str = 'chrome'
    driver: Optional[WebDriver] = None


@dataclass
class Driver(DriverBase):
    """Class for getting an instance of the driver class."""
    custom_settings: Optional[tuple] = None

    def __post_init__(self) -> None:
        """Post initialization."""
        if self.driver_type.lower() == 'chrome':
            self.driver = Chrome(
                options=DriverSettings(
                    custom_settings=self.custom_settings
                ).get_settings
            )
            return None
        raise Exception('Driver not found')

    @property
    def get_driver(self) -> Chrome:
        """Method for getting an instance of a Chrome class with settings applied.

        Returns:
            An instance of a Chrome class with settings applied.
        """
        return self.driver


def get_user_agent(driver: Union[Driver, WebDriver]) -> str:
    """Method for getting user-agent.

    Args:
        driver: driver instance.

    Returns:
        User-agent.
    """
    return driver.execute_script("return navigator.userAgent;")


def add_cookies(driver: Union[Driver, WebDriver], cookies: list[dict]) -> None:
    """Method for adding cookies.

    Args:
        driver: driver instance.
        cookies: list with cookies.
    """
    _ = [driver.add_cookie(i) for i in cookies]
