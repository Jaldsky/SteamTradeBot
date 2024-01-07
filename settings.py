from typing import Optional
from os import environ

DEBUG = False
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

webdriver_settings = (
    # '--headless',
    '--window-size=1200x600',
)

STEAM_LOGIN: Optional[str] = environ.get('login', None)
STEAM_PASSWORD: Optional[str] = environ.get('password', None)
