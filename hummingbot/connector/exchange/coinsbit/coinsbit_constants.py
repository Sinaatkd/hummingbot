from hummingbot.core.api_throttler.data_types import LinkedLimitWeightPair, RateLimit

# General Information
EXCHANGE_NAME = 'coinsbit'
DEFAULT_DOMAIN = 'io'

# Base URL
REST_URL = 'https://coinsbit.{}/api/'
WSS_URL = 'wss://coinsbit.{}/trade_ws'

PUBLIC_API_VERSION = 'v1'
PRIVATE_API_vERSION = 'v1'

HBOT_ORDER_ID_PREFIX = "hummingbot"
MAX_ORDER_ID_LEN = 32

# Public API endpoints
SNAPSHOT_PATH_URL = '/public/depth/result'
TICKERS_BOOK_PATH_URL = '/public/tickers'
TICKER_PATH_URL = '/public/ticker'

# Private API endpoints
CREATE_ORDER_PATH_URL = '/order/new'
ACCOUNT_BALANCES_PATH_URL = '/account/balances'
ACCOUNT_BALANCE_PATH_URL = '/account/balance'
ACCOUNT_TRADE_PATH_URL = '/account/trades'
CANCEL_ORDER_PATH = '/order/cancel'

WS_HEARTBEAT_TIME_INTERVAL = 30
LISTEN_KEY_KEEP_ALIVE_INTERVAL = 1800  # Recommended to Ping/Update listen key to keep connection alive
HEARTBEAT_TIME_INTERVAL = 30.0

# Websocket event types
DIFF_EVENT_TYPE = "depth.update"
TRADE_EVENT_TYPE = "deals.update"

# Coinsbit params
SIDE_BUY = "buy"
SIDE_SELL = "sell"

RATE_LIMIT = [
    RateLimit(limit_id=SNAPSHOT_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(SNAPSHOT_PATH_URL)]),
    RateLimit(limit_id=TICKERS_BOOK_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(TICKERS_BOOK_PATH_URL)]),
    RateLimit(limit_id=TICKER_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(TICKER_PATH_URL)]),
    RateLimit(limit_id=CREATE_ORDER_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(CREATE_ORDER_PATH_URL)]),
    RateLimit(limit_id=ACCOUNT_BALANCES_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(ACCOUNT_BALANCES_PATH_URL)]),
    RateLimit(limit_id=ACCOUNT_BALANCE_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(ACCOUNT_BALANCE_PATH_URL)]),
    RateLimit(limit_id=ACCOUNT_TRADE_PATH_URL, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(ACCOUNT_TRADE_PATH_URL)]),
    RateLimit(limit_id=CANCEL_ORDER_PATH, limit=200, time_interval=1, linked_limits=[LinkedLimitWeightPair(CANCEL_ORDER_PATH)]),
]
