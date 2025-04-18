import matplotlib.pyplot as plt

def plot_trades(df, signals):
    plt.figure(figsize=(14, 6))
    plt.plot(df['Close'], label='Price', alpha=0.5)
    
    buys = signals[signals['Signal'] == 'Buy']
    sells = signals[signals['Signal'] == 'Sell']
    
    plt.scatter(buys['Datetime'], buys['Price'], marker='^', color='g', label='Buy')
    plt.scatter(sells['Datetime'], sells['Price'], marker='v', color='r', label='Sell')
    
    plt.title("Trade Signals")
    plt.legend()
    plt.grid()
    return plt
