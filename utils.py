from hyperliquid.info import Info
from hyperliquid.utils import constants
import pandas as pd
import numpy as np




def display_recent_open_orders(df: pd.DataFrame, max_orders: int = 5) -> str:
    # Check if DataFrame is empty
    if df.empty:
        return "No open orders available."

    # Sort the DataFrame by the 'timestamp' column in descending order
    df.sort_values(by='timestamp', ascending=False, inplace=True)

    # Select the most recent 5 or fewer rows
    recent_orders = df.head(max_orders)

    # Format the output as a string for display
    output_str = recent_orders.to_string(index=False)
    return output_str



import pandas as pd
import matplotlib.pyplot as plt

def create_funding_rates_heatmap(funding_history):
    # Convert to DataFrame
    df = pd.DataFrame(funding_history)

    # Convert Unix timestamp in milliseconds to datetime
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    # Ensure 'fundingRate' is numeric
    df['fundingRate'] = pd.to_numeric(df['fundingRate'], errors='coerce')

    # Pivot the DataFrame for the heatmap
    heatmap_data = df.pivot(index="coin", columns="time", values="fundingRate")

    # Handle NaN values in heatmap_data, e.g., fill with zeros or interpolate
    heatmap_data = heatmap_data.fillna(0)

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(10, 4))  # Adjust the size as needed
    cax = ax.imshow(heatmap_data, cmap='Greens', aspect='auto')

    # Add color bar
    fig.colorbar(cax)

    # Add labels
    ax.set_xticks(np.arange(len(heatmap_data.columns)))
    ax.set_xticklabels([time.strftime('%Y-%m-%d %H:%M') for time in heatmap_data.columns], rotation=45)
    ax.set_yticks(np.arange(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)

    ax.set_title('Funding Rates Heatmap')

    return fig
import asyncio
import datetime
import json
import pandas as pd
from pathlib import Path
from hyperliquid import info
from hyperliquid.info import Info
from hyperliquid.utils import constants
async def fetch_and_save_rates():
    # Initialize the API client
    info = Info(constants.MAINNET_API_URL, skip_ws=True)

    while True:
        now = datetime.datetime.now()
        metas = info.meta()  # Fetch current rates
        json_data = json.loads(metas) if isinstance(metas, str) else metas

        # Initialize an empty list to hold the data for each coin
        data_list = []

        # Ensure there is a 'universe' and additional data
        if 'universe' in json_data[0] and len(json_data) > 1:
            additional_data = json_data[1]  # This is the additional data array
            
            for i, coin_info in enumerate(json_data[0]['universe']):
                # Match each 'universe' entry with its corresponding additional data by index
                if i < len(additional_data):
                    combined_info = additional_data[i]
                    name = coin_info['name']  # Get the coin name from the 'universe' part
                    
                    # Add each coin's combined info as a dictionary to the list
                    data_list.append({
                        'name': name,
                        'premium': combined_info.get('premium', None),  # Use get() to handle missing keys
                        'funding': combined_info.get('funding', None),  # Get the funding rate
                        'timestamp': now
                    })
                else:
                    # If there's no corresponding additional data, add what's available
                    data_list.append({
                        'name': coin_info['name'],
                        'premium': None,
                        'funding': None,
                        'timestamp': now
                    })

        # Create a DataFrame from the list of dictionaries
        new_entries_df = pd.DataFrame(data_list)

        # Convert 'premium' and 'funding' to numeric
        new_entries_df['premium'] = pd.to_numeric(new_entries_df['premium'], errors='coerce')
        new_entries_df['funding'] = pd.to_numeric(new_entries_df['funding'], errors='coerce')

        # Check if the CSV file exists and append current data
        csv_file = 'historical_data.csv'
        file_exists = Path(csv_file).is_file()

        # If the file doesn't exist, write with header, otherwise append without header
        new_entries_df.to_csv(csv_file, mode='a', header=not file_exists, index=False)

        await asyncio.sleep(30)  # Wait for 30 seconds before next fetch
