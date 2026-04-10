import pandas as pd

def create_features(df):
    df = df.sort_values(by='Date')

    # Price features
    df['Return'] = df['Close'].pct_change()
    df['MA_3'] = df['Close'].rolling(3).mean()
    df['MA_7'] = df['Close'].rolling(7).mean()

    # Sentiment smoothing
    df['Sentiment_MA'] = df['Sentiment'].rolling(3).mean()

    # Target: next day movement
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    df = df.dropna()

    return df