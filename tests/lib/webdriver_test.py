from unittest import TestCase
from unittest.mock import patch, Mock

from lib.webdriver import Driver


settings = (
    '--headless',
    '--window-size=1200x600',
)


@patch('settings.webdriver_settings', new=Mock(return_value=settings))
class TestWebDriver(TestCase):

    def test_webdriver(self) -> None:
        instance = Driver()
        instance.get("https://www.google.ru/")
        self.assertEqual('Google', instance.title)
