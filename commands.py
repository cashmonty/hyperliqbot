
import discord
import datetime
from discord.ext import commands
from hyperliquid.info import Info
from hyperliquid.utils import constants
import pandas as pd
import json
import matplotlib.pyplot as plt
import io
from utils import create_funding_rates_heatmap, display_recent_open_orders

# Initialize the API client
info = Info(constants.MAINNET_API_URL, skip_ws=True)

# Function to convert JSON string to DataFrame
def json_to_df(json_str):
    return pd.DataFrame(json.loads(json_str))




@commands.command(name='positions', help='Display the most recent 5 or fewer asset positions')
async def positions(ctx, user_address: str):
    user_state = info.user_state(user_address)

    if user_state and 'assetPositions' in user_state:
        df_asset_positions = pd.json_normalize(user_state['assetPositions'])

        # Selecting specific columns and renaming them for clarity
        columns_to_display = ['position.coin', 'position.positionValue', 'position.entryPx', 'position.leverage.type', 'position.leverage.value', 'position.unrealizedPnl']
        df_asset_positions = df_asset_positions[columns_to_display]
        df_asset_positions.columns = ['Coin', 'Positions Size', 'Entry Price', 'Leverage Type', 'Leverage Value', 'Unrealized PnL']

        # Convert 'Entry Price' and 'Unrealized PnL' to numeric
        df_asset_positions['Entry Price'] = pd.to_numeric(df_asset_positions['Entry Price'], errors='coerce').round(2)
        df_asset_positions['Unrealized PnL'] = pd.to_numeric(df_asset_positions['Unrealized PnL'], errors='coerce')

        # Formatting 'Unrealized PnL' with 2 decimal places and handling NaNs
        df_asset_positions['Unrealized PnL'] = df_asset_positions['Unrealized PnL'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)

        df_recent_positions = df_asset_positions.sort_values('Entry Price', ascending=False).head(5)
        recent_positions_str = df_recent_positions.to_string(index=False)
        await ctx.send(f"Recent Asset Positions:\n```\n{recent_positions_str}\n```")
    else:
        await ctx.send("Failed to fetch asset positions.")



@commands.command(name='recentorders', help='Display the most recent 5 or fewer open orders')
async def recentorders(ctx, user_address: str):
    open_orders = info.open_orders(user_address)

    if open_orders:
        df_open_orders = pd.DataFrame(open_orders)

        # Convert 'timestamp' to a readable format
        df_open_orders['timestamp'] = pd.to_datetime(df_open_orders['timestamp'], unit='ms')

        # Convert to numeric and round, handling non-numeric values
        numeric_columns = ['limitPx', 'origSz', 'sz']
        for column in numeric_columns:
            df_open_orders[column] = pd.to_numeric(df_open_orders[column], errors='coerce').round(2)

        recent_orders_str = df_open_orders.to_string(index=False)
        await ctx.send(f"Recent Open Orders:\n```\n{recent_orders_str}\n```")
    else:
        await ctx.send("Failed to fetch open orders.")


@commands.command(name='allprices', help='Display current prices of all coins')
async def allprices(ctx):
    all_mids = info.all_mids()
    if all_mids:
        # Convert the dictionary to a DataFrame for easier formatting
        df_all_mids = pd.DataFrame(list(all_mids.items()), columns=['Coin', 'Price'])

        # Convert DataFrame to a string for display
        all_prices_str = df_all_mids.to_string(index=False)
        await ctx.send(f"All Prices:\n```\n{all_prices_str}\n```")
    else:
        await ctx.send("Failed to fetch prices.")

@commands.command(name='userfills', help='Display the most recent 3 user fills')
async def userfills(ctx, user_address: str):
    user_fills = info.user_fills(user_address)
    if user_fills:
        df_user_fills = pd.DataFrame(user_fills)

        # Assuming 'time' is in Unix milliseconds format
        df_user_fills['time'] = pd.to_datetime(df_user_fills['time'], unit='ms')

        # Sort by 'time' in descending order and select top 3
        df_recent_fills = df_user_fills.sort_values('time', ascending=False).head(3)

        # Formatting numeric columns
        # Example: df_recent_fills['some_numeric_column'] = df_recent_fills['some_numeric_column'].apply(lambda x: f"{x:,.2f}")

        recent_fills_str = df_recent_fills.to_string(index=False, justify='left')
        await ctx.send(f"Recent Fills for {user_address}:\n```\n{recent_fills_str}\n```")
    else:
        await ctx.send(f"Failed to fetch fills for {user_address}.")





@commands.command(name='recentorders', help='Display the most recent 5 or fewer open orders')
async def recentorders(ctx, user_address: str):
    open_orders = info.open_orders(user_address)

    if open_orders:
        df_open_orders = pd.DataFrame(open_orders)

        # Convert 'timestamp' to a readable format and rename columns
        df_open_orders['timestamp'] = pd.to_datetime(df_open_orders['timestamp'], unit='ms')

        # Rename columns to more descriptive names
        df_open_orders.rename(columns={
            'coin': 'Coin',
            'limitPx': 'Limit Price',
            'oid': 'Order ID',
            'origSz': 'Original Size',
            'reduceOnly': 'Reduce Only',
            'side': 'Side',
            'sz': 'Size',
            'timestamp': 'Timestamp'
        }, inplace=True)

        # Convert to numeric and round, handling non-numeric values
        numeric_columns = ['Limit Price', 'Original Size', 'Size']
        for column in numeric_columns:
            df_open_orders[column] = pd.to_numeric(df_open_orders[column], errors='coerce').round(2)

        recent_orders_str = df_open_orders.to_string(index=False)
        await ctx.send(f"Recent Open Orders:\n```\n{recent_orders_str}\n```")
    else:
        await ctx.send("Failed to fetch open orders.")
