import pandas as pd

def generate_trade_signals(df, zones, use_volume=True, session_start=None):
    support, resistance = zones
    signals = []

    for i in range(1, len(df)):
        current_time = df.index[i].time()
        if session_start and current_time < session_start:
            continue

        close_price = df['Close'].iloc[i]
        volume = df['Volume'].iloc[i] if 'Volume' in df.columns else 0

        for s in support:
            if abs(close_price - s) / s < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({"Datetime": df.index[i], "Signal": "Buy", "Price": close_price})

        for r in resistance:
            if abs(close_price - r) / r < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({"Datetime": df.index[i], "Signal": "Sell", "Price": close_price})

    return pd.DataFrame(signals)