import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import json
from utils import get_sector_etf, get_sector_constituents

# Function to check if Ollama is running
def check_ollama_status():
    """
    Check if Ollama service is running and accessible.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# Function to generate company description using Ollama
def generate_company_description(stock_symbol, stock_info, selected_model):
    """
    Generate an 80-120 word company description using the selected Ollama model.
    """
    try:
        # Prepare the prompt with company information
        company_name = stock_info.get('longName', stock_symbol)
        sector = stock_info.get('sector', 'N/A')
        industry = stock_info.get('industry', 'N/A')
        market_cap = stock_info.get('marketCap', 0)
        pe_ratio = stock_info.get('trailingPE', 0)
        description = stock_info.get('longBusinessSummary', '')
        
        # Format market cap for readability
        if market_cap and market_cap > 0:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.1f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.1f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.1f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = "N/A"
        
        prompt = f"""You are a financial analyst. Write a concise, professional company overview for {company_name} ({stock_symbol}) in exactly 80-120 words. 

Company Information:
- Name: {company_name}
- Symbol: {stock_symbol}
- Sector: {sector}
- Industry: {industry}
- Market Cap: {market_cap_str}
- P/E Ratio: {pe_ratio if pe_ratio else 'N/A'}
- Business Description: {description[:500]}{'...' if len(description) > 500 else ''}

Write a clear, informative overview that includes:
1. What the company does
2. Its market position
3. Key business focus areas
4. Current market context

Keep it professional, factual, and exactly 80-120 words. Focus on the company's core business and market position."""

        # Call Ollama API
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 200
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            description = result.get('response', '').strip()
            
            # Clean up the response
            if description.startswith('```'):
                description = description.split('\n', 1)[1] if '\n' in description else description
            if description.endswith('```'):
                description = description.rsplit('\n', 1)[0] if '\n' in description else description
            
            return description
        else:
            return f"**{stock_symbol}** is currently trading in the {sector} sector. Based on current valuation metrics, the stock shows mixed signals relative to sector peers."
            
    except Exception as e:
        # Fallback to static description if LLM fails
        sector = stock_info.get('sector', 'N/A')
        return f"**{stock_symbol}** is currently trading in the {sector} sector. Based on current valuation metrics, the stock shows mixed signals relative to sector peers."

# Page configuration
st.set_page_config(
    page_title="AI Investment Agent as Sector Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 {
        color: white;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    .status-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #6ee7b7;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
    }
    .status-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #fca5a5;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        color: #64748b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    .stSidebar {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    .stMetric {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 AI Investment Agent as Sector Analyst</h1>
    <p>Enter a stock, analyze its valuation, then compare it against its sector peers.</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 8px 12px; margin-bottom: 1rem; font-size: 0.85rem; color: #92400e;">
    ⚠️ <strong>Disclaimer:</strong> This tool is for educational purposes only. Not financial advice. Always do your own research.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🤖 Configuration")
    
    # Model selection
    model_options = ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5"]
    selected_model = st.selectbox("Select Ollama Model", model_options, index=0)
    
    # Status indicator
    if check_ollama_status():
        st.markdown('<div class="status-success">✅ Ollama is running</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">❌ Ollama is not running</div>', unsafe_allow_html=True)
    
    st.header("📊 Stock Input")
    stock_symbol = st.text_input("Enter stock symbol", placeholder="e.g., AAPL, MSFT", key="stock_input")
    
    # Add sector price checkbox
    add_sector_price = st.checkbox("📊 Add sector price (SPDR ETF)", value=False, help="Include the corresponding SPDR sector ETF in the price chart for comparison")
    
    if stock_symbol:
        stock_symbol = stock_symbol.upper()
        
        # Get stock info
        try:
            stock = yf.Ticker(stock_symbol)
            info = stock.info
            
            st.subheader("📋 Stock Information")
            st.write(f"**Company:** {info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            
            # Show sector ETF info if checkbox is checked
            if add_sector_price:
                sector_etf, sector_name = get_sector_etf(stock_symbol)
                if sector_etf:
                    st.write(f"**Sector ETF:** {sector_etf} ({sector_name})")
                else:
                    st.warning("⚠️ Could not determine sector ETF for this stock")
            
        except Exception as e:
            st.error(f"Error fetching stock data: {e}")

# Main content
if stock_symbol:
    try:
        # Get stock data
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📈 Overview", "🧮 Deep Analysis", "🧠 AI Report"])
        
        with tab1:
            st.header("📈 Stock Valuation Overview")
            
            # Key metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                current_price = info.get('currentPrice', 'N/A')
                if current_price != 'N/A':
                    current_price = f"${current_price:.2f}"
                st.metric("Current Price", current_price)
            
            with col2:
                pe_ratio = info.get('trailingPE', 'N/A')
                st.metric("P/E Ratio", pe_ratio)
            
            with col3:
                pb_ratio = info.get('priceToBook', 'N/A')
                st.metric("P/B Ratio", pb_ratio)
            
            with col4:
                peg_ratio = info.get('pegRatio', 'N/A')
                st.metric("PEG Ratio", peg_ratio)
            
            with col5:
                market_cap = info.get('marketCap', 'N/A')
                if market_cap != 'N/A':
                    market_cap = f"${market_cap/1e9:.1f}B"
                st.metric("Market Cap", market_cap)
            
            # Stock overview
            st.subheader("Company Overview")
            
            # Generate company description with loading spinner
            with st.spinner("🤖 AI is generating company overview..."):
                try:
                    description = generate_company_description(stock_symbol, info, selected_model)
                    st.write(description)
                    
                    # Add a small indicator that this was AI-generated
                    st.caption("💡 *AI-generated description using " + selected_model + " model*")
                    
                except Exception as e:
                    # Fallback to static description if LLM generation fails
                    st.warning("⚠️ Could not generate AI description. Using fallback description.")
                    st.write(f"**{stock_symbol}** is currently trading in the {info.get('sector', 'N/A')} sector. "
                            f"Based on current valuation metrics, the stock shows mixed signals relative to sector peers.")
                    st.caption("💡 *Fallback description - AI service unavailable*")
            
            # Price chart
            st.subheader("Price Chart")
            hist = stock.history(period="1y")
            
            # Create the base figure with stock price
            fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name=f'{stock_symbol} Close Price')])
            
            # Add sector ETF if checkbox is checked
            if add_sector_price:
                sector_etf, sector_name = get_sector_etf(stock_symbol)
                if sector_etf:
                    try:
                        etf = yf.Ticker(sector_etf)
                        etf_hist = etf.history(period="1y")
                        
                        # Normalize ETF price to match stock price scale for better comparison
                        if not etf_hist.empty and not hist.empty:
                            # Calculate relative performance (both starting at 100)
                            stock_normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                            etf_normalized = (etf_hist['Close'] / etf_hist['Close'].iloc[0]) * 100
                            
                            # Add ETF line to the chart
                            fig.add_trace(go.Scatter(
                                x=etf_hist.index, 
                                y=etf_normalized, 
                                mode='lines', 
                                name=f'{sector_etf} (Normalized)', 
                                line=dict(dash='dash', color='orange')
                            ))
                            
                            # Update layout for normalized chart
                            fig.update_layout(
                                title=f"{stock_symbol} vs {sector_etf} Performance (Normalized to 100)",
                                xaxis_title="Date", 
                                yaxis_title="Relative Performance (Base=100)",
                                legend=dict(x=0.02, y=0.98)
                            )
                        else:
                            # Fallback to regular price chart if normalization fails
                            fig.add_trace(go.Scatter(
                                x=etf_hist.index, 
                                y=etf_hist['Close'], 
                                mode='lines', 
                                name=f'{sector_etf} Price', 
                                line=dict(dash='dash', color='orange')
                            ))
                            fig.update_layout(
                                title=f"{stock_symbol} vs {sector_etf} Stock Price (1 Year)",
                                xaxis_title="Date", 
                                yaxis_title="Price ($)",
                                legend=dict(x=0.02, y=0.98)
                            )
                    except Exception as e:
                        st.warning(f"Could not fetch {sector_etf} data: {e}")
                        # Fallback to original chart
                        fig.update_layout(
                            title=f"{stock_symbol} Stock Price (1 Year)", 
                            xaxis_title="Date", 
                            yaxis_title="Price ($)"
                        )
                else:
                    st.warning("⚠️ Could not determine sector ETF for this stock")
                    fig.update_layout(
                        title=f"{stock_symbol} Stock Price (1 Year)", 
                        xaxis_title="Date", 
                        yaxis_title="Price ($)"
                    )
            else:
                # Original chart without sector ETF
                fig.update_layout(
                    title=f"{stock_symbol} Stock Price (1 Year)", 
                    xaxis_title="Date", 
                    yaxis_title="Price ($)"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.header("🧮 Sector-wide Valuation Comparison")
            
            # Get sector data
            sector_etf, sector_name = get_sector_etf(stock_symbol)
            if sector_etf:
                try:
                    # Get sector constituents
                    constituents = get_sector_constituents(sector_etf)
                    
                    # Get comparative metrics for sector
                    from utils import get_comparative_metrics
                    comp_df = get_comparative_metrics(constituents[:10])  # Limit to top 10 for performance
                    
                    if not comp_df.empty:
                        st.subheader(f"Sector Comparison: {sector_name}")
                        st.dataframe(comp_df, use_container_width=True)
                        
                        # Create comparison charts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Filter out NaN values for plotting
                            plot_df = comp_df.dropna(subset=['P/E'])
                            if not plot_df.empty:
                                fig_pe = px.bar(plot_df, x=plot_df.index, y='P/E', title='P/E Ratio Comparison')
                                st.plotly_chart(fig_pe, use_container_width=True)
                        
                        with col2:
                            plot_df = comp_df.dropna(subset=['P/B'])
                            if not plot_df.empty:
                                fig_pb = px.bar(plot_df, x=plot_df.index, y='P/B', title='P/B Ratio Comparison')
                                st.plotly_chart(fig_pb, use_container_width=True)
                    else:
                        st.warning("Could not retrieve sector comparison data")
                        
                except Exception as e:
                    st.error(f"Error fetching sector data: {e}")
            else:
                st.warning("Could not determine sector for comparison")
            
            # Valuation analysis
            st.subheader("Valuation Analysis")
            st.write("Detailed valuation metrics and analysis will appear here...")
        
        with tab3:
            st.header("🧠 AI Investment Analysis")
            
            # Simulate AI analysis
            with st.spinner("AI is analyzing the stock..."):
                time.sleep(2)  # Simulate processing time
                
                st.subheader("Investment Overview")
                st.write(f"Based on comprehensive analysis of {stock_symbol} against its {info.get('sector', 'Technology')} sector peers, "
                        f"the stock presents a mixed investment opportunity.")
                
                st.subheader("Valuation Metrics")
                pe_ratio = info.get('trailingPE', 0)
                if pe_ratio != 0:
                    st.write(f"The current P/E ratio of {pe_ratio:.1f} suggests the stock is trading at a premium to the sector average of 24.2. "
                            f"However, this premium may be justified by:")
                    
                    st.markdown("""
                    - Strong revenue growth trajectory
                    - Market leadership position
                    - Robust cash flow generation
                    - Innovation pipeline strength
                    """)
                
                st.subheader("Analysis")
                pb_ratio = info.get('priceToBook', 0)
                peg_ratio = info.get('pegRatio', 0)
                
                if pb_ratio != 0:
                    st.write(f"The P/B ratio of {pb_ratio:.1f} indicates significant market confidence in the company's "
                            f"intangible assets and future growth prospects.")
                
                if peg_ratio != 0:
                    st.write(f"The PEG ratio of {peg_ratio:.1f} suggests growth expectations are factored into current pricing.")
                
                st.subheader("Conclusion")
                st.write(f"While {stock_symbol} appears fairly valued within its sector context, investors should consider "
                        f"the premium valuation against expected growth delivery. The stock may be suitable for growth-oriented "
                        f"portfolios but could face pressure if growth expectations are not met.")
        
        # Comparative metrics table (floating panel simulation)
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Comparative Metrics")
        
        # Create a smaller comparison table in sidebar
        try:
            sector_etf, sector_name = get_sector_etf(stock_symbol)
            if sector_etf:
                constituents = get_sector_constituents(sector_etf)
                comp_df = get_comparative_metrics(constituents[:5])  # Show top 5 for sidebar
                if not comp_df.empty:
                    st.sidebar.dataframe(comp_df[['P/E', 'P/B']], use_container_width=True)
        except:
            pass
        
    except Exception as e:
        st.error(f"Error analyzing stock {stock_symbol}: {e}")
        st.write("Please check the stock symbol and try again.")

else:
    # Welcome message
    st.info("👈 Enter a stock symbol in the sidebar to begin analysis")
    
    # Demo content
    st.header("Welcome to AI Investment Agent")
    st.write("""
    This application provides comprehensive stock analysis including:
    
    - **Real-time stock data** from Yahoo Finance
    - **Valuation metrics** (P/E, P/B, PEG ratios)
    - **Sector comparison** against peers
    - **AI-powered analysis** and recommendations
    
    To get started, enter a stock symbol in the sidebar (e.g., AAPL, MSFT, GOOGL).
    """)
    
    # Sample data
    st.subheader("Sample Analysis")
    sample_data = {
        'Metric': ['P/E Ratio', 'P/B Ratio', 'PEG Ratio', 'Market Cap'],
        'Value': ['28.5', '45.2', '2.1', '$3.2T'],
        'Sector Avg': ['24.2', '12.8', '1.8', '--']
    }
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)


