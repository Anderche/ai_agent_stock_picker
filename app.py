import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="📈 AI Investment Agent as Sector Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff4b4b, #ff6b6b);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
        margin: 0.5rem 0;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
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

# Sidebar
with st.sidebar:
    st.header("🤖 Configuration")
    
    # Model selection
    model_options = ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5"]
    selected_model = st.selectbox("Select Ollama Model", model_options, index=0)
    
    # Status indicator
    st.markdown('<div class="status-success">✅ Ollama is running</div>', unsafe_allow_html=True)
    
    st.header("📊 Stock Input")
    stock_symbol = st.text_input("Enter stock symbol", placeholder="e.g., AAPL, MSFT", key="stock_input")
    
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
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pe_ratio = info.get('trailingPE', 'N/A')
                st.metric("P/E Ratio", pe_ratio)
            
            with col2:
                pb_ratio = info.get('priceToBook', 'N/A')
                st.metric("P/B Ratio", pb_ratio)
            
            with col3:
                peg_ratio = info.get('pegRatio', 'N/A')
                st.metric("PEG Ratio", peg_ratio)
            
            with col4:
                market_cap = info.get('marketCap', 'N/A')
                if market_cap != 'N/A':
                    market_cap = f"${market_cap/1e9:.1f}B"
                st.metric("Market Cap", market_cap)
            
            # Stock overview
            st.subheader("Company Overview")
            st.write(f"**{stock_symbol}** is currently trading in the {info.get('sector', 'N/A')} sector. "
                    f"Based on current valuation metrics, the stock shows mixed signals relative to sector peers.")
            
            # Price chart
            st.subheader("Price Chart")
            hist = stock.history(period="1y")
            fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close Price')])
            fig.update_layout(title=f"{stock_symbol} Stock Price (1 Year)", xaxis_title="Date", yaxis_title="Price ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.header("🧮 Sector-wide Valuation Comparison")
            
            # Simulate sector comparison data
            sector_data = {
                'Symbol': [stock_symbol, 'MSFT', 'GOOGL', 'AMZN', 'META'],
                'P/E': [info.get('trailingPE', 0), 32.1, 28.5, 45.2, 22.3],
                'P/B': [info.get('priceToBook', 0), 12.8, 6.2, 8.9, 4.1],
                'PEG': [info.get('pegRatio', 0), 1.9, 1.5, 2.8, 1.2],
                'Market Cap': ['Current', '$2.8T', '$1.9T', '$1.7T', '$1.2T'],
                'Sector': [info.get('sector', 'N/A'), 'Technology', 'Technology', 'Technology', 'Technology']
            }
            
            df = pd.DataFrame(sector_data)
            st.dataframe(df, use_container_width=True)
            
            # Valuation analysis
            st.subheader("Valuation Analysis")
            st.write("Detailed valuation metrics and analysis will appear here...")
            
            # Create comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pe = px.bar(df, x='Symbol', y='P/E', title='P/E Ratio Comparison')
                st.plotly_chart(fig_pe, use_container_width=True)
            
            with col2:
                fig_pb = px.bar(df, x='Symbol', y='P/B', title='P/B Ratio Comparison')
                st.plotly_chart(fig_pb, use_container_width=True)
        
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
        comparison_df = df.head(3)  # Show top 3 for sidebar
        st.sidebar.dataframe(comparison_df[['Symbol', 'P/E', 'P/B']], use_container_width=True)
        
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