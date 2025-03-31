"""Portfolio Simulator — Backtest custom allocations vs ASX200."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, fetch_multiple_stocks, get_stock_name
from src.portfolio import backtest_portfolio, calculate_portfolio_metrics
from src.risk_metrics import calculate_daily_returns

st.set_page_config(page_title="Portfolio Simulator", page_icon="💼", layout="wide")
st.title("Portfolio Simulator")

st.markdown("""
Build a custom portfolio of ASX stocks and backtest its performance against the ASX200 index.
Adjust allocation weights and see how your portfolio would have performed historically.
""")

# Sidebar: Stock selection
st.sidebar.header("Portfolio Configuration")
selected = st.sidebar.multiselect(
    "Select Stocks (2-8)",
    list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX", "WES.AX"],
    format_func=lambda x: f"{x} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Backtest Period", list(PERIOD_MAP.keys()), index=3)
initial = st.sidebar.number_input("Initial Investment ($)", 1000, 1000000, 10000, step=1000)

if len(selected) < 2:
    st.warning("Select at least 2 stocks to build a portfolio.")
    st.stop()

# Allocation sliders
st.subheader("Allocation Weights")
st.markdown("Adjust the weight for each stock. Weights will be normalized to 100%.")

cols = st.columns(min(len(selected), 4))
weights = {}
for i, ticker in enumerate(selected):
    col = cols[i % len(cols)]
    name = get_stock_name(ticker)
    weights[ticker] = col.slider(
        f"{name}",
        min_value=0, max_value=100, value=100 // len(selected),
        key=f"weight_{ticker}",
    )

total_weight = sum(weights.values())
if total_weight == 0:
    st.error("Total weight cannot be zero.")
    st.stop()

# Show normalized weights
norm_weights = {k: v / total_weight for k, v in weights.items()}
weight_display = pd.DataFrame({
    "Stock": [get_stock_name(t) for t in norm_weights],
    "Ticker": list(norm_weights.keys()),
    "Weight": [f"{w:.1%}" for w in norm_weights.values()],
})
st.dataframe(weight_display, use_container_width=True, hide_index=True)

# Fetch data and run backtest
stock_data = fetch_multiple_stocks(selected, PERIOD_MAP[period])
benchmark = fetch_stock_data("^AXJO", PERIOD_MAP[period])

if not stock_data:
    st.error("Unable to fetch stock data.")
    st.stop()

portfolio_df = backtest_portfolio(stock_data, norm_weights, initial)

if portfolio_df.empty:
    st.error("Insufficient data for backtesting.")
    st.stop()

# Portfolio metrics
st.subheader("Performance Metrics")
metrics = calculate_portfolio_metrics(portfolio_df)

if not benchmark.empty:
    bench_returns = calculate_daily_returns(benchmark)
    bench_total = (1 + bench_returns).cumprod().iloc[-1] - 1
    bench_annual = bench_returns.mean() * 252
    metrics["ASX200 Return"] = f"{bench_total:.2%}"

cols = st.columns(len(metrics))
for i, (key, val) in enumerate(metrics.items()):
    cols[i % len(cols)].metric(key, val)

# Performance chart
st.subheader("Portfolio Value Over Time")
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=portfolio_df.index, y=portfolio_df["Portfolio Value"],
    name="Your Portfolio", line=dict(color="#2ecc71", width=2),
    fill="tozeroy", fillcolor="rgba(46,204,113,0.1)",
))

# Benchmark
if not benchmark.empty:
    bench_returns = calculate_daily_returns(benchmark)
    bench_value = initial * (1 + bench_returns).cumprod()
    # Align dates
    common_dates = portfolio_df.index.intersection(bench_value.index)
    if len(common_dates) > 0:
        fig.add_trace(go.Scatter(
            x=common_dates, y=bench_value[common_dates],
            name="ASX200 Benchmark", line=dict(color="#e74c3c", width=2, dash="dash"),
        ))

fig.add_hline(y=initial, line_dash="dot", line_color="white", opacity=0.3,
              annotation_text=f"Initial: ${initial:,}")

fig.update_layout(
    yaxis_title="Portfolio Value ($)",
    template="plotly_dark",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig, use_container_width=True)

# Cumulative return comparison
st.subheader("Cumulative Return Comparison")
fig_cum = go.Figure()

fig_cum.add_trace(go.Scatter(
    x=portfolio_df.index, y=portfolio_df["Cumulative Return"],
    name="Portfolio", line=dict(color="#2ecc71"),
))

if not benchmark.empty and len(common_dates) > 0:
    bench_cum = (1 + bench_returns).cumprod() - 1
    fig_cum.add_trace(go.Scatter(
        x=common_dates, y=bench_cum[common_dates],
        name="ASX200", line=dict(color="#e74c3c", dash="dash"),
    ))

fig_cum.update_layout(
    yaxis_title="Cumulative Return",
    yaxis_tickformat=".0%",
    template="plotly_dark",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig_cum, use_container_width=True)

st.caption("*Not financial advice. Past performance does not guarantee future results.*")
