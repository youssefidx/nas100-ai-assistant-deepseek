import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def detect_zones(df, window=20, min_touches=3):
    # Find swing points
    highs = df['High']
    lows = df['Low']
    
    # Get local maxima/minima
    max_idx = argrelextrema(highs.values, np.greater_equal, order=window)[0]
    min_idx = argrelextrema(lows.values, np.less_equal, order=window)[0]
    
    # Cluster levels
    def cluster_levels(points, tolerance=0.002):
        clusters = []
        for p in points:
            found = False
            for c in clusters:
                if abs(p - c['mean'])/c['mean'] < tolerance:
                    c['points'].append(p)
                    c['mean'] = np.mean(c['points'])
                    found = True
                    break
            if not found:
                clusters.append({'points': [p], 'mean': p})
        return [c['mean'] for c in clusters if len(c['points']) >= min_touches]
    
    resistance = cluster_levels(highs.iloc[max_idx].tolist())
    support = cluster_levels(lows.iloc[min_idx].tolist())
    
    return sorted(support), sorted(resistance)
