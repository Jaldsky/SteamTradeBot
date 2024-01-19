from unittest import TestCase
from unittest.mock import patch

from trade_bot.trade_bot import TradeBot


@patch('lib.authorization.DEBUG', True)
class TestTradeBot(TestCase):

    def test_trade_bot(self) -> None:
        instance = TradeBot()
        instance.exec()

