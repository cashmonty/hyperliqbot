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
