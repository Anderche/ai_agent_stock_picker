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
SECTOR_CONSTITUENTS_DATA = {
    "XLK": ["AAPL", "AVGO", "CRM", "CSCO", "IBM", "INTU", "MSFT", "NVDA", "ORCL", "PLTR"],
    "XLY": ["AMZN", "BKNG", "HD", "LOW", "MCD", "NKE", "ORLY", "SBUX", "TJX", "TSLA"],
    "XLP": ["CL", "COST", "KMB", "KO", "MDLZ", "MO", "PEP", "PG", "PM", "WMT"],
    "XLE": ["COP", "CVX", "EOG", "KMI", "MPC", "OKE", "PSX", "SLB", "WMB", "XOM"],
    "XLF": ["AXP", "BAC", "BRK-B", "GS", "JPM", "MA", "PGR", "SPGI", "V", "WFC"],
    "XLV": ["ABBV", "ABT", "AMGN", "BSX", "ISRG", "JNJ", "LLY", "MRK", "TMO", "UNH"],
    "XLI": ["ADP", "BA", "CAT", "DE", "GE", "GEV", "HON", "RTX", "UBER", "UNP"],
    "XLB": ["APD", "CTVA", "DD", "ECL", "FCX", "LIN", "MLM", "NEM", "SHW", "VMC"],
    "XLU": ["AEP", "CEG", "D", "DUK", "EXC", "NEE", "PEG", "SO", "SRE", "VST"],
    "XLRE": ["AMT", "CBRE", "CCI", "DLR", "EQIX", "O", "PLD", "PSA", "SPG", "WELL"],
    "XLC": ["CHTR", "DIS", "EA", "GOOG", "GOOGL", "LYV", "META", "NFLX", "T", "TTWO"]
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
                
            # Try exact match first
            for etf, name in spdr_map.items():
                if sector.lower() == name.lower():
                    return etf, name
            
            # Try partial match
            for etf, name in spdr_map.items():
                if sector.lower() in name.lower() or name.lower() in sector.lower():
                    return etf, name
            
            # Try common sector name variations
            sector_variations = {
                "technology": "XLK",
                "tech": "XLK",
                "consumer discretionary": "XLY",
                "consumer cyclical": "XLY",  # Yahoo Finance uses "Consumer Cyclical"
                "consumer staples": "XLP",
                "consumer defensive": "XLP",  # Yahoo Finance uses "Consumer Defensive"
                "energy": "XLE",
                "financials": "XLF",
                "financial services": "XLF",
                "health care": "XLV",
                "healthcare": "XLV",
                "industrials": "XLI",
                "materials": "XLB",
                "utilities": "XLU",
                "real estate": "XLRE",
                "communication services": "XLC",
                "communications": "XLC"
            }
            
            sector_lower = sector.lower()
            if sector_lower in sector_variations:
                etf = sector_variations[sector_lower]
                name = spdr_map[etf]
                return etf, name
                    
            print(f"Warning: Could not map sector '{sector}' for {symbol} to any ETF")
            return None, None
            
        except Exception as e:
            print(f"Error getting sector for {symbol} (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to get sector for {symbol} after {max_retries} attempts")
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
            return SECTOR_CONSTITUENTS_DATA.get(etf, [])
    except Exception as e:
        return SECTOR_CONSTITUENTS_DATA.get(etf, [])

def sector_constituents(etf):
    """
    Alias for get_sector_constituents for backward compatibility
    """
    return get_sector_constituents(etf)

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

