# ASX Market Analytics Dashboard

Interactive Streamlit dashboard for Australian Securities Exchange (ASX) stock analysis featuring price exploration, volatility metrics, sector comparison, technical forecasting, and portfolio backtesting — all using live market data.

## Features

### 1. Stock Explorer
- Candlestick and line charts for 20+ ASX stocks
- Configurable moving averages (SMA 20, 50, 200)
- Volume overlay with green/red coloring
- Real-time price metrics

### 2. Volatility & Risk
- 30-day rolling annualized volatility
- Beta calculation vs ASX200 index
- Sharpe ratio comparison table
- Maximum drawdown analysis
- Return correlation heatmap

### 3. Sector Performance
- ASX sector return comparison (Financials, Mining, Healthcare, Energy, etc.)
- Cumulative sector returns over time
- Individual stock performance within sectors

### 4. Forecasting
- Moving average crossover signals (Golden Cross / Death Cross)
- RSI (Relative Strength Index) with overbought/oversold zones
- Linear regression trend projection with confidence bands
- Configurable forecast horizon (30-180 days)

### 5. Portfolio Simulator
- Custom stock allocation with adjustable weights
- Historical backtest against ASX200 benchmark
- Portfolio metrics: Sharpe ratio, max drawdown, annualized return
- Cumulative return comparison charts

## ASX Stocks Covered

BHP, CBA, CSL, NAB, WBC, ANZ, WES, MQG, FMG, WOW, TLS, RIO, WDS, ALL, COL, STO, JHX, REA, TCL, GMG

## Tech Stack

- **Streamlit** — Interactive web dashboard framework
- **Plotly** — Interactive charts (candlestick, scatter, heatmap)
- **yfinance** — Live market data from Yahoo Finance
- **pandas / numpy** — Data processing
- **scikit-learn** — Linear regression forecasting
- **scipy** — Statistical calculations

## Project Structure

```
asx-market-dashboard/
├── app.py                          # Main entry point
├── pages/
│   ├── 1_Stock_Explorer.py
│   ├── 2_Volatility_Risk.py
│   ├── 3_Sector_Performance.py
│   ├── 4_Forecasting.py
│   └── 5_Portfolio_Simulator.py
├── src/
│   ├── data_fetcher.py             # yfinance API wrapper with caching
│   ├── technical_indicators.py     # SMA, Bollinger, RSI, MA crossovers
│   ├── risk_metrics.py             # Beta, Sharpe, volatility, drawdown
│   └── portfolio.py                # Backtest engine and portfolio metrics
├── .streamlit/config.toml          # Dark theme configuration
└── requirements.txt
```

## Quick Start

```bash
git clone https://github.com/AldrichVin/asx-market-dashboard.git
cd asx-market-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

## Deploy

Deploy for free on [Streamlit Community Cloud](https://share.streamlit.io/):

1. Push repo to GitHub
2. Go to share.streamlit.io
3. Connect repo and select `app.py`
4. Deploy

*Data sourced from Yahoo Finance. Not financial advice.*
