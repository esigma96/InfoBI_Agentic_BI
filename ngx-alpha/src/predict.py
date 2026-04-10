def generate_predictions(model, df):
    features = ['Return', 'MA_3', 'MA_7', 'Sentiment', 'Sentiment_MA']
    
    df['Prediction'] = model.predict(df[features])

    df['Recommendation'] = df['Prediction'].map({
        1: 'BUY',
        0: 'SELL'
    })

    return df