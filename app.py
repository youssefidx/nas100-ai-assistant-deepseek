import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy

# Config
st.set_page_config(layout="wide", page_title="NAS100 Trading Assistant")
st.title("📈 NAS100 AI Trading Assistant")

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

# Data Upload
uploaded_file = st.file_uploader("Upload Market Data (CSV)", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Datetime"], index_col="Datetime")
        
        # Data Validation
        if not {'Open','High','Low','Close'}.issubset(df.columns):
            st.error("❌ Missing required price columns")
            st.stop()

        # Generate Trading Signals
        support, resistance = detect_zones(df)
        signals = generate_trade_signals(df, (support, resistance))
        
        if not signals.empty:
            # Interactive Price Chart
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                             vertical_spacing=0.05, row_heights=[0.7, 0.3])
            
            # Candlesticks
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Price"
            ), row=1, col=1)
            
            # Trading Signals
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

            # Backtest Configuration
            st.subheader("⚙️ Backtest Parameters")
            col1, col2 = st.columns(2)
            with col1:
                sl_pct = st.slider("Stop Loss %", 0.5, 5.0, 1.5, step=0.1)
            with col2:
                tp_pct = st.slider("Take Profit %", 0.5, 10.0, 3.0, step=0.1)
            
            # Run Backtest
            result = backtest_strategy(df, signals.set_index('Datetime'), sl_pct, tp_pct)
            
            # Performance Dashboard
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
            
            # Equity Curve Visualization
            st.subheader("📈 Equity Curve")
            eq_df = pd.DataFrame({
                'Equity': result['equity'],
                'Drawdown': [100*(1 - x/max(result['equity'][:i+1])) 
                            for i, x in enumerate(result['equity'])]
            })
            
            eq_fig = make_subplots(specs=[[{"secondary_y": True}]])
            eq_fig.add_trace(go.Scatter(
                x=eq_df.index, y=eq_df['Equity'],
                name="Equity", line=dict(color='#4e79a7')
            ), secondary_y=False)
            eq_fig.add_trace(go.Bar(
                x=eq_df.index, y=eq_df['Drawdown'],
                name="Drawdown", marker=dict(color='#e15759', opacity=0.3)
            ), secondary_y=True)
            eq_fig.update_layout(
                height=400,
                yaxis_title="Equity ($)",
                yaxis2=dict(title="Drawdown %", range=[0, 100])
            )
            st.plotly_chart(eq_fig, use_container_width=True)
            
            # Signals Table
            st.subheader("🔍 Trade Signals")
            st.dataframe(
                signals.style.format({'Price': '{:.2f}'})
                .applymap(lambda x: 'color: green' if x == 'Buy' else 'color: red', 
                         subset=['Signal']),
                height=400
            )
            
            # Data Export
            st.download_button(
                "📥 Export Signals as CSV",
                signals.to_csv(index=False),
                "nas100_signals.csv"
            )
            
        else:
            st.warning("⚠️ No trade signals generated with current parameters")
            
    except Exception as e:
        st.error(f"❌ Processing Error: {str(e)}")
