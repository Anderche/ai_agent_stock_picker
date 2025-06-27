# AI Investment Agent with Sector Comparison

This app uses an LLM agent to analyze a user-entered stock, compare it with peers in its SPDR sector ETF, and generate a markdown-based investment report.

## Features
- Accepts any stock ticker (e.g., AAPL)
- Detects sector and corresponding SPDR ETF (e.g., XLK for Technology)
- Fetches all constituents of that sector ETF
- Compares P/E, P/B, PEG, Forward P/E, Analyst Rating
- Highlights whether user’s stock is underpriced or overpriced
- Streams a markdown investment report from GPT-4o


