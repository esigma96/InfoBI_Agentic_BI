import pandas as pd

def load_data():
    prices = pd.read_csv('data/stock_prices.csv')
    sentiment = pd.read_csv('data/sentiment_data.csv')

    prices['Date'] = pd.to_datetime(prices['Date'])
    sentiment['Date'] = pd.to_datetime(sentiment['Date'])

    df = pd.merge(prices, sentiment, on=['Date', 'Stock'], how='inner')

    return df