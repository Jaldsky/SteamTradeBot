from datetime import datetime
from enum import Enum

from settings import DATE_FORMAT


class CategoryTrade(Enum):
    DOTA = 570
    CS = 730

    def __str__(self):
        return str(self.value)


def get_current_date() -> str:
    return datetime.now().strftime(DATE_FORMAT)
