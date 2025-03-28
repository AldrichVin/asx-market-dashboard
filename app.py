"""ASX Market Analytics Dashboard — Main Entry Point"""
import streamlit as st

st.set_page_config(
    page_title="ASX Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ASX Market Analytics Dashboard")
st.markdown("""
Interactive analytics for Australian Securities Exchange (ASX) stocks.
Explore stock prices, volatility, sector performance, forecasting signals,
and portfolio simulation using live market data.

---

### Pages

- **Stock Explorer** — Price charts, moving averages, volume analysis
- **Volatility & Risk** — Rolling volatility, beta, Sharpe ratio, drawdown
- **Sector Performance** — ASX sector comparison and relative strength
- **Forecasting** — Moving average crossover signals and trend projections
- **Portfolio Simulator** — Backtest custom portfolio allocations vs ASX200

---

*Data sourced from Yahoo Finance via yfinance API. Not financial advice.*
""")

st.sidebar.success("Select a page above to begin analysis.")
