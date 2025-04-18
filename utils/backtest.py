import pandas as pd
import numpy as np

def backtest_strategy(df, signals, sl_pct=1.5, tp_pct=5.0):
    if signals.empty:
        return {"equity": [10000], "stats": {
            "final_equity": 10000,
            "total_trades": 0,
            "win_rate": "0.0%",
            "max_drawdown": "0.0%"
        }}
    
    initial_equity = 10000
    equity = initial_equity
    results = [equity]
    wins = 0
    drawdowns = []
    current_peak = initial_equity

    signals = signals.sort_index()
    
    for dt, row in signals.iterrows():
        try:
            idx = df.index.get_loc(dt)
            entry = row['Price']
            is_buy = row['Signal'] == 'Buy'
            
            # Position sizing (risk 2% per trade)
            position_size = (equity * 0.02) / (entry * (sl_pct/100))
            
            sl = entry * (1 - sl_pct/100) if is_buy else entry * (1 + sl_pct/100)
            tp = entry * (1 + tp_pct/100) if is_buy else entry * (1 - tp_pct/100)
            
            for j in range(idx, min(idx+100, len(df))):
                current_low = df['Low'].iloc[j]
                current_high = df['High'].iloc[j]
                
                if is_buy:
                    if current_low <= sl:
                        pnl = -sl_pct
                        break
                    elif current_high >= tp:
                        pnl = tp_pct
                        wins += 1
                        break
                else:
                    if current_high >= sl:
                        pnl = -sl_pct
                        break
                    elif current_low <= tp:
                        pnl = tp_pct
                        wins += 1
                        break
            
            # Update equity with proper position sizing
            equity += (equity * (pnl/100))
            results.append(equity)
            
            # Track drawdowns
            if equity > current_peak:
                current_peak = equity
            drawdowns.append((current_peak - equity)/current_peak)
            
        except Exception as e:
            continue
    
    max_drawdown = max(drawdowns) * 100 if drawdowns else 0
    
    stats = {
        "final_equity": round(equity, 2),
        "total_trades": len(signals),
        "win_rate": f"{wins/max(1,len(signals)):.1%}",
        "max_drawdown": f"{max_drawdown:.1f}%"
    }
    
    return {"equity": results, "stats": stats}
