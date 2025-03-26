"""Fetch and cache ASX stock data from yfinance."""
import pandas as pd
import yfinance as yf
import streamlit as st
from pathlib import Path

ASX_STOCKS = {
    "BHP.AX": "BHP Group",
    "CBA.AX": "Commonwealth Bank",
    "CSL.AX": "CSL Limited",
    "NAB.AX": "National Australia Bank",
    "WBC.AX": "Westpac Banking",
    "ANZ.AX": "ANZ Banking Group",
    "WES.AX": "Wesfarmers",
    "MQG.AX": "Macquarie Group",
    "FMG.AX": "Fortescue Metals",
    "WOW.AX": "Woolworths Group",
    "TLS.AX": "Telstra",
    "RIO.AX": "Rio Tinto",
    "WDS.AX": "Woodside Energy",
    "ALL.AX": "Aristocrat Leisure",
    "COL.AX": "Coles Group",
    "STO.AX": "Santos",
    "JHX.AX": "James Hardie",
    "REA.AX": "REA Group",
    "TCL.AX": "Transurban",
    "GMG.AX": "Goodman Group",
}

ASX_SECTORS = {
    "Financials": ["CBA.AX", "NAB.AX", "WBC.AX", "ANZ.AX", "MQG.AX"],
    "Mining": ["BHP.AX", "RIO.AX", "FMG.AX"],
    "Healthcare": ["CSL.AX"],
    "Energy": ["WDS.AX", "STO.AX"],
    "Consumer": ["WES.AX", "WOW.AX", "COL.AX"],
    "Technology": ["REA.AX", "ALL.AX"],
    "Telecom": ["TLS.AX"],
    "Infrastructure": ["TCL.AX", "GMG.AX", "JHX.AX"],
}

PERIOD_MAP = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}


@st.cache_data(ttl=3600)
def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        return pd.DataFrame()
    df.index = df.index.tz_localize(None)
    return df


@st.cache_data(ttl=3600)
def fetch_multiple_stocks(tickers: list[str], period: str = "1y") -> dict[str, pd.DataFrame]:
    result = {}
    for ticker in tickers:
        data = fetch_stock_data(ticker, period)
        if not data.empty:
            result[ticker] = data
    return result


def get_stock_name(ticker: str) -> str:
    return ASX_STOCKS.get(ticker, ticker.replace(".AX", ""))
