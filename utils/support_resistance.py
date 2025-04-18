import pandas as pd

def detect_zones(df, window=20):
    support = []
    resistance = []

    for i in range(window, len(df)-window):
        low_range = df['Low'].iloc[i-window:i+window]
        high_range = df['High'].iloc[i-window:i+window]
        
        if df['Low'].iloc[i] == low_range.min():
            support.append(df['Low'].iloc[i])
        if df['High'].iloc[i] == high_range.max():
            resistance.append(df['High'].iloc[i])

    return pd.Series(support).drop_duplicates().tolist(), pd.Series(resistance).drop_duplicates().tolist()
