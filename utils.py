import yfinance as yf
import pandas as pd
import time
import random

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

# Known sector mappings for common stocks (fallback only)
known_sectors = {
    "TSLA": "Consumer Discretionary",
    "AAPL": "Technology", 
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "GOOG": "Technology",
    "AMZN": "Consumer Discretionary",
    "NVDA": "Technology",
    "META": "Communication Services",
    "NFLX": "Communication Services",
    "ADBE": "Technology",
    "CRM": "Technology",
    "ORCL": "Technology",
    "INTC": "Technology",
    "AMD": "Technology",
    "QCOM": "Technology",
    "CSCO": "Technology",
    "IBM": "Technology",
    "TXN": "Technology",
    "AVGO": "Technology",
    "MU": "Technology",
    "HD": "Consumer Discretionary",
    "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary",
    "SBUX": "Consumer Discretionary",
    "LOW": "Consumer Discretionary",
    "TJX": "Consumer Discretionary",
    "BKNG": "Consumer Discretionary",
    "MAR": "Consumer Discretionary",
    "HLT": "Consumer Discretionary",
    "YUM": "Consumer Discretionary",
    "CMG": "Consumer Discretionary",
    "TGT": "Consumer Discretionary",
    "COST": "Consumer Staples",
    "WMT": "Consumer Staples",
    "ULTA": "Consumer Discretionary",
    "ROST": "Consumer Discretionary",
    "LVS": "Consumer Discretionary"
}

def get_sector_etf(symbol, max_retries=3):
    """
    Get sector ETF for a stock symbol with retry logic for rate limiting
    """
    for attempt in range(max_retries):
        try:
            # Add longer random delay to avoid rate limiting
            if attempt > 0:
                time.sleep(random.uniform(3, 6))  # Longer delay between retries
            else:
                time.sleep(random.uniform(1, 2))  # Initial delay
            
            ticker = yf.Ticker(symbol)
            
            # Try multiple methods to get sector information
            sector = None
            
            # Method 1: Try info attribute
            try:
                info = ticker.info
                sector = info.get("sector", "")
            except:
                pass
            
            # Method 2: Try fast_info if available
            if not sector:
                try:
                    fast_info = ticker.fast_info
                    sector = getattr(fast_info, 'sector', '')
                except:
                    pass
            
            # Method 3: Try getting basic info
            if not sector:
                try:
                    # Try a more basic approach
                    basic_info = ticker.get_info()
                    sector = basic_info.get("sector", "")
                except:
                    pass
            
            # Check if we got valid sector information
            if not sector:
                print(f"Warning: No sector found for {symbol} on attempt {attempt + 1}")
                continue
                
            # Map sector to ETF
            for etf, sector_name in spdr_map.items():
                if sector.lower() in sector_name.lower():
                    return etf, sector_name
            
            # If no exact match, try partial matching
            for etf, sector_name in spdr_map.items():
                if any(word in sector.lower() for word in sector_name.lower().split()):
                    return etf, sector_name
                    
            print(f"Warning: Could not map sector '{sector}' for {symbol} to any ETF")
            return None, None
            
        except Exception as e:
            print(f"Error getting sector for {symbol} (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to get sector for {symbol} after {max_retries} attempts")
                # Last resort: use known sector mapping
                if symbol in known_sectors:
                    sector = known_sectors[symbol]
                    for etf, sector_name in spdr_map.items():
                        if sector.lower() in sector_name.lower():
                            print(f"Using fallback sector mapping for {symbol}: {sector}")
                            return etf, sector_name
                return None, None
            continue
    
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

def get_comparative_metrics(symbols, max_retries=2):
    rows = []
    for s in symbols:
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(random.uniform(0.5, 1.5))
                
                t = yf.Ticker(s)
                info = t.info
                
                # Check if we got valid data
                if not info or len(info) < 5:  # Basic check for valid response
                    print(f"Warning: Invalid data for {s} on attempt {attempt + 1}")
                    if attempt == max_retries - 1:
                        continue
                    else:
                        continue
                
                rows.append({
                    "Ticker": s,
                    "P/E": info.get("trailingPE"),
                    "P/B": info.get("priceToBook"),
                    "PEG": info.get("pegRatio"),
                    "Forward P/E": info.get("forwardPE"),
                    "Market Cap": info.get("marketCap"),
                    "Analyst Rating": info.get("recommendationMean")
                })
                break  # Success, move to next symbol
                
            except Exception as e:
                print(f"Error getting data for {s} (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    print(f"Failed to get data for {s} after {max_retries} attempts")
                    continue
                else:
                    continue
    
    df = pd.DataFrame(rows)
    
    # Only drop rows that are missing the Ticker column (essential)
    df = df.dropna(subset=['Ticker'])
    
    # Check if DataFrame is empty or has no data after dropna
    if df.empty or "Ticker" not in df.columns:
        return pd.DataFrame()  # Return empty DataFrame
    
    df = df.set_index("Ticker")
    return df.sort_values("P/E", na_position='last')  # Put NaN values at the end

