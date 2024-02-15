
import discord
import datetime
from discord.ext import commands
from hyperliquid.info import Info
from hyperliquid.utils import constants
import pandas as pd
import json
import matplotlib.pyplot as plt
import io
from utils import create_funding_rates_heatmap, display_recent_open_orders, fetch_and_save_rates

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

import datetime
import pandas as pd
import json
import matplotlib.pyplot as plt
import io
import discord
@commands.command(name='basischart', help='Display the basis rates for the current day')
async def basischart(ctx):
    now = datetime.datetime.now()
    one_hour_ago = now - datetime.timedelta(hours=1)
    
    # Load historical data from CSV
    historical_df = pd.read_csv('historical_data.csv', parse_dates=['timestamp'])
    
    # Filter for data within the last hour
    last_hour_df = historical_df[(historical_df['timestamp'] >= one_hour_ago) & (historical_df['timestamp'] <= now)]
    
    # Calculate the 10 lowest basis rates within the last hour
    lowest_basis_rates = last_hour_df.groupby('name')['premium'].last().nsmallest(10)
    lowest_10_names = lowest_basis_rates.index.tolist()
    
    # Plotting
    plt.figure(figsize=(12, 8))
    for name in lowest_10_names:
        coin_data = last_hour_df[last_hour_df['name'] == name]
        plt.plot(coin_data['timestamp'], coin_data['premium'], label=name, linestyle='-')
    
    plt.xlabel('Time')
    plt.ylabel('Basis Rate')
    plt.title('Lowest 10 Basis Rates Over Last Hour')
    plt.xticks(rotation=45)
    plt.legend(title='Coin')
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    await ctx.send(file=discord.File(fp=buffer, filename='basis_rates.png'))
    plt.close()



@commands.command(name='fundingrates', help='Display the funding rates for the current day')
async def fundingrates(ctx, coin: str):
    coin = coin.upper()  # Convert coin to uppercase
    start_of_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)

    start_timestamp = int(start_of_day.timestamp() * 1000)
    end_timestamp = int(end_of_day.timestamp() * 1000)

    funding_history = info.funding_history(coin, start_timestamp, end_timestamp)

    if funding_history:
        # Call utility function to create heatmap
        heatmap_image = create_funding_rates_heatmap(funding_history)

        # Save the plot to a BytesIO object
        with io.BytesIO() as image_binary:
            heatmap_image.savefig(image_binary, format='PNG')
            image_binary.seek(0)
            await ctx.send(f"Funding Rates for {coin} on {start_of_day.date()}:", file=discord.File(fp=image_binary, filename='heatmap.png'))
    else:
        await ctx.send(f"Failed to fetch funding rates for {coin}.")
import asyncio

@commands.command(name='fundingchart', help='Display the funding rates for the current day')
async def fundingchart(ctx):
    now = datetime.datetime.now()
    one_hour_ago = now - datetime.timedelta(hours=1)
    
    # Load historical data from CSV
    historical_df = pd.read_csv('historical_data.csv', parse_dates=['timestamp'])
    
    # Filter for data within the last hour
    last_hour_df = historical_df[(historical_df['timestamp'] >= one_hour_ago) & (historical_df['timestamp'] <= now)]
    
    # Calculate the 10 highest funding rates within the last hour
    highest_funding_rates = last_hour_df.groupby('name')['funding'].last().nlargest(10)
    highest_10_names = highest_funding_rates.index.tolist()
    
    # Plotting
    plt.figure(figsize=(12, 8))
    for name in highest_10_names:
        coin_data = last_hour_df[last_hour_df['name'] == name]
        plt.plot(coin_data['timestamp'], coin_data['funding'], label=name, linestyle='-')
    
    plt.xlabel('Time')
    plt.ylabel('Funding Rate')
    plt.title('Highest 10 Funding Rates Over Last Hour')
    plt.xticks(rotation=45)
    plt.legend(title='Coin')
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    await ctx.send(file=discord.File(fp=buffer, filename='funding_rates.png'))
    plt.close()
