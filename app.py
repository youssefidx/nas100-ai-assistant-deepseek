import streamlit as st
import pandas as pd
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy
from utils.plots import plot_trades

st.set_page_config(page_title="NAS100 AI Trading Assistant", layout="wide", page_icon="📈")
st.title("📊 NAS100 AI Trading Assistant")

# Sample data download in sidebar
with st.sidebar:
    st.markdown("### Sample Data")
    sample_data = pd.DataFrame({
        'Datetime': pd.date_range(start='2024-01-01', periods=5, freq='5T'),
        'Open': [18000, 18005, 18010, 18015, 18020],
        'High': [18005, 18010, 18015, 18020, 18025],
        'Low': [17995, 18000, 18005, 18010, 18015],
        'Close': [18003, 18008, 18013, 18018, 18023],
        'Volume': [1000, 1200, 800, 1500, 2000]
    })
    st.download_button(
        label="⬇️ Download Sample CSV",
        data=sample_data.to_csv(index=False),
        file_name="nas100_sample_data.csv",
        mime="text/csv"
    )

uploaded_file = st.file_uploader("Upload NAS100 CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Datetime"], index_col="Datetime")
        
        # Data validation
        required_cols = {'Open', 'High', 'Low', 'Close'}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Missing required columns. Your data needs: {required_cols}")
            st.stop()

        st.subheader("📈 Candlestick Preview")
        st.line_chart(df["Close"])

        # Support/Resistance Display
        st.subheader("📊 Key Levels")
        supp, res = detect_zones(df)
        support = sorted(list(set(round(s, 2) for s in supp if s > 0))[:10]
        resistance = sorted(list(set(round(r, 2) for r in res if r > 0))[-10:]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🛑 Support")
            st.json(support)
        with col2:
            st.markdown("#### 🚀 Resistance") 
            st.json(resistance)

        use_volume = st.checkbox("Use Volume for Entry Confirmation", value=True)
        session_start = pd.to_datetime("09:30:00").time()
        signals = generate_trade_signals(df, (support, resistance), use_volume=use_volume, session_start=session_start)

        if not signals.empty:
            st.subheader("🔍 Filtered Signals (Top 20)")
            st.dataframe(
                signals.head(20).style.format({'Price': '{:.2f}'}),
                height=400
            )
            
            fig = plot_trades(df, signals)
            st.pyplot(fig)

            sl_pct = st.slider("Stop Loss %", 1.0, 5.0, 1.5)
            tp_pct = st.slider("Take Profit %", 1.0, 10.0, 5.0)
            
            result = backtest_strategy(df, signals.set_index('Datetime'), sl_pct, tp_pct)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Final Equity", f"${result['stats']['final_equity']}")
                st.metric("🎯 Win Rate", result['stats']['win_rate'])
            with col2:
                st.metric("📊 Total Trades", result['stats']['total_trades'])
                st.metric("⚠️ Max Drawdown", result['stats']['max_drawdown'])
            
            st.area_chart(pd.DataFrame({'Equity': result['equity']}))
            
            st.download_button(
                "📥 Download Trade Log",
                signals.to_csv(index=False),
                "trade_signals.csv"
            )
        else:
            st.warning("No trade signals detected.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please check: 1) CSV format 2) Required columns 3) Datetime format")
