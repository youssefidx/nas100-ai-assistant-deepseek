for signal in signals.itertuples():
    entry_price = signal.Price
    is_buy = signal.Signal == 'Buy'
    pnl = 0  # Initialize with default value

    # [SL/TP calculations remain the same]

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

    # Ensure pnl was set
    if pnl == 0:
        st.warning(f"No exit condition met for trade at {signal.Index}")
        continue
        
    balance *= (1 + pnl / 100)
    results.append(balance)
