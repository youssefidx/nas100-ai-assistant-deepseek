import pandas as pd
import numpy as np

def backtest_strategy(df, signals, sl_pct=1.5, tp_pct=3.0):
    if signals.empty:
        return {
            "equity": [10000],
            "stats": {
                "final_equity": 10000,
                "total_trades": 0,
                "win_rate": "0.0%",
                "max_drawdown": "0.0%"
            }
        }
    
    equity = 10000
    results = [equity]
    wins = 0
    peak = equity
    max_dd = 0
    
    for dt, row in signals.iterrows():
        try:
            idx = df.index.get_loc(dt)
            entry = row['Price']
            is_buy = row['Signal'] == 'Buy'
            
            # Risk 2% per trade
            risk_amount = equity * 0.02
            sl = entry * (1 - sl_pct/100) if is_buy else entry * (1 + sl_pct/100)
            tp = entry * (1 + tp_pct/100) if is_buy else entry * (1 - tp_pct/100)
            
            # Simulate trade
            for i in range(idx, min(idx+100, len(df))):
                current_low = df['Low'].iloc[i]
                current_high = df['High'].iloc[i]
                
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
            
            # Update equity
            equity += (equity * (pnl/100))
            results.append(equity)
            
            # Track drawdown
            if equity > peak:
                peak = equity
            current_dd = (peak - equity)/peak
            if current_dd > max_dd:
                max_dd = current_dd
                
        except:
            continue
    
    return {
        "equity": results,
        "stats": {
            "final_equity": round(equity, 2),
            "total_trades": len(signals),
            "win_rate": f"{wins/max(1,len(signals)):.1%}",
            "max_drawdown": f"{max_dd*100:.1f}%"
        }
    }
