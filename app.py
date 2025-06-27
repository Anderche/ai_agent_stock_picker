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
