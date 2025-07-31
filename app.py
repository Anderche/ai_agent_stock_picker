import streamlit as st
import pandas as pd
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools
from utils import get_sector_etf, get_sector_constituents, get_comparative_metrics

st.set_page_config(page_title="AI Investment Agent", layout="wide")
st.title("📈 AI Investment Agent as Sector Analyst")
st.caption("Enter a stock, analyze its valuation, then compare it against its sector peers.")

# Model selection for Ollama
model_options = ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5"]
selected_model = st.selectbox("🤖 Select Ollama Model", model_options, index=0)

# Check if Ollama is running
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not responding. Please start Ollama first.")
        st.stop()
except Exception:
    st.error("❌ Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434")
    st.info("💡 To start Ollama, run: `ollama serve` in your terminal")
    st.stop()

# Initialize the agent with Ollama
assistant = Agent(
    model=Ollama(id=selected_model),
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        stock_fundamentals=True
    )],
    show_tool_calls=True,
    description="You are an investment analyst analyzing stock valuations and sector comparisons.",
    instructions=[
        "Format your response using markdown with the following structure:",
        "1. Start with a brief introduction comparing the stock to its sector peers",
        "2. Include a 'Valuation Metrics' section with a comparison table showing the stock vs sector ETF metrics",
        "3. Include an 'Analysis' section with bullet points explaining each metric (P/E, P/B, PEG ratios)",
        "4. End with a 'Conclusion' section summarizing whether the stock appears overvalued or undervalued",
        "Use tables for sector-wide metrics when appropriate.",
        "Always structure your response with clear markdown headers: ### Valuation Metrics, ### Analysis, ### Conclusion",
        "IMPORTANT: Your response must be a minimum of 800 words. Provide detailed analysis, explanations, and insights for each section."
    ],
)

stock_symbol = st.text_input("📊 Enter a stock symbol (e.g. AAPL, MSFT)").strip().upper()

if stock_symbol:
    with st.spinner("Detecting sector and fetching data..."):
        st.info(f"🔍 Step 1: Detecting sector for {stock_symbol}...")
        sector_etf, sector_name = get_sector_etf(stock_symbol)

        if not sector_etf:
            st.error("Could not determine sector. Try another stock.")
        else:
            st.success(f"{stock_symbol} belongs to the '{sector_name}' sector (ETF: {sector_etf})")

            st.info(f"🔍 Step 2: Fetching sector constituents for {sector_etf}...")
            df = get_sector_constituents(sector_etf)
            
            st.info(f"🔍 Step 3: Getting comparative metrics for {len(df)} stocks...")
            comp_df = get_comparative_metrics(df)

            # Check if we got any data
            if comp_df.empty:
                st.error("Could not retrieve sector data. Please try again later.")
            else:
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


