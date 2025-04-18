import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy

# Configuration
st.set_page_config(page_title="NAS100 AI Trading Assistant", layout="wide", page_icon="📈")
st.title("📊 NAS100 AI Trading Assistant")

# Custom CSS
st.markdown("""
<style>
.metric-card {
    padding: 15px;
    border-radius: 10px;
    background: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
.profit { color: #00aa00; }
.loss { color: #ff0000; }
</style>
""", unsafe_allow_html=True)

# Sample Data
with st.sidebar:
    st.markdown("### 📁 Sample Data")
    sample_data = pd.DataFrame({
        'Datetime': pd.date_range(start='2024-01-01', periods=100, freq='5T'),
        'Open': np.linspace(18000, 18200, 100),
        'High': np.linspace(18005, 18205, 100),
        'Low': np.linspace(17995, 18195, 100),
        'Close': np.linspace(18000, 18200, 100),
        'Volume': np.random.randint(1000, 5000, 100)
    })
    st.download_button(
        "⬇️ Download Sample Data",
        sample_data.to_csv(index=False),
        "nas100_sample.csv"
    )

# Main App Logic
uploaded_file = st.file_uploader("Upload NAS100 Data (CSV)", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Datetime"], index_col="Datetime")
        
        # Data Validation
        if not {'Open','High','Low','Close'}.issubset(df.columns):
            st.error("Missing required price columns")
            st.stop()

        # Generate Levels and Signals
        support, resistance = detect_zones(df)
        signals = generate_trade_signals(df, (support, resistance))
        
        # Visualizations
        if not signals.empty:
            # Price Chart
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                             vertical_spacing=0.05, row_heights=[0.7, 0.3])
            
            # Candlesticks
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Price"
            ), row=1, col=1)
            
            # Signals
            buys = signals[signals['Signal'] == 'Buy']
            sells = signals[signals['Signal'] == 'Sell']
            fig.add_trace(go.Scatter(
                x=buys['Datetime'], y=buys['Price'],
                mode='markers', name='Buy',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=sells['Datetime'], y=sells['Price'],
                mode='markers', name='Sell',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ), row=1, col=1)
            
            # Volume
            fig.add_trace(go.Bar(
                x=df.index, y=df['Volume'],
                name="Volume", marker_color='rgba(100, 150, 200, 0.6)'
            ), row=2, col=1)
            
            fig.update_layout(height=600, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # Backtest
            st.subheader("⚙️ Backtest Configuration")
            sl, tp = st.slider("Stop Loss %", 0.5, 5.0, 1.5), st.slider("Take Profit %", 1.0, 10.0, 3.0)
            result = backtest_strategy(df, signals.set_index('Datetime'), sl, tp)
            
            # Metrics
            st.subheader("📊 Performance Metrics")
            cols = st.columns(4)
            metrics = [
                ("💰 Final Equity", f"${result['stats']['final_equity']:,.2f}", 
                 "profit" if result['stats']['final_equity'] >= 10000 else "loss"),
                ("🎯 Win Rate", result['stats']['win_rate'], None),
                ("📈 Total Trades", result['stats']['total_trades'], None),
                ("⚠️ Max Drawdown", result['stats']['max_drawdown'], "loss")
            ]
            
            for col, (title, value, style) in zip(cols, metrics):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{title}</h3>
                        <h2 class="{style if style else ''}">{value}</h2>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Equity Curve
            st.subheader("📈 Equity Curve")
            eq_fig = go.Figure()
            eq_fig.add_trace(go.Scatter(
                x=list(range(len(result['equity']))),
                y=result['equity'],
                fill='tozeroy',
                line=dict(color='#4e79a7')
            ))
            eq_fig.update_layout(height=400, yaxis_title="Equity ($)")
            st.plotly_chart(eq_fig, use_container_width=True)
            
            # Signals Table
            st.subheader("🔍 Trade Signals")
            st.dataframe(
                signals.style.format({'Price': '{:.2f}'})
                .applymap(lambda x: 'color: green' if x == 'Buy' else 'color: red', 
                         subset=['Signal']),
                height=400
            )
            
            # Download
            st.download_button(
                "📥 Export Signals",
                signals.to_csv(index=False),
                "trade_signals.csv"
            )
            
        else:
            st.warning("No trade signals generated with current parameters")
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
