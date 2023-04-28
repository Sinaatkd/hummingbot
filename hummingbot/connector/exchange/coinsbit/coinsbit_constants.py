# General Information
EXCHANGE_NAME = 'coinsbit'
DEFAULT_DOMAIN = 'io'

# Base URL
REST_URL = 'https://coinsbit.{}/api/'
WSS_URL = 'wss://coinsbit.{}/trade_ws'

PUBLIC_API_VERSION = 'v1'
PRIVATE_API_vERSION = 'v1'

# Public API endpoints
SNAPSHOT_PATH_URL = '/public/depth/result'

# Private API endpoints
ACCOUNT_BALANCES_PATH = '/account/balances'
ACCOUNT_BALANCE_PATH = '/account/balance'

WS_HEARTBEAT_TIME_INTERVAL = 30

# Websocket event types
DIFF_EVENT_TYPE = "depth.update"
TRADE_EVENT_TYPE = "deals.update"

# Coinsbit params
SIDE_BUY = "buy"
SIDE_SELL = "sell"


RATE_LIMIT = []
