from hyperliquid.info import Info
from hyperliquid.utils import constants
import pandas as pd
import json

# Initialize the API client
info = Info(constants.MAINNET_API_URL, skip_ws=True)

# Function to convert JSON string to DataFrame
def json_to_df(json_str):
    return pd.DataFrame(json.loads(json_str))

# Example user address and coin
user_address = "0xcd5051944f780a621ee62e39e493c489668acf4d"
coin = "BTC"
start_time = 1701450403  # Example Unix timestamp in milliseconds


# User State
user_state = info.user_state(user_address)
df_user_state = json_to_df(user_state)

# Open Orders
open_orders = info.open_orders(user_address)
df_open_orders = json_to_df(open_orders)

# Frontend Open Orders
frontend_open_orders = info.frontend_open_orders(user_address)
df_frontend_open_orders = json_to_df(frontend_open_orders)

# All Mids
all_mids = info.all_mids()
df_all_mids = json_to_df(all_mids)

# User Fills
user_fills = info.user_fills(user_address)
df_user_fills = json_to_df(user_fills)

# Funding History
funding_history = info.funding_history(coin, start_time, end_time)
df_funding_history = json_to_df(funding_history)

# L2 Snapshot
l2_snapshot = info.l2_snapshot(coin)
df_l2_snapshot = json_to_df(l2_snapshot)

# Candles Snapshot
candles_snapshot = info.candles_snapshot(coin, "1m", start_time, end_time)  # Example interval "1m"
df_candles_snapshot = json_to_df(candles_snapshot)

# Example print statement for one DataFrame
print(df_user_state)

