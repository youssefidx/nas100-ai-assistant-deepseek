import pandas as pd
import numpy as np

def detect_zones(df, window=50, min_strength=3):
    support = []
    resistance = []
    
    # Find swing highs/lows
    highs = df['High'].rolling(window, center=True).max()
    lows = df['Low'].rolling(window, center=True).min()
    
    # Cluster similar levels
    for level in highs.unique():
        if pd.notna(level):
            touches = sum((df['High'] >= level*0.998) & (df['High'] <= level*1.002))
            if touches >= min_strength:
                resistance.append(level)
    
    for level in lows.unique():
        if pd.notna(level):
            touches = sum((df['Low'] >= level*0.998) & (df['Low'] <= level*1.002))
            if touches >= min_strength:
                support.append(level)
    
    # Return top 10 strongest levels
    return sorted(support)[-10:], sorted(resistance)[:10]
