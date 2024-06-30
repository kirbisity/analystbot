import os
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime

directory = 'data/macro_data'


def plot_graph(df, columns):
    plt.figure(figsize=(14, 10))
    for i, c, in enumerate(columns):
        plt.subplot(2, 1, 1+i)
        plt.plot(df['Date'], df[c], marker=None, linestyle='-')
        plt.xlabel('Date')
        plt.ylabel(f'{c}')
        plt.grid(True)


def show_graph(df, columns, interval=1):
    sampled_df = df[1::interval]
    plot_graph(sampled_df, columns)
    plt.show()


def save_graph(name, df, columns, interval=1):
    sampled_df = df[1::interval]
    plot_graph(sampled_df, columns)
    plt.savefig(name)
    plt.clf


def get_data_in_date_range(df, start, end):
    start_date = pd.to_datetime(f'{start}')
    end_date = pd.to_datetime(f'{end}')
    filtered_df = df[(pd.to_datetime(df['Date']) >= start_date) & (pd.to_datetime(df['Date']) < end_date)]
    return filtered_df

def get_data_in_year_range(df, start, end):
    start_date = pd.to_datetime(f'{start}-01-01')
    end_date = pd.to_datetime(f'{end + 1}-01-01')
    filtered_df = df[(pd.to_datetime(df['Date']) >= start_date) & (pd.to_datetime(df['Date']) < end_date)]
    return filtered_df


def read_nasdaq_data(directory):
    dfs = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)

            idf = pd.read_csv(file_path, usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
            idf['Date'] = pd.to_datetime(idf['Date'], format='%Y-%m-%d')
            idf['Open'] = idf['Open'].astype(float)
            idf['High'] = idf['High'].astype(float)
            idf['Low'] = idf['Low'].astype(float)
            idf['Close'] = idf['Close'].astype(float)
            idf['Adj Close'] = idf['Adj Close'].astype(float)
            idf['Volume'] = idf['Volume'].astype(float)
            idf['Price'] = idf['Open']
            idf['Total value'] = idf['Price'] * idf['Volume']
            dfs.append(idf)

    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(by=['Date'], ascending=True)

    df['Change% Price'] = df['Price'].pct_change() * 100
    df = df.dropna()
    df = df.reset_index(drop=True)

    df['Monthly Avg Price'] = df['Price'].rolling(window=30, min_periods=1).mean()
    return df


def read_gdp_data(directory):
    dfs = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            idf = pd.read_csv(file_path, usecols=['Date', 'GDP'])
            idf['Date'] = pd.to_datetime(idf['Date'], format='%Y-%m-%d')
            dfs.append(idf)

    df = pd.concat(dfs)
    df = df.sort_values(by=['Date'], ascending=True)


    df_daily = df.set_index('Date').resample('d').mean()
    df = df_daily.interpolate(method='linear')
    return df


def read_pe_data(directory):
    dfs = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            idf = pd.read_csv(file_path, usecols=['Date', 'PE'])
            idf['Date'] = pd.to_datetime(idf['Date'], format='%Y-%m-%d')
            dfs.append(idf)

    df = pd.concat(dfs)
    df = df.sort_values(by=['Date'], ascending=True)


    #df_daily = df.set_index('Date').resample('d').mean()
    #df = df_daily.interpolate(method='linear')
    return df

def read_btc_data(directory):
    dfs = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            idf = pd.read_csv(file_path, usecols=['Start', 'End', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap'])
            idf['Date'] = pd.to_datetime(idf['Start'], format='%Y-%m-%d')
            dfs.append(idf)

    df = pd.concat(dfs)
    df = df.sort_values(by=['Date'], ascending=True)
    return df


def simulate_inverse_etf(df, price_column='Close'):
    """
    Simulate an inverse (-1x) linked exposure ETF that shorts the asset.

    Parameters:
    - df: DataFrame containing historical daily prices with at least one column representing the prices.
    - price_column: The column name in df representing the daily prices.

    Returns:
    - A DataFrame with the simulated inverse ETF prices.
    """
    # Ensure the DataFrame contains the necessary price column
    if price_column not in df.columns:
        raise ValueError(f"The DataFrame must contain a '{price_column}' column.")

    df['Daily_Return'] = df[price_column].pct_change()
    df['Inverse_ETF_Daily_Return'] = -df['Daily_Return']
    # Assuming the initial price of the inverse ETF is the same as the initial price of the asset
    initial_price = df[price_column].iloc[0]
    # Calculate the cumulative returns to get the price series of the inverse ETF
    df['Inverse ETF Price'] = initial_price * (1 + df['Inverse_ETF_Daily_Return']).cumprod()
    # Clean up the DataFrame by dropping intermediate columns
    df.drop(columns=['Daily_Return', 'Inverse_ETF_Daily_Return'], inplace=True)
    return df


def predict_future(df_in, y_column_nm, verbose=False):
    model = Prophet()
    df_c = df_in.rename(columns={'Date': 'ds', y_column_nm: 'y'})
    model.fit(df_c)
    future_dates = model.make_future_dataframe(periods=300)
    forecast_df = model.predict(future_dates)

    if (verbose):
        plt.figure(figsize=(14, 10))
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(forecast_df['ds'], forecast_df['yhat'], label='yhat (Predicted)', color='blue')
        ax.fill_between(forecast_df['ds'], forecast_df['yhat_lower'], forecast_df['yhat_upper'], color='gray', alpha=0.3, label='Uncertainty Interval')
        ax.scatter(df_c['ds'], df_c['y'], label='Actual', color='black', s=10)
        ax.set_title('Forecasted Prices')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        plt.savefig(f'output/prophet.png')
        plt.clf

    return forecast_df


if __name__=='__main__':

    nasdaq_df = read_nasdaq_data('data/NASDAQ')
    gdp_df = read_gdp_data('data/GDP')
    pe_df = read_pe_data('data/PE_Ratio')

    btc_df = read_btc_data('data/BTC')

    year_ranges = [
        1980,
        1990,
        2000,
        2010,
        2020,
        2030
    ]

    btc_df = get_data_in_date_range(btc_df, '2021-10-25', '2024-05-11')
    btc_pf_df = predict_future(btc_df, "Close", verbose=True)
    biti_df = simulate_inverse_etf(btc_df, "Close")
    
    save_graph("output/btc.png", btc_df, ['Close'])
    save_graph("output/biti.png", biti_df, ['Inverse ETF Price'])
    #show_graph(get_data_in_year_range(pe_df, 2000, 2024), ['PE'])

    #show_graph(get_data_in_year_range(nasdaq_df, 2000, 2024), ['Close', 'Volume'])

    if False:
        for i in range(1, len(year_ranges)):
            start, end = year_ranges[i-1], year_ranges[i]
            save_graph(f'output/nasdaq_{start}_{end}', get_data_in_year_range(nasdaq_df, start, end), ['Price', 'Total value'], interval=3)
            plt.clf()
    
    #show_graph(get_data_in_year_range(nasdaq_df, 2000, 2024), ['GDP'])
