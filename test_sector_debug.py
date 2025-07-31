#!/usr/bin/env python3

import yfinance as yf
from utils import get_sector_etf, spdr_map

# Test stocks from different sectors
test_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM", "XOM", "JNJ", "PG", "HD", "META"]

print("Testing sector ETF matching...")
print("=" * 50)

for stock in test_stocks:
    print(f"\nTesting {stock}:")
    try:
        # Get stock info directly
        ticker = yf.Ticker(stock)
        info = ticker.info
        sector = info.get("sector", "N/A")
        print(f"  Yahoo Finance sector: '{sector}'")
        
        # Test our function
        etf, name = get_sector_etf(stock)
        if etf:
            print(f"  ✅ Matched to: {etf} ({name})")
        else:
            print(f"  ❌ No match found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 50)
print("Available SPDR ETFs:")
for etf, name in spdr_map.items():
    print(f"  {etf}: {name}") 