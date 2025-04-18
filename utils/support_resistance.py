import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def detect_zones(df, window=50, min_touches=3, tolerance=0.002):
    highs = df['High']
    lows = df['Low']
    
    # Find swing points
    max_idx = argrelextrema(highs.values, np.greater_equal, order=window)[0]
    min_idx = argrelextrema(lows.values, np.less_equal, order=window)[0]
    
    # Cluster similar levels
    def cluster_levels(points):
        clusters = []
        for p in points:
            matched = False
            for c in clusters:
                if abs(p - c['mean'])/c['mean'] < tolerance:
                    c['points'].append(p)
                    c['mean'] = np.mean(c['points'])
                    matched = True
                    break
            if not matched:
                clusters.append({'points': [p], 'mean': p})
        return [c['mean'] for c in clusters if len(c['points']) >= min_touches]
    
    resistance = cluster_levels(highs.iloc[max_idx].tolist())
    support = cluster_levels(lows.iloc[min_idx].tolist())
    
    return sorted(support), sorted(resistance)
