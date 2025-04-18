import matplotlib.pyplot as plt

def plot_trades(df, signals):
    plt.figure(figsize=(14, 6))
    plt.plot(df['Close'], label='Close Price', alpha=0.5)

    for _, row in signals.iterrows():
        if row['Signal'] == 'Buy':
            plt.scatter(row['Datetime'], row['Price'], marker='^', color='green', label='Buy Signal')
        elif row['Signal'] == 'Sell':
            plt.scatter(row['Datetime'], row['Price'], marker='v', color='red', label='Sell Signal')

    plt.title("Trade Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    return plt

def plot_equity_curve(equity_curve):
    plt.figure(figsize=(10, 4))
    plt.plot(equity_curve, label='Equity Curve', color='blue')
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid()
    return plt