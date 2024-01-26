from typing import Optional
from os import environ, path, getcwd

DEBUG = False
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

webdriver_settings = (
    # '--headless',
    '--window-size=1200x600',
)

DB_PATH = path.join(getcwd(), 'SteamTrade.db')
DB_PATH_TEST = path.join(getcwd(), 'tests', 'TestDB.db')

STEAM_MAIN: str = 'https://steamcommunity.com'
STEAM_LOGIN: Optional[str] = environ.get('login', None)
STEAM_PASSWORD: Optional[str] = environ.get('password', None)
