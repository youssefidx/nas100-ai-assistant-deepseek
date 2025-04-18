import streamlit as st
import pandas as pd
import numpy as np
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="NAS100 AI Trading Assistant", layout="wide", page_icon="📈")
st.title("📊 NAS100 AI Trading Assistant")

# Custom CSS for better visuals
st.markdown("""
<style>
.metric-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f0f2f6;
    margin-bottom: 15px;
}
.positive {
    color: #00aa00;
}
.negative {
    color: #ff0000;
}
</style>
""", unsafe_allow_html=True)

# Sample data download
with st.sidebar:
    st.markdown("### 🧪 Sample Data")
    sample_data = pd.DataFrame({
        'Datetime': pd.date_range(start='2024-01-01', periods=100, freq='5T'),
        'Open': np.cumsum(np.random.uniform(-5, 5, 100)) + 18000,
        'High': np.cumsum(np.random.uniform(-5, 5, 100)) + 18005,
        'Low': np.cumsum(np.random.uniform(-5, 5, 100)) + 17995,
        'Close': np.cumsum(np.random.uniform(-5, 5, 100)) + 18000,
        'Volume': np.random.randint(500, 2000, 100)
    })
    st.download_button(
        label="⬇️ Download Sample CSV",
        data=sample_data.to_csv(index=False),
        file_name="nas100_sample_data.csv",
        mime="text/csv"
    )

# Main app
uploaded_file = st.file_uploader("📤 Upload NAS100 CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Datetime"], index_col="Datetime")
        
        # Data validation
        required_cols = {'Open', 'High', 'Low', 'Close'}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Missing required columns. Needed: {required_cols}")
            st.stop()

        # Price chart
        st.subheader("📈 Price Chart with Signals")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        ), row=1, col=1)

        # Support/Resistance
        support, resistance = detect_zones(df)
        
        for level in support:
            fig.add_hline(y=level, line_dash="dot", 
                         line_color="green", opacity=0.5,
                         annotation_text=f"S {level:.1f}", 
                         annotation_position="bottom right",
                         row=1, col=1)
        
        for level in resistance:
            fig.add_hline(y=level, line_dash="dot", 
                         line_color="red", opacity=0.5,
                         annotation_text=f"R {level:.1f}", 
                         annotation_position="top right",
                         row=1, col=1)

        # Volume
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Volume",
            marker_color='rgba(100, 100, 200, 0.6)'
        ), row=2, col=1)

        fig.update_layout(height=600, showlegend=False, 
                         xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Generate signals
        use_volume = st.checkbox("Use Volume Confirmation", value=True)
        signals = generate_trade_signals(df, (support, resistance), use_volume=use_volume)

        if not signals.empty:
            # Backtest configuration
            st.subheader("⚙️ Backtest Parameters")
            col1, col2 = st.columns(2)
            with col1:
                sl_pct = st.slider("Stop Loss %", 0.5, 5.0, 1.5, step=0.1)
            with col2:
                tp_pct = st.slider("Take Profit %", 0.5, 10.0, 3.0, step=0.1)

            # Run backtest
            result = backtest_strategy(df, signals.set_index('Datetime'), sl_pct, tp_pct)
            
            # Performance metrics
            st.subheader("📊 Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            final_equity = result['stats']['final_equity']
            equity_change = (final_equity - 10000) / 100
            equity_class = "positive" if equity_change >= 0 else "negative"
            
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <h3>Final Equity</h3>
                    <h2 class="{equity_class}">${final_equity:,.2f}</h2>
                    <small>{equity_change:+.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <h3>Win Rate</h3>
                    <h2>{result['stats']['win_rate']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <h3>Total Trades</h3>
                    <h2>{result['stats']['total_trades']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-box">
                    <h3>Max Drawdown</h3>
                    <h2 class="negative">{result['stats']['max_drawdown']}</h2>
                </div>
                """, unsafe_allow_html=True)

            # Equity curve
            st.subheader("💰 Equity Curve")
            equity_df = pd.DataFrame({
                'Equity': result['equity'],
                'Drawdown': [100*(1 - x/max(result['equity'][:i+1])) for i, x in enumerate(result['equity'])]
            })
            
            fig_eq = make_subplots(specs=[[{"secondary_y": True}]])
            fig_eq.add_trace(
                go.Scatter(
                    x=equity_df.index,
                    y=equity_df['Equity'],
                    name="Equity",
                    line=dict(color='#4e79a7')
                ),
                secondary_y=False
            )
            fig_eq.add_trace(
                go.Bar(
                    x=equity_df.index,
                    y=equity_df['Drawdown'],
                    name="Drawdown",
                    marker=dict(color='#e15759', opacity=0.3)
                ),
                secondary_y=True
            )
            fig_eq.update_layout(
                height=400,
                yaxis=dict(title="Equity ($)", side="left"),
                yaxis2=dict(title="Drawdown %", side="right", range=[0, 100])
            )
            st.plotly_chart(fig_eq, use_container_width=True)

            # Trade signals table
            st.subheader("🔍 Trade Signals")
            signals['Date'] = signals['Datetime'].dt.date
            st.dataframe(
                signals[['Datetime', 'Signal', 'Price', 'Type']]
                .style.format({'Price': '{:.2f}'})
                .applymap(lambda x: 'color: green' if x == 'Buy' else 'color: red', 
                         subset=['Signal']),
                height=400,
                use_container_width=True
            )

            # Download
            st.download_button(
                "📥 Download Trade Log",
                signals.to_csv(index=False),
                "trade_signals.csv"
            )
        else:
            st.warning("⚠️ No trade signals detected with current parameters")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please check: 1) Data format 2) Date ranges 3) Missing values")
