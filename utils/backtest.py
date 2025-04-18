import pandas as pd
import numpy as np

def backtest_strategy(df, signals, sl_pct=1.5, tp_pct=5.0):
    if signals.empty:
        return {"equity": [10000], "stats": {"error": "No signals provided"}}
    
    equity = 10000
    results = [equity]
    wins = 0
    
    signals = signals.sort_index()
    
    for dt, row in signals.iterrows():
        try:
            idx = df.index.get_loc(dt)
            entry = row['Price']
            is_buy = row['Signal'] == 'Buy'
            
            sl = entry * (1 - sl_pct/100) if is_buy else entry * (1 + sl_pct/100)
            tp = entry * (1 + tp_pct/100) if is_buy else entry * (1 - tp_pct/100)
            
            for j in range(idx, min(idx+100, len(df))):
                high, low = df['High'].iloc[j], df['Low'].iloc[j]
                
                if is_buy:
                    if low <= sl: 
                        equity *= 0.985
                        break
                    elif high >= tp:
                        equity *= 1.05
                        wins += 1
                        break
                else:
                    if high >= sl:
                        equity *= 0.985
                        break
                    elif low <= tp:
                        equity *= 1.05
                        wins += 1
                        break
            
            results.append(equity)
        except:
            continue
    
    stats = {
        "final_equity": round(equity, 2),
        "total_trades": len(signals),
        "win_rate": f"{wins/max(1,len(signals)):.1%}",
        "max_drawdown": f"{(10000 - min(results))/100:.1f}%"
    }
    
    return {"equity": results, "stats": stats}
