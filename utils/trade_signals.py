import pandas as pd
import numpy as np

def generate_trade_signals(df, zones, use_volume=True):
    support, resistance = zones
    signals = []
    
    # Filter significant levels
    min_diff = df['Close'].mean() * 0.005  # 0.5% of average price
    support = [s for s in support if not any(abs(s-x) < min_diff for x in support if x != s)]
    resistance = [r for r in resistance if not any(abs(r-x) < min_diff for x in resistance if x != r)]
    
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Check support bounce (BUY)
        for s in support:
            if (prev['Low'] <= s * 1.001) and (current['Close'] > s * 1.001):
                if not use_volume or current['Volume'] > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Buy",
                        "Price": current['Close'],
                        "Type": "Support Bounce"
                    })
                    break
        
        # Check resistance rejection (SELL)
        for r in resistance:
            if (prev['High'] >= r * 0.999) and (current['Close'] < r * 0.999):
                if not use_volume or current['Volume'] > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Sell",
                        "Price": current['Close'],
                        "Type": "Resistance Reject"
                    })
                    break
    
    return pd.DataFrame(signals).drop_duplicates(subset=['Datetime', 'Signal'])
