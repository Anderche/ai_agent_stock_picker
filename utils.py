import yfinance as yf
import pandas as pd

spdr_map = {
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples", "XLE": "Energy",
    "XLF": "Financials", "XLV": "Health Care", "XLI": "Industrials", "XLB": "Materials",
    "XLK": "Technology", "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Communication Services"
}

def get_sector_etf(symbol):
    try:
        info = yf.Ticker(symbol).info
        sector = info.get("sector", "")
        for etf, name in spdr_map.items():
            if sector.lower() in name.lower():
                return etf, name
        return None, None
    except Exception:
        return None, None

def get_sector_constituents(etf):
    try:
        etf_ticker = yf.Ticker(etf)
        holdings = etf_ticker.fund_holdings
        symbols = holdings['symbol'].dropna().unique().tolist()
        return symbols
    except Exception:
        return []

def get_comparative_metrics(symbols):
    rows = []
    for s in symbols:
        try:
            t = yf.Ticker(s)
            info = t.info
            rows.append({
                "Ticker": s,
                "P/E": info.get("trailingPE"),
                "P/B": info.get("priceToBook"),
                "PEG": info.get("pegRatio"),
                "Forward P/E": info.get("forwardPE"),
                "Market Cap": info.get("marketCap"),
                "Analyst Rating": info.get("recommendationMean")
            })
        except Exception:
            continue
    df = pd.DataFrame(rows).dropna()
    df = df.set_index("Ticker")
    return df.sort_values("P/E")

