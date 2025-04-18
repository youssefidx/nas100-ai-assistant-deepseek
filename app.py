import streamlit as st
import pandas as pd
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy
from utils.plots import plot_trades, plot_equity_curve
from utils.download import get_table_download_link

st.set_page_config(page_title="NAS100 AI Trading Assistant", layout="wide", page_icon="📈")
st.title("📊 NAS100 AI Trading Assistant")

uploaded_file = st.file_uploader("Upload NAS100 CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["Datetime"], index_col="Datetime")
    st.subheader("Candlestick Preview")
    st.line_chart(df["Close"])

    support, resistance = detect_zones(df)
    zones = (support, resistance)

    st.subheader("Detected Support & Resistance Zones")
    st.write("Support:", support)
    st.write("Resistance:", resistance)

    use_volume = st.checkbox("Use Volume for Entry Confirmation", value=True)
    session_start = pd.to_datetime("09:30:00").time()
    signals = generate_trade_signals(df, zones, use_volume=use_volume, session_start=session_start)

    if not signals.empty:
        st.subheader("Trade Signals")
        st.write(signals.head())
        fig1 = plot_trades(df, signals)
        st.pyplot(fig1)

        sl_pct = st.slider("Stop Loss %", 1.0, 2.5, 1.5)
        tp_pct = st.slider("Take Profit %", 3.0, 10.0, 5.0)
        result, equity = backtest_strategy(df, signals, sl_pct, tp_pct)

        st.subheader("Equity Curve")
        fig2 = plot_equity_curve(equity)
        st.pyplot(fig2)

        st.subheader("Performance")
        st.write(f"📈 Final Equity: ${equity[-1]:.2f}")
        st.write(f"✅ Total Trades: {len(equity)}")

        st.subheader("Download Trade Log")
        get_table_download_link(signals)
    else:
        st.warning("No trade signals detected.")
        
        # After signal generation
if not signals.empty:
    st.subheader("🔍 Filtered Signals (Top 20)")
    st.dataframe(
        signals.head(20).style.format({
            'Price': '{:.2f}'
        }),
        height=400
    )
    
    # Backtest and display
    result = backtest_strategy(df, signals.set_index('Datetime'), sl_pct, tp_pct)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Final Equity", f"${result['stats']['final_equity']}")
        st.metric("🎯 Win Rate", result['stats']['win_rate'])
    with col2:
        st.metric("📊 Total Trades", result['stats']['total_trades'])
        st.metric("⚠️ Max Drawdown", result['stats']['max_drawdown'])
    
    st.area_chart(pd.DataFrame({'Equity': result['equity']))
    
    # After detect_zones()
st.subheader("📊 Key Levels")

supp, res = detect_zones(df)
support = sorted(list(set(round(s, 2) for s in supp if s > 0))[:10]  # Top 10
resistance = sorted(list(set(round(r, 2) for r in res if r > 0))[-10:]  # Top 10

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🛑 Support")
    st.json(support)
with col2:
    st.markdown("#### 🚀 Resistance") 
    st.json(resistance)
