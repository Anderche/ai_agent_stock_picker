import yfinance as yf
import pandas as pd

spdr_map = {
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples", "XLE": "Energy",
    "XLF": "Financials", "XLV": "Health Care", "XLI": "Industrials", "XLB": "Materials",
    "XLK": "Technology", "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Communication Services"
}


