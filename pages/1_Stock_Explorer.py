"""Stock Explorer — Price charts, moving averages, and volume."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, get_stock_name
from src.technical_indicators import add_moving_averages, add_bollinger_bands

st.set_page_config(page_title="Stock Explorer", page_icon="📊", layout="wide")
st.title("Stock Explorer")

# Sidebar controls
st.sidebar.header("Settings")
selected_tickers = st.sidebar.multiselect(
    "Select Stocks",
    options=list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX"],
    format_func=lambda x: f"{x} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Time Period", list(PERIOD_MAP.keys()), index=3)
show_sma = st.sidebar.multiselect("Moving Averages", [20, 50, 200], default=[20, 50])
show_volume = st.sidebar.checkbox("Show Volume", value=True)
chart_type = st.sidebar.radio("Chart Type", ["Line", "Candlestick"])

if not selected_tickers:
    st.warning("Please select at least one stock.")
    st.stop()

# Fetch and display data for each stock
for ticker in selected_tickers:
    df = fetch_stock_data(ticker, PERIOD_MAP[period])

    if df.empty:
        st.error(f"No data available for {ticker}")
        continue

    df = add_moving_averages(df, show_sma)
    name = get_stock_name(ticker)

    # Create chart
    fig = make_subplots(
        rows=2 if show_volume else 1, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3] if show_volume else [1],
        vertical_spacing=0.05,
    )

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="OHLC",
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], name="Close",
            line=dict(color="#1f77b4", width=2),
        ), row=1, col=1)

    # Moving averages
    colors = {20: "#ff7f0e", 50: "#2ca02c", 200: "#d62728"}
    for w in show_sma:
        col_name = f"SMA_{w}"
        if col_name in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col_name], name=f"SMA {w}",
                line=dict(color=colors.get(w, "#888"), width=1, dash="dash"),
            ), row=1, col=1)

    # Volume
    if show_volume:
        vol_colors = ["#2ca02c" if c >= o else "#d62728"
                      for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"], name="Volume",
            marker_color=vol_colors, opacity=0.5,
        ), row=2, col=1)

    fig.update_layout(
        title=f"{name} ({ticker}) — {period}",
        height=600 if show_volume else 450,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="Price (AUD)", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # Key metrics
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    change = (latest["Close"] - prev["Close"]) / prev["Close"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Close", f"${latest['Close']:.2f}", f"{change:.2%}")
    col2.metric("High", f"${latest['High']:.2f}")
    col3.metric("Low", f"${latest['Low']:.2f}")
    col4.metric("Volume", f"{latest['Volume']:,.0f}")

    st.divider()
