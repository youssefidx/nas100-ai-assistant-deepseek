import streamlit as st
import base64

def get_table_download_link(df, filename="trade_log.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'
    return st.markdown(href, unsafe_allow_html=True)