import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(#f0f2f6, #ffffff);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Dashboard Controls")

# Stock symbol input
default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
selected_stock = st.sidebar.selectbox(
    "🔍 Select Stock Symbol:",
    default_stocks + ['Custom'],
    index=0
)

if selected_stock == 'Custom':
    custom_stock = st.sidebar.text_input("Enter custom stock symbol:", "AAPL")
    selected_stock = custom_stock.upper()

# Time period selection
time_periods = {
    "1 Day": "1d",
    "5 Days": "5d", 
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

selected_period = st.sidebar.selectbox(
    "📅 Select Time Period:",
    list(time_periods.keys()),
    index=4
)

# Chart type selection
chart_type = st.sidebar.selectbox(
    "📈 Select Chart Type:",
    ["Candlestick", "Line Chart", "Area Chart"],
    index=0
)

# Technical indicators
st.sidebar.subheader("📊 Technical Indicators")
show_ma = st.sidebar.checkbox("Moving Averages", True)
show_volume = st.sidebar.checkbox("Volume", True)
show_bollinger = st.sidebar.checkbox("Bollinger Bands", False)

@st.cache_data
def get_stock_data(symbol, period):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        info = stock.info
        return data, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

@st.cache_data
def calculate_technical_indicators(data):
    """Calculate technical indicators"""
    # Moving averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # Bollinger Bands
    data['BB_middle'] = data['Close'].rolling(window=20).mean()
    bb_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
    data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
    
    return data

# Fetch data
if selected_stock:
    with st.spinner(f'📡 Fetching data for {selected_stock}...'):
        stock_data, stock_info = get_stock_data(selected_stock, time_periods[selected_period])
    
    if stock_data is not None and not stock_data.empty:
        # Calculate technical indicators
        stock_data = calculate_technical_indicators(stock_data)
        
        # Display stock info
        if stock_info:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_price = stock_data['Close'].iloc[-1]
                st.metric(
                    "💰 Current Price", 
                    f"${current_price:.2f}",
                    delta=f"{((current_price - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2] * 100):.2f}%"
                )
            
            with col2:
                day_high = stock_data['High'].iloc[-1]
                st.metric("📈 Day High", f"${day_high:.2f}")
            
            with col3:
                day_low = stock_data['Low'].iloc[-1]
                st.metric("📉 Day Low", f"${day_low:.2f}")
            
            with col4:
                volume = stock_data['Volume'].iloc[-1]
                st.metric("📊 Volume", f"{volume:,.0f}")
        
        # Create main chart
        fig = make_subplots(
            rows=2 if show_volume else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[f'{selected_stock} Stock Price', 'Volume'] if show_volume else [f'{selected_stock} Stock Price'],
            row_width=[0.7, 0.3] if show_volume else [1]
        )
        
        # Main price chart
        if chart_type == "Candlestick":
            fig.add_trace(
                go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name="OHLC",
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444'
                ),
                row=1, col=1
            )
        elif chart_type == "Line Chart":
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )
        else:  # Area Chart
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    fill='tonexty',
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=1),
                    fillcolor='rgba(31, 119, 180, 0.3)'
                ),
                row=1, col=1
            )
        
        # Add technical indicators
        if show_ma and len(stock_data) > 20:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['MA20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
            
            if len(stock_data) > 50:
                fig.add_trace(
                    go.Scatter(
                        x=stock_data.index,
                        y=stock_data['MA50'],
                        mode='lines',
                        name='MA50',
                        line=dict(color='red', width=1)
                    ),
                    row=1, col=1
                )
        
        if show_bollinger and len(stock_data) > 20:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['BB_upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash')
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['BB_lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128, 128, 128, 0.1)'
                ),
                row=1, col=1
            )
        
        # Add volume chart
        if show_volume:
            colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in stock_data.iterrows()]
            fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f'{selected_stock} - {selected_period}',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        if show_volume:
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        fig.update_xaxes(rangeslider_visible=False)
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional metrics and analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Key Statistics")
            if stock_info:
                stats_data = {
                    "Market Cap": stock_info.get('marketCap', 'N/A'),
                    "P/E Ratio": stock_info.get('trailingPE', 'N/A'),
                    "52 Week High": stock_info.get('fiftyTwoWeekHigh', 'N/A'),
                    "52 Week Low": stock_info.get('fiftyTwoWeekLow', 'N/A'),
                    "Dividend Yield": stock_info.get('dividendYield', 'N/A'),
                    "Beta": stock_info.get('beta', 'N/A')
                }
                
                for key, value in stats_data.items():
                    if isinstance(value, (int, float)) and key == "Market Cap":
                        value = f"${value:,.0f}" if value != 'N/A' else 'N/A'
                    elif isinstance(value, (int, float)) and key in ["52 Week High", "52 Week Low"]:
                        value = f"${value:.2f}" if value != 'N/A' else 'N/A'
                    elif isinstance(value, (int, float)) and key == "Dividend Yield":
                        value = f"{value*100:.2f}%" if value != 'N/A' else 'N/A'
                    elif isinstance(value, (int, float)):
                        value = f"{value:.2f}" if value != 'N/A' else 'N/A'
                    
                    st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("🔍 Price Analysis")
            
            # Calculate price changes
            price_change_1d = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2] * 100)
            
            if len(stock_data) >= 5:
                price_change_5d = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-6]) / stock_data['Close'].iloc[-6] * 100)
            else:
                price_change_5d = 0
                
            if len(stock_data) >= 20:
                price_change_20d = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-21]) / stock_data['Close'].iloc[-21] * 100)
            else:
                price_change_20d = 0
            
            st.write(f"**1 Day Change:** {price_change_1d:.2f}%")
            st.write(f"**5 Day Change:** {price_change_5d:.2f}%")
            st.write(f"**20 Day Change:** {price_change_20d:.2f}%")
            
            # Volatility
            volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
            st.write(f"**Annualized Volatility:** {volatility:.2f}%")
        
        # Recent data table
        st.subheader("📋 Recent Trading Data")
        recent_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10)
        recent_data = recent_data.round(2)
        st.dataframe(recent_data, use_container_width=True)
        
    else:
        st.error(f"❌ Could not fetch data for {selected_stock}. Please check the symbol and try again.")

# Footer
st.markdown("---")
st.markdown(
    "**📊 Stock Market Dashboard** | Built with Streamlit, Plotly & Yahoo Finance | "
    "⚠️ *This is for educational purposes only. Not financial advice.*"
)