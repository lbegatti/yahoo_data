from typing import Any

import plotly.express as px
import yfinance as yf

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
window = 50  # 50 days rolling window


def idx_change_chart(idx_ticker_list: list) -> dict[Any, Any]:
    """Method to fetch and plot the data from yahoo finance on some indexes.
    :param idx_ticker_list: list of tickers to get data of."""
    for t in idx_ticker_list:
        ticker = yf.Ticker(t)
        idx_data = ticker.history(period=time_period)[['Close', 'Volume']]
        pct_change_data = idx_data.pct_change()
        pct_change_data['price_change'] = pct_change_data['Close']
        pct_change_data['volume_change'] = pct_change_data['Volume']
        pct_change_data['rolling_mean'] = pct_change_data['price_change'].rolling(window).mean()
        pct_change_data['rolling_std'] = pct_change_data['price_change'].rolling(window).std()
        pct_change_data = pct_change_data[['price_change', 'volume_change', 'rolling_mean', 'rolling_std']]
        pct_change_data['U2STD'] = pct_change_data['rolling_mean'] + 2 * pct_change_data['rolling_std']
        pct_change_data['L2STD'] = pct_change_data['rolling_mean'] - 2 * pct_change_data['rolling_std']
        final = pct_change_data[['price_change', 'volume_change', 'rolling_mean', 'U2STD', 'L2STD']].dropna()
        fig = px.bar(final, x=final.index, y='price_change').update_traces(width=1000 * 3600 * 24 * 2.0)
        fig.add_scatter(x=final.index, y=final['U2STD'], name='U2STD')
        fig.add_scatter(x=final.index, y=final['L2STD'], name='L2STD')
        fig.add_scatter(x=final.index, y=final['rolling_mean'], name='Mov.Avg')
        fig.update_layout(
            title=t + f' Daily changes, roll.window {window} days',
            xaxis_title="Date",
            yaxis_title="Price changes (%)", )
        fig.show()
        index_data.update({t.split("^")[1]: final})
    return index_data


trump_index_impact = idx_change_chart(ticker_list)
index_data.keys()
