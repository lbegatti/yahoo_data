from typing import Any, Tuple, Union, Dict
import logging
import plotly.express as px
import yfinance as yf
from pandas import Timestamp, Series, DataFrame

logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Define the ticker symbol
SP500_ticker = "^SPX"
NASDAQ_ticker = "^IXIC"
DJIA_ticker = "^DJI"
NYSE_ticker = "^NYA"
NIKKEI_ticker = "^N225"

# Create a Ticker object
ticker_list = [SP500_ticker, NASDAQ_ticker, DJIA_ticker, NYSE_ticker, NIKKEI_ticker]

index_data = {}
time_period = '10y'
window = 20  # rolling window
no_of_std = 2  # standard practice
default_color = "blue"
colors = {Timestamp('2024-11-6 00:00:00-0500', tz='America/New_York'): "red"}


def get_data_from_yfinance(ticker_symbol: str) -> DataFrame:
    """
    Method to fetch the data from yfinance and build some measure like rolling avg, std.
    :param ticker_symbol: the ticker symbol as a string.
    :return: dataframe with the data.
    """
    ticker = yf.Ticker(ticker_symbol)
    logging.info(f' Getting data for {ticker_symbol} index...\n')
    idx_data = ticker.history(period=time_period)[['Close', 'Volume']]
    pct_change_data = idx_data.pct_change()
    pct_change_data['price_change'] = pct_change_data['Close']
    pct_change_data['volume_change'] = pct_change_data['Volume']
    pct_change_data['rolling_mean'] = pct_change_data['price_change'].rolling(window).mean()
    pct_change_data['rolling_std'] = pct_change_data['price_change'].rolling(window).std()
    pct_change_data = pct_change_data[['price_change', 'volume_change', 'rolling_mean', 'rolling_std']]
    pct_change_data['U2STD'] = pct_change_data['rolling_mean'] + no_of_std * pct_change_data['rolling_std']
    pct_change_data['L2STD'] = pct_change_data['rolling_mean'] - no_of_std * pct_change_data['rolling_std']
    final = pct_change_data[['price_change', 'volume_change', 'rolling_mean', 'U2STD', 'L2STD']].dropna()
    index_data.update({ticker_symbol.split("^")[1]: final})
    return final


def idx_chart(idx_ticker_list: list) -> dict[Any, Any]:
    """Method to plot index data daily changes.
    :param idx_ticker_list: list of tickers to obtain data from yfinance."""
    for t in idx_ticker_list:
        data = get_data_from_yfinance(t)
        color_discrete_map = {
            c: colors.get(c, default_color)
            for c in data.index.unique()}
        fig = px.bar(data, x=data.index, y='price_change', barmode='relative',
                     color=data.index, color_discrete_map=color_discrete_map).update_traces(
            width=1000 * 3600 * 24 * 0.9)
        fig.add_scatter(x=data.index, y=data['U2STD'], name='U2STD', mode='lines',
                        line=dict(dash='dot', color="green"))
        fig.add_scatter(x=data.index, y=data['L2STD'], name='L2STD', mode='lines',
                        line=dict(dash='dot', color="red"))
        fig.add_scatter(x=data.index, y=data['rolling_mean'], name='Mov.Avg', mode='lines',
                        line=dict(dash='dot', color="purple"))
        fig.update_layout(
            title=t + f' Daily changes (roll.window {window} (days))',
            xaxis_title="Date",
            yaxis_title="Price changes (%)",
            showlegend=False
        )
        fig.show()
        logging.info(f'Obtained and stored data for {t}.\n')
    return index_data


trump_index_impact = idx_chart(ticker_list)
index_data.keys()
