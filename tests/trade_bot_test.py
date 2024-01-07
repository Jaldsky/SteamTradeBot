from unittest import TestCase
from unittest.mock import patch, Mock

from trade_bot import TradeBot


class TestTradeBot(TestCase):

    def test_trade_bot(self) -> None:
        instance = TradeBot()
        instance.exec()

