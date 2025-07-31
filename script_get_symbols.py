import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log script start
logger.info("Starting ETF holdings fetch script")

etfs = ['XLK','XLY','XLP','XLE','XLF','XLV','XLI','XLB','XLU','XLRE','XLC']
all_holdings = {}

logger.info(f"Processing {len(etfs)} ETFs: {', '.join(etfs)}")

for i, ticker in enumerate(etfs, 1):
    logger.info(f"Processing ETF {i}/{len(etfs)}: {ticker}")
    
    fund = yf.Ticker(ticker)
    try:
        # Use funds_data.top_holdings instead of fund_holdings
        logger.debug(f"Fetching funds_data for {ticker}")
        h = fund.funds_data.top_holdings
        
        if h is not None and not h.empty:
            # Extract symbols from the index (which contains the ticker symbols)
            symbols = h.index.tolist()
            all_holdings[ticker] = sorted(symbols)
            logger.info(f"✅ Successfully fetched {len(symbols)} holdings for {ticker}")
            logger.debug(f"Sample holdings for {ticker}: {symbols[:5]}...")
        else:
            logger.warning(f"❗ No holdings data available for {ticker}")
    except Exception as e:
        logger.error(f"❗ Error fetching holdings for {ticker}: {str(e)}")
        logger.debug(f"Exception details for {ticker}:", exc_info=True)

# Create ticker_symbols directory if it doesn't exist
logger.info("Creating ticker_symbols directory")
os.makedirs('./ticker_symbols', exist_ok=True)

# Save as JSON file
output_file = './ticker_symbols/sector_etf_holdings.json'
logger.info(f"Saving data to {output_file}")

with open(output_file, 'w') as f:
    json.dump(all_holdings, f, indent=2)

logger.info("Data saved successfully")
logger.info(f"Total ETFs processed: {len(all_holdings)}")

for ticker, holdings in all_holdings.items():
    logger.info(f"{ticker}: {len(holdings)} holdings")

logger.info("Script completed successfully") 