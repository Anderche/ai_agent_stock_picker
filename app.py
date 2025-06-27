import streamlit as st
import pandas as pd
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from utils import get_sector_etf, get_sector_constituents, get_comparative_metrics

st.set_page_config(page_title="AI Investment Agent", layout="wide")
st.title("📈 AI Investment Agent as Sector Analyst")
st.caption("Enter a stock, analyze its valuation, then compare it against its sector peers.")

openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")


if openai_api_key:
    assistant = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        tools=[YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True
        )],
        show_tool_calls=True,
        description="You are an investment analyst analyzing stock valuations and sector comparisons.",
        instructions=[
            "Format your response using markdown. Use tables for sector-wide metrics when appropriate."
        ],
    )

    stock_symbol = st.text_input("📊 Enter a stock symbol (e.g. AAPL, MSFT)").strip().upper()

    if stock_symbol:
        with st.spinner("Detecting sector and fetching data..."):
            sector_etf, sector_name = get_sector_etf(stock_symbol)

            if not sector_etf:
                st.error("Could not determine sector. Try another stock.")
            else:
                st.success(f"{stock_symbol} belongs to the '{sector_name}' sector (ETF: {sector_etf})")

                df = get_sector_constituents(sector_etf)
                comp_df = get_comparative_metrics(df)

                # Highlight user's stock
                if stock_symbol in comp_df.index:
                    st.markdown(f"### 📈 Valuation Report for {stock_symbol}")
                    st.dataframe(comp_df.loc[[stock_symbol]])
                else:
                    st.warning("User stock not found in sector constituents")

                st.markdown("### 🧮 Sector-wide Valuation Comparison")
                st.dataframe(comp_df)

                st.markdown("### 🧠 AI Report")
                query = (
                    f"Compare {stock_symbol} with all its peers in the {sector_name} sector ETF ({sector_etf}). "
                    "Identify if it's underpriced or overpriced using valuation metrics like P/E, P/B, and PEG."
                )
                response = assistant.run(query, stream=False)
                st.markdown(response.content)
