import pandas as pd

def backtest_strategy(df, signals, sl_pct, tp_pct):
    # Input validation
    if not isinstance(signals, pd.DataFrame):
        raise ValueError("Signals must be a pandas DataFrame")
        
    if 'Datetime' not in signals.columns or 'Price' not in signals.columns or 'Signal' not in signals.columns:
        raise ValueError("Signals DataFrame must contain 'Datetime', 'Price', and 'Signal' columns")

    # Ensure proper indexing
    if not isinstance(signals.index, pd.DatetimeIndex):
        signals = signals.set_index('Datetime')
    
    # Check alignment with price data
    missing_dates = signals.index[~signals.index.isin(df.index)]
    if len(missing_dates) > 0:
        raise ValueError(f"{len(missing_dates)} signal timestamps missing in price data")

    # Backtest logic
    equity = 10000
    balance = equity
    results = []

    for signal in signals.itertuples():
        entry_price = signal.Price
        is_buy = signal.Signal == 'Buy'

        sl_price = entry_price * (1 - sl_pct / 100) if is_buy else entry_price * (1 + sl_pct / 100)
        tp_price = entry_price * (1 + tp_pct / 100) if is_buy else entry_price * (1 - tp_pct / 100)

        for i in range(df.index.get_loc(signal.Index), len(df)):
            high = df['High'].iloc[i]
            low = df['Low'].iloc[i]

            if is_buy:
                if low <= sl_price:
                    pnl = -sl_pct
                    break
                elif high >= tp_price:
                    pnl = tp_pct
                    break
            else:
                if high >= sl_price:
                    pnl = -sl_pct
                    break
                elif low <= tp_price:
                    pnl = tp_pct
                    break
        balance *= (1 + pnl / 100)
        results.append(balance)

    return pd.DataFrame({"Equity": results}), results
