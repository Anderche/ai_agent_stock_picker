import yfinance as yf
import pandas as pd

spdr_map = {
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples", "XLE": "Energy",
    "XLF": "Financials", "XLV": "Health Care", "XLI": "Industrials", "XLB": "Materials",
    "XLK": "Technology", "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Communication Services"
}

# Predefined sector constituents as fallback
sector_constituents = {
    "XLK": ["AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "NFLX", "ADBE", "CRM", "ORCL", "INTC", "AMD", "QCOM", "CSCO", "IBM", "TXN", "AVGO", "MU"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "MAR", "HLT", "YUM", "CMG", "TGT", "COST", "WMT", "ULTA", "ROST", "TJX", "LVS"],
    "XLP": ["PG", "KO", "PEP", "WMT", "COST", "PM", "MO", "CL", "EL", "GIS", "K", "HSY", "SJM", "CAG", "KMB", "HRL", "SJM", "CPB", "KHC", "MDLZ"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "PXD", "VLO", "MPC", "PSX", "OXY", "HAL", "BKR", "DVN", "KMI", "WMB", "OKE", "ET", "ENB", "TRP", "PBA"],
    "XLF": ["BRK-B", "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SPGI", "CB", "AXP", "USB", "PNC", "TFC", "COF", "SCHW", "AIG", "MET", "PRU", "ALL"],
    "XLV": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "MRK", "ABT", "DHR", "BMY", "AMGN", "GILD", "CVS", "CI", "ANTM", "HUM", "CNC", "WBA", "REGN", "BIIB", "VRTX"],
    "XLI": ["UNP", "HON", "UPS", "RTX", "CAT", "DE", "LMT", "BA", "GE", "MMM", "EMR", "ETN", "ITW", "NSC", "FDX", "CSX", "WM", "RSG", "WM", "PCAR"],
    "XLB": ["LIN", "APD", "FCX", "NEM", "DOW", "DD", "ECL", "BLL", "NUE", "VMC", "ALB", "CTVA", "IFF", "LYB", "SHW", "BLL", "VMC", "NUE", "FCX", "NEM"],
    "XLU": ["NEE", "DUK", "SO", "D", "AEP", "SRE", "XEL", "WEC", "DTE", "ED", "EIX", "PEG", "AEE", "CMS", "CNP", "ATO", "LNT", "BKH", "NI", "OGE"],
    "XLRE": ["AMT", "PLD", "CCI", "EQIX", "PSA", "O", "DLR", "WELL", "SPG", "EQR", "AVB", "MAA", "VICI", "ARE", "BXP", "KIM", "REG", "FRT", "UDR", "ESS"],
    "XLC": ["META", "GOOGL", "GOOG", "NFLX", "CMCSA", "CHTR", "VZ", "T", "TMUS", "DISH", "PARA", "WBD", "FOX", "NWSA", "NWS", "LBRDK", "LBRDA", "LSXMK", "LSXMA", "FWONK"]
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
        if holdings is not None and not holdings.empty:
            symbols = holdings['symbol'].dropna().unique().tolist()
            return symbols
        else:
            return sector_constituents.get(etf, [])
    except Exception as e:
        return sector_constituents.get(etf, [])

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
        except Exception as e:
            continue
    
    df = pd.DataFrame(rows)
    
    # Only drop rows that are missing the Ticker column (essential)
    df = df.dropna(subset=['Ticker'])
    
    # Check if DataFrame is empty or has no data after dropna
    if df.empty or "Ticker" not in df.columns:
        return pd.DataFrame()  # Return empty DataFrame
    
    df = df.set_index("Ticker")
    return df.sort_values("P/E", na_position='last')  # Put NaN values at the end

