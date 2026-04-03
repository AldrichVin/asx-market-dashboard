"""Volatility & Risk — Beta, Sharpe, drawdown, correlations."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, fetch_multiple_stocks, get_stock_name
from src.risk_metrics import (
    calculate_rolling_volatility, calculate_beta, calculate_sharpe_ratio,
    calculate_max_drawdown, calculate_correlation_matrix, calculate_daily_returns,
)
from src.ui import load_css, apply_chart_style, show_chart, page_header, NAVY, CHART_COLORS

st.set_page_config(page_title="Risk", layout="wide")
load_css()
page_header("Risk", "Volatility, drawdown, and correlation analysis.")

st.sidebar.markdown("#### Controls")
selected = st.sidebar.multiselect(
    "Stocks",
    list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "FMG.AX"],
    format_func=lambda x: f"{x.replace('.AX', '')} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()), index=3)

if not selected:
    st.info("Select at least one stock.")
    st.stop()

stock_data = fetch_multiple_stocks(selected, PERIOD_MAP[period])
benchmark = fetch_stock_data("^AXJO", PERIOD_MAP[period])

# Metrics table
st.subheader("Summary")
rows = []
for ticker, df in stock_data.items():
    beta = calculate_beta(df, benchmark) if not benchmark.empty else float("nan")
    rows.append({
        "Stock": get_stock_name(ticker),
        "Sharpe": round(calculate_sharpe_ratio(df), 2),
        "Beta": round(beta, 2),
        "Max DD": f"{calculate_max_drawdown(df):.1%}",
        "Volatility": f"{calculate_daily_returns(df).std() * 252**0.5:.1%}",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Rolling volatility
st.subheader("30-Day Rolling Volatility")
fig_vol = go.Figure()
for i, (ticker, df) in enumerate(stock_data.items()):
    vol = calculate_rolling_volatility(df, 30)
    fig_vol.add_trace(go.Scatter(
        x=vol.index, y=vol.values, name=get_stock_name(ticker),
        line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1.5),
    ))
apply_chart_style(fig_vol, 380)
fig_vol.update_yaxes(title_text="Annualised Volatility", tickformat=".0%")
show_chart(fig_vol)

# Drawdown
st.subheader("Drawdown")
fig_dd = go.Figure()
for i, (ticker, df) in enumerate(stock_data.items()):
    rets = calculate_daily_returns(df)
    cum = (1 + rets).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()
    fig_dd.add_trace(go.Scatter(
        x=dd.index, y=dd.values, name=get_stock_name(ticker),
        fill="tozeroy", line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1),
        fillcolor=f"rgba(30,58,95,{0.06 + i*0.02})",
    ))
apply_chart_style(fig_dd, 380)
fig_dd.update_yaxes(title_text="Drawdown", tickformat=".0%")
show_chart(fig_dd)

# Correlation
if len(stock_data) >= 2:
    st.subheader("Return Correlation")
    corr = calculate_correlation_matrix(stock_data)
    corr.index = [get_stock_name(t) for t in corr.index]
    corr.columns = [get_stock_name(t) for t in corr.columns]

    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="Blues",
        zmin=0, zmax=1,
    )
    apply_chart_style(fig_corr, 450)
    fig_corr.update_layout(coloraxis_showscale=False)
    show_chart(fig_corr)
