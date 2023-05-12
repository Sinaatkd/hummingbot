# import asyncio
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from bidict import bidict

from hummingbot.connector.constants import s_decimal_NaN
from hummingbot.connector.exchange.coinsbit import (  # coinsbit_utils,
    coinsbit_constants as CONSTANTS,
    coinsbit_web_utils as web_utils,
)
from hummingbot.connector.exchange.coinsbit.coinsbit_api_order_book_data_source import CoinsbitAPIOrderBookDataSource
from hummingbot.connector.exchange.coinsbit.coinsbit_api_user_stream_data_source import CoinsbitAPIUserStreamDataSource
from hummingbot.connector.exchange.coinsbit.coinsbit_auth import CoinsbitAuth
from hummingbot.connector.exchange_py_base import ExchangePyBase
from hummingbot.connector.trading_rule import TradingRule

# from hummingbot.connector.utils import TradeFillOrderDetails, combine_to_hb_trading_pair
from hummingbot.connector.utils import combine_to_hb_trading_pair
from hummingbot.core.api_throttler.data_types import RateLimit
from hummingbot.core.data_type.common import OrderType, TradeType

# from hummingbot.core.data_type.in_flight_order import InFlightOrder, OrderUpdate, TradeUpdate
from hummingbot.core.data_type.in_flight_order import InFlightOrder, OrderUpdate
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource
from hummingbot.core.data_type.trade_fee import DeductedFromReturnsTradeFee, TokenAmount, TradeFeeBase
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource

# from hummingbot.core.event.events import MarketEvent, OrderFilledEvent
# from hummingbot.core.utils.async_utils import safe_gather
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory

if TYPE_CHECKING:
    from hummingbot.client.config.config_helpers import ClientConfigAdapter


class CoinsbitExchange(ExchangePyBase):
    web_utils = web_utils

    def __init__(self,
                 client_config_map: "ClientConfigAdapter",
                 coinsbit_api_key: str,
                 coinsbit_api_secret: str,
                 coinsbit_websocket_token: str,
                 trading_pairs: Optional[List[str]] = None,
                 trading_required: bool = True,
                 domain: str = CONSTANTS.DEFAULT_DOMAIN):
        self.api_key = coinsbit_api_key
        self.secret_key = coinsbit_api_secret
        self.websocket_token = coinsbit_websocket_token
        self._domain = domain
        self._trading_required = trading_required
        self._trading_pairs = trading_pairs
        super().__init__(client_config_map)

    @staticmethod
    def coinsbit_order_type(order_type: OrderType) -> str:
        return order_type.name.upper()

    @staticmethod
    def to_hb_order_type(coinsbit_type: str) -> OrderType:
        return OrderType[coinsbit_type]

    @property
    def authenticator(self) -> AuthBase:
        return CoinsbitAuth(
            api_key=self.api_key,
            secret_key=self.secret_key,
            websocket_token=self.websocket_token
        )

    @property
    def name(self) -> str:
        return CONSTANTS.EXCHANGE_NAME

    @property
    def rate_limits_rules(self) -> List[RateLimit]:
        return CONSTANTS.RATE_LIMIT

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def client_order_id_max_length(self) -> int:
        return CONSTANTS.MAX_ORDER_ID_LEN

    @property
    def client_order_id_prefix(self) -> str:
        return CONSTANTS.HBOT_ORDER_ID_PREFIX

    # TODO: Complete after
    # @property
    # def trading_rules_request_path(self) -> str:
    #     return super().trading_rules_request_path

    # @property
    # def check_network_request_path(self) -> str:
    #     return super().check_network_request_path
    # TODO: Complete after

    @property
    def trading_pairs(self) -> List[str]:
        return self._trading_pairs

    @property
    def is_cancel_request_in_exchange_synchronous(self) -> bool:
        return True

    @property
    def is_trading_required(self) -> bool:
        return self._trading_required

    def supported_order_types(self) -> List[OrderType]:
        return [OrderType.LIMIT, OrderType.MARKET]

    async def get_all_pairs_prices(self) -> List[Dict[str, str]]:
        pairs_prices = await self._api_get(path_url=CONSTANTS.TICKERS_BOOK_PATH_URL)
        return pairs_prices

    def _is_request_exception_related_to_time_synchronizer(self, request_exception: Exception) -> bool:
        # API documentation does not clarify the error message for timestamp related problems
        return False

    def _is_order_not_found_during_status_update_error(self, status_update_exception: Exception) -> bool:
        # TODO: implement this method correctly for the connector
        # The default implementation was added when the functionality to detect not found orders was introduced in the
        # ExchangePyBase class. Also fix the unit test test_lost_order_removed_if_not_found_during_order_status_update
        # when replacing the dummy implementation
        return False

    def _is_order_not_found_during_cancelation_error(self, cancelation_exception: Exception) -> bool:
        # TODO: implement this method correctly for the connector
        # The default implementation was added when the functionality to detect not found orders was introduced in the
        # ExchangePyBase class. Also fix the unit test test_cancel_order_not_found_in_the_exchange when replacing the
        # dummy implementation
        return False

    def _create_web_assistants_factory(self) -> WebAssistantsFactory:
        return web_utils.build_api_factory(
            throttler=self._throttler,
            time_synchronizer=self._time_synchronizer,
            domain=self._domain,
            auth=self._auth
        )

    def _create_order_book_data_source(self) -> OrderBookTrackerDataSource:
        return CoinsbitAPIOrderBookDataSource(
            trading_pairs=self._trading_pairs,
            connector=self,
            domain=self._domain,
            api_factory=self._web_assistants_factory
        )

    def _create_user_stream_data_source(self) -> UserStreamTrackerDataSource:
        return CoinsbitAPIUserStreamDataSource(
            auth=self._auth,
            trading_pairs=self._trading_pairs,
            connector=self,
            api_factory=self._web_assistants_factory,
            domain=self._domain
        )

    def _get_fee(self,
                 base_currency: str,
                 quote_currency: str,
                 order_type: OrderType,
                 order_side: OrderType,
                 amount: Decimal,
                 price: Decimal = s_decimal_NaN,
                 is_maker: Optional[bool] = None) -> TradeFeeBase:
        is_maker = order_type is OrderType.LIMIT_MAKER
        return DeductedFromReturnsTradeFee(percent=self.estimate_fee_pct(is_maker))

    async def _place_order(self,
                           trading_pair: str,
                           amount: Decimal,
                           trade_type: TradeType,
                           price: Decimal,
                           **kwargs) -> Tuple[str, float]:
        symbol = await self.exchange_symbol_associated_to_pair(trading_pair=trading_pair)

        data = {
            'market': symbol,
            'side': trade_type.name.lower(),
            'amount': f"{amount:f}",
            'price': f"{price:f}"
        }
        order_result = await self._api_post(
            path_url=CONSTANTS.CREATE_ORDER_PATH,
            data=data,
            is_auth_required=True)
        if not order_result.get('success'):
            raise IOError({"label": "ORDER_REJECTED", "message": "Order rejected."})
        order_id = order_result.get('result')[0]
        transact_time = order_result.get('result')[5]
        return order_id, transact_time

    async def _place_cancel(self, order_id: str, tracked_order: InFlightOrder):
        symbol = await self.exchange_symbol_associated_to_pair(trading_pair=tracked_order.trading_pair)
        api_params = {
            "market": symbol,
            'orderId': order_id
        }
        cancel_result = await self._api_post(
            path_url=CONSTANTS.CANCEL_ORDER_PATH,
            params=api_params,
            is_auth_required=True
        )
        if cancel_result.get('success'):
            return True
        return False

    async def _format_trading_rules(self, raw_trading_pair_info: Dict[str, Any]) -> List[TradingRule]:
        """
        Converts json API response into a dictionary of trading rules.

        :param raw_trading_pair_info: The json API response
        :return A dictionary of trading rules.

        Exam raw_trading_pair_info:
        https://api.coinsbit.io/api/v1/public/markets
        """
        result = []
        for info in raw_trading_pair_info['result']:
            if web_utils.is_pair_information_valid(info):
                try:
                    pass
                    # trading_pair = await self.trading_pair_associated_to_exchange_symbol(symbol=info.get('name'))
                    # result.append(
                    #     TradingRule(
                    #     trading_pair=trading_pair,
                    #     min_order_size=Decimal(info['moneyPrec']),
                    #     min_order_=Decimal
                    #     )
                    # )
                except Exception:
                    self.logger().exception(f"Error parsing the trading pair rule {info}. Skipping.")
        return result

    async def _status_polling_loop_fetch_updates(self):
        await super()._status_polling_loop_fetch_updates()

    async def _update_trading_fees(self):
        """
        Update fees information from the exchange
        """
        pass

    async def _all_trade_updates_for_order(self, order: InFlightOrder) -> List[OrderUpdate]:
        trade_updates = []
        if order.exchange_order_id is not None:
            exchange_order_id = int(order.exchange_order_id)
            trading_pair = self.exchange_symbol_associated_to_pair(trading_pair=order.trading_pair)
            all_fills_response = await self._api_get(
                path_url=CONSTANTS.ACCOUNT_TRADE_PATH_URL,
                params={
                    "orderId": exchange_order_id
                },
                is_auth_required=True,
                limit_id=CONSTANTS.ACCOUNT_TRADE_PATH_URL)

            for trade in all_fills_response['result']['records']:
                exchange_order_id = str(trade['id'])
                fee = TradeFeeBase.new_spot_fee(
                    fee_schema=self.trade_fee_schema(),
                    trade_type=order.trade_type,
                    percent_token=None,
                    flat_fees=[TokenAmount(amount=Decimal(trade['fee']), token=None)]
                )
                trade_update = TradeType(
                    trade_id=str(trade['id']),
                    client_order_id=order.client_order_id,
                    exchange_order_id=exchange_order_id,
                    trading_pair=trading_pair,
                    fee=fee,
                    fill_base_amount=Decimal(trade['amount']),
                    fill_quote_amount=Decimal(trade['amount']) * Decimal(trade['price']),
                    fill_price=Decimal(trade['price']),
                    fill_timestamp=trade['time']
                )
                trade_updates.append(trade_update)
        return trade_updates

    async def _update_balances(self):
        local_asset_names = set(self._account_balances.keys())
        remote_asset_names = set()

        account_info = await self._api_post(
            path_url=CONSTANTS.ACCOUNT_BALANCES_PATH_URL,
            is_auth_required=True,
            limit_id=CONSTANTS.ACCOUNT_BALANCES_PATH_URL
        )
        for asset, value in account_info['result'].items():
            free_balance = None
            locked_balance = None
            for key, amount in value.item():
                if key == 'available':
                    free_balance = Decimal(amount)
                elif key == 'freeze':
                    locked_balance = Decimal(amount)
            asset_name = asset
            total_balance = Decimal(free_balance) + Decimal(locked_balance)
            self._account_available_balances[asset_name] = free_balance
            self._account_balances[asset_name] = total_balance
            remote_asset_names.add(asset_name)

        asset_names_to_remove = local_asset_names.difference(remote_asset_names)
        for asset_name in asset_names_to_remove:
            del self._account_available_balances[asset_name]
            del self._account_balances[asset_name]

    def _initialize_trading_pair_symbols_from_exchange_info(self, exchange_info: Dict[str. Any]):
        mapping = bidict()
        for symbol_data in filter(web_utils.is_pair_information_valid, exchange_info):
            mapping[symbol_data['name']] = combine_to_hb_trading_pair(base=symbol_data['stock'],
                                                                      quote=symbol_data['money'])
        self._set_trading_pair_symbol_map(mapping)

    async def _get_last_traded_price(self, trading_pair: str) -> float:
        params = {
            'market': await self.exchange_symbol_associated_to_pair(trading_pair=trading_pair)
        }

        response_json = await self._api_request(
            method=RESTMethod.GET,
            path_url=CONSTANTS.TICKER_PATH_URL,
            params=params
        )

        return float(response_json['result']['last'])
