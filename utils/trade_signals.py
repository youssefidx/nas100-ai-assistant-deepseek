import pandas as pd
import numpy as np

def generate_trade_signals(df, zones, use_volume=True):
    support, resistance = zones
    signals = []
    
    # Filter nearby levels (0.5% threshold)
    support = [s for s in support if not any(abs(s-x)/s < 0.005 for x in support if x != s)]
    resistance = [r for r in resistance if not any(abs(r-x)/r < 0.005 for x in resistance if x != r)]
    
    # Add confirmation requirement (price must cross level)
    for i in range(2, len(df)):
        prev_close = df['Close'].iloc[i-1]
        current_close = df['Close'].iloc[i]
        volume = df['Volume'].iloc[i] if 'Volume' in df.columns else 0
        
        # Support Breakout (BUY)
        for s in support:
            if (prev_close < s) and (current_close > s):
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Buy",
                        "Price": current_close,
                        "Type": "Support Breakout"
                    })
                    break
        
        # Resistance Rejection (SELL)
        for r in resistance:
            if (prev_close > r) and (current_close < r):
                if not use_volume or volume > df['Volume'].rolling(20).mean().iloc[i]:
                    signals.append({
                        "Datetime": df.index[i],
                        "Signal": "Sell",
                        "Price": current_close,
                        "Type": "Resistance Rejection"
                    })
                    break
    
    signals_df = pd.DataFrame(signals)
    
    # Remove duplicate signals in same direction
    signals_df = signals_df.drop_duplicates(
        subset=['Datetime', 'Signal'], 
        keep='first'
    )
    
    return signals_df
