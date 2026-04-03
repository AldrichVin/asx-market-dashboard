"""Stock Explorer — Price charts with technical overlays."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, get_stock_name
from src.technical_indicators import add_moving_averages
from src.ui import load_css, apply_chart_style, show_chart, page_header, NAVY, NAVY_LIGHT, GRAY, GREEN, RED

st.set_page_config(page_title="Stocks", layout="wide")
load_css()
page_header("Stocks", "Price action and technical overlays for ASX equities.")

# Sidebar
st.sidebar.markdown("#### Controls")
selected_tickers = st.sidebar.multiselect(
    "Stocks",
    list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX"],
    format_func=lambda x: f"{x.replace('.AX', '')} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()), index=3)
show_sma = st.sidebar.multiselect("Moving Averages", [20, 50, 200], default=[20, 50])
show_volume = st.sidebar.checkbox("Volume", value=True)
chart_type = st.sidebar.radio("Chart", ["Line", "Candlestick"])

if not selected_tickers:
    st.info("Select at least one stock from the sidebar.")
    st.stop()

sma_colors = {20: NAVY_LIGHT, 50: "#D97B4A", 200: "#8B5CD9"}

for ticker in selected_tickers:
    df = fetch_stock_data(ticker, PERIOD_MAP[period])
    if df.empty:
        st.warning(f"No data for {ticker}")
        continue

    df = add_moving_averages(df, show_sma)
    name = get_stock_name(ticker)

    fig = make_subplots(
        rows=2 if show_volume else 1, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25] if show_volume else [1],
        vertical_spacing=0.04,
    )

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="OHLC",
            increasing_line_color=GREEN, decreasing_line_color=RED,
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], name="Close",
            line=dict(color=NAVY, width=2),
        ), row=1, col=1)

    for w in show_sma:
        col_name = f"SMA_{w}"
        if col_name in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col_name], name=f"SMA {w}",
                line=dict(color=sma_colors.get(w, GRAY), width=1, dash="dot"),
            ), row=1, col=1)

    if show_volume:
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"], name="Volume",
            marker_color=NAVY, opacity=0.15, showlegend=False,
        ), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, showlegend=True)
    apply_chart_style(fig, height=520 if show_volume else 400)
    fig.update_layout(title=f"{name}  ({ticker})")
    fig.update_yaxes(title_text="AUD", row=1, col=1)

    show_chart(fig)

    # Metrics
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    change = (latest["Close"] - prev["Close"]) / prev["Close"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Close", f"${latest['Close']:.2f}", f"{change:+.2%}")
    c2.metric("High", f"${latest['High']:.2f}")
    c3.metric("Low", f"${latest['Low']:.2f}")
    c4.metric("Volume", f"{latest['Volume']:,.0f}")

    st.markdown("---")
