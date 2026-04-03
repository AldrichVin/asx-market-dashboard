"""ASX Market Analytics Dashboard"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.ui import load_css, NAVY
from src.data_fetcher import fetch_stock_data, get_stock_name

st.set_page_config(
    page_title="ASX Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

st.title("ASX Market Analytics")
st.caption("Real-time analysis of Australian Securities Exchange equities.")

st.markdown("---")

# Live ASX200 snapshot
benchmark = fetch_stock_data("^AXJO", "5d")
if not benchmark.empty:
    latest = benchmark.iloc[-1]
    prev = benchmark.iloc[-2] if len(benchmark) > 1 else latest
    change = (latest["Close"] - prev["Close"]) / prev["Close"]

    c1, c2, c3 = st.columns(3)
    c1.metric("ASX 200", f"{latest['Close']:,.0f}", f"{change:+.2%}")
    c2.metric("Day High", f"{latest['High']:,.0f}")
    c3.metric("Day Low", f"{latest['Low']:,.0f}")

st.markdown("---")

st.markdown("""
Use the sidebar to navigate between analysis views.

- **Stocks** — Price charts with technical overlays
- **Risk** — Volatility, beta, and correlation analysis
- **Sectors** — Sector-level performance comparison
- **Signals** — Trend detection and projections
- **Portfolio** — Backtest custom allocations vs ASX 200
""")

st.caption("Data from Yahoo Finance. Not financial advice.")
