from typing import Dict, Optional

import hummingbot.connector.exchange.coinsbit.coinsbit_constants as CONSTANTS
from hummingbot.core.data_type.common import TradeType
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import OrderBookMessage, OrderBookMessageType


class CoinsbitOrderBook(OrderBook):

    @classmethod
    def trade_message_from_exchange(cls, msg: Dict[str, any], metadata: Optional[Dict] = None):
        """
        Creates a trade message with the information from the trade event sent by the exchange
        :param msg: the trade event details sent by the exchange
        :param metadata: a dictionary with extra information to add to trade message
        :return: a trade message with the details of the trade as provided by the exchange
        """
        if metadata:
            msg.update(metadata)
        ts = msg["result"][5]
        price = msg["result"][2]
        side = msg['result'][3]
        amount = msg["result"][8]
        trade_type = float(TradeType.SELL.value) if side == CONSTANTS.SIDE_SELL else float(TradeType.BUY.value)
        return OrderBookMessage(OrderBookMessageType.TRADE, {
            "trading_pair": msg["trading_pair"],
            "trade_type": trade_type,
            "trade_id": msg["t"],
            "update_id": ts,
            "price": price,
            "amount": amount
        }, timestamp=ts * 1e-3)
