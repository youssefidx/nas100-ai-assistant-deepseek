import pandas as pd

def generate_trade_signals(df, zones, use_volume=True):
    support, resistance = zones
    signals = []
    
    support = [s for s in support if not any(abs(s-x)/s < 0.002 for x in support if x != s)]
    resistance = [r for r in resistance if not any(abs(r-x)/r < 0.002 for x in resistance if x != r)]

    for i in range(1, len(df)):
        close = df['Close'].iloc[i]
        volume = df['Volume'].iloc[i] if 'Volume' in df.columns else 0
        
        for s in support:
            if abs(close - s)/s < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Buy",
                        "Price": close
                    })
                    break

        for r in resistance:
            if abs(close - r)/r < 0.001:
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i], 
                        "Signal": "Sell",
                        "Price": close
                    })
                    break

    signals_df = pd.DataFrame(signals)
    signals_df = signals_df.drop_duplicates(subset=['Datetime', 'Signal'], keep='first')
    return signals_df
