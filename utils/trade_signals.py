import pandas as pd

def generate_trade_signals(df, zones, use_volume=True, session_start=None):
    support, resistance = zones
    signals = []
    
    # Filter nearby levels (within 0.2%)
    support = [s for s in support if not any(abs(s-x)/s < 0.002 for x in support if x != s)]
    resistance = [r for r in resistance if not any(abs(r-x)/r < 0.002 for x in resistance if x != r)]

    for i in range(1, len(df)):
        current_time = df.index[i].time()
        if session_start and current_time < session_start:
            continue

        close = df['Close'].iloc[i]
        volume = df['Volume'].iloc[i] if 'Volume' in df.columns else 0
        
        # Check support (BUY)
        for s in support:
            if abs(close - s)/s < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Buy",
                        "Price": close,
                        "Type": "Support Bounce"
                    })
                    break  # Only one signal per level

        # Check resistance (SELL)
        for r in resistance:
            if abs(close - r)/r < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i], 
                        "Signal": "Sell",
                        "Price": close,
                        "Type": "Resistance Reject"
                    })
                    break

    signals_df = pd.DataFrame(signals)
    
    # Remove duplicates within 3 candles
    signals_df = signals_df[~signals_df.duplicated(subset=['Signal', 'Price'], keep='first')]
    
    return signals_df
