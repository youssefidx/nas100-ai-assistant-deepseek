import streamlit as st
import pandas as pd
from utils.support_resistance import detect_zones
from utils.trade_signals import generate_trade_signals
from utils.backtest import backtest_strategy
from utils.plots import plot_trades, plot_equity_curve
from utils.download import get_table_download_link

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
            
            try:
                result, equity = backtest_strategy(df, signals, sl_pct, tp_pct)

                st.subheader("Equity Curve")
                fig2 = plot_equity_curve(equity)
                st.pyplot(fig2)

                st.subheader("Performance")
                st.write(f"📈 Final Equity: ${equity[-1]:.2f}")
                st.write(f"✅ Total Trades: {len(equity)}")

                st.subheader("Download Trade Log")
                get_table_download_link(signals)
            except Exception as e:
                st.error(f"⚠️ Backtesting failed: {str(e)}")
                st.info("Common issues: \n1. Missing price columns (OHLC) \n2. Signal format mismatch \n3. Invalid datetime index")
        else:
            st.warning("No trade signals detected.")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")