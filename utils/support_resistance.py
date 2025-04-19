import pandas as pd

def detect_zones(df, window=20, threshold=3):
    support = []
    resistance = []

    for i in range(window, len(df) - window):
        low_slice = df['Low'][i - window:i + window]
        high_slice = df['High'][i - window:i + window]
        current_low = df['Low'].iloc[i]
        current_high = df['High'].iloc[i]

        if current_low == low_slice.min():
            support.append(current_low)
        if current_high == high_slice.max():
            resistance.append(current_high)

    support_series = pd.Series(sorted(set(support)))
    resistance_series = pd.Series(sorted(set(resistance)))
    return support_series, resistance_series