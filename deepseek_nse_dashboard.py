import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import numpy as np
from datetime import datetime, timedelta
import time

# Set page config
st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        color: #1f88e5;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9em;
        margin: 0;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 2px solid #1f88e5;
        padding-bottom: 0.5rem;
    }
    .stock-gain {
        color: #4caf50;
        font-weight: bold;
    }
    .stock-loss {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# List of F&O stocks (major ones)
FO_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS',
    'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'TITAN.NS',
    'SUNPHARMA.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'M&M.NS',
    'BAJFINANCE.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS',
    'TATASTEEL.NS', 'ADANIENT.NS', 'TECHM.NS', 'HCLTECH.NS', 'TATAMOTORS.NS',
    'DRREDDY.NS', 'BAJAJFINSV.NS', 'GRASIM.NS', 'CIPLA.NS', 'BRITANNIA.NS',
    'APOLLOHOSP.NS', 'DIVISLAB.NS', 'EICHERMOT.NS', 'BPCL.NS', 'TATACONSUM.NS'
]

# Sector mapping
SECTOR_MAPPING = {
    'RELIANCE.NS': 'Oil_Gas', 'TCS.NS': 'Technology', 'HDFCBANK.NS': 'Banking',
    'INFY.NS': 'Technology', 'HINDUNILVR.NS': 'FMCG', 'ICICIBANK.NS': 'Banking',
    'KOTAKBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 'BHARTIARTL.NS': 'Telecom',
    'ASIANPAINT.NS': 'Paint', 'ITC.NS': 'FMCG', 'LT.NS': 'Infrastructure',
    'AXISBANK.NS': 'Banking', 'MARUTI.NS': 'Automobile', 'TITAN.NS': 'Jewelry',
    'SUNPHARMA.NS': 'Pharma', 'ULTRACEMCO.NS': 'Cement', 'NESTLEIND.NS': 'FMCG',
    'WIPRO.NS': 'Technology', 'M&M.NS': 'Automobile', 'BAJFINANCE.NS': 'Finance',
    'ONGC.NS': 'Oil_Gas', 'NTPC.NS': 'Power', 'POWERGRID.NS': 'Power',
    'COALINDIA.NS': 'Mining', 'TATASTEEL.NS': 'Steel', 'ADANIENT.NS': 'Conglomerate',
    'TECHM.NS': 'Technology', 'HCLTECH.NS': 'Technology', 'TATAMOTORS.NS': 'Automobile',
    'DRREDDY.NS': 'Pharma', 'BAJAJFINSV.NS': 'Finance', 'GRASIM.NS': 'Textile',
    'CIPLA.NS': 'Pharma', 'BRITANNIA.NS': 'FMCG', 'APOLLOHOSP.NS': 'Healthcare',
    'DIVISLAB.NS': 'Pharma', 'EICHERMOT.NS': 'Automobile', 'BPCL.NS': 'Oil_Gas',
    'TATACONSUM.NS': 'FMCG'
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol, period="1d"):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        info = stock.info
        return data, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None, None

@st.cache_data(ttl=300)
def fetch_nifty_data():
    """Fetch NIFTY 50 data"""
    try:
        nifty = yf.Ticker("^NSEI")
        data = nifty.history(period="5d", interval="5m")
        return data
    except Exception as e:
        st.error(f"Error fetching NIFTY data: {e}")
        return None

@st.cache_data(ttl=300)
def fetch_all_fo_data():
    """Fetch data for all F&O stocks"""
    fo_data = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(FO_STOCKS):
        status_text.text(f'Loading {symbol}... ({i+1}/{len(FO_STOCKS)})')
        data, info = fetch_stock_data(symbol)
        if data is not None and not data.empty:
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            fo_data[symbol] = {
                'current_price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': data['Volume'].iloc[-1],
                'high': data['High'].iloc[-1],
                'low': data['Low'].iloc[-1],
                'sector': SECTOR_MAPPING.get(symbol, 'Others')
            }
        progress_bar.progress((i + 1) / len(FO_STOCKS))
    
    progress_bar.empty()
    status_text.empty()
    return fo_data

def create_nifty_chart(nifty_data):
    """Create NIFTY chart with volume"""
    if nifty_data is None or nifty_data.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('NIFTY 50', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=nifty_data.index,
            open=nifty_data['Open'],
            high=nifty_data['High'],
            low=nifty_data['Low'],
            close=nifty_data['Close'],
            name="NIFTY 50"
        ),
        row=1, col=1
    )
    
    # Add volume bars
    colors = ['red' if close < open else 'green' 
              for close, open in zip(nifty_data['Close'], nifty_data['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=nifty_data.index,
            y=nifty_data['Volume'],
            name="Volume",
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="NIFTY 50 Price & Volume",
        xaxis_rangeslider_visible=False,
        height=500
    )
    
    return fig

def create_heatmap(fo_data):
    """Create heatmap of F&O stocks"""
    if not fo_data:
        return None
    
    # Prepare data for heatmap
    symbols = list(fo_data.keys())
    changes = [fo_data[symbol]['change_pct'] for symbol in symbols]
    
    # Create a grid layout (8x5 for 40 stocks)
    rows = 8
    cols = 5
    
    # Pad with empty values if needed
    while len(symbols) < rows * cols:
        symbols.append("")
        changes.append(0)
    
    # Reshape into grid
    symbols_grid = np.array(symbols[:rows*cols]).reshape(rows, cols)
    changes_grid = np.array(changes[:rows*cols]).reshape(rows, cols)
    
    # Create text for each cell
    text_grid = []
    for i in range(rows):
        row_text = []
        for j in range(cols):
            if symbols_grid[i, j]:
                symbol_name = symbols_grid[i, j].replace('.NS', '')
                change_val = changes_grid[i, j]
                row_text.append(f"{symbol_name}<br>{change_val:.1f}%")
            else:
                row_text.append("")
        text_grid.append(row_text)
    
    # Fixed the colorbar configuration here
    fig = go.Figure(data=go.Heatmap(
        z=changes_grid,
        text=text_grid,
        texttemplate="%{text}",
        textfont={"size": 10},
        colorscale='RdYlGn',
        zmid=0,
        showscale=True,
        colorbar=dict(
            title=dict(text="Change %"),  # Fixed title configuration
            tickfont=dict(size=10)        # Use tickfont instead of titlefont
        )
    ))
    
    fig.update_layout(
        title="F&O Stocks Heatmap",
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        height=400
    )
    
    return fig

def create_sectors_chart(fo_data):
    """Create sectors performance chart"""
    if not fo_data:
        return None
    
    # Calculate sector performance
    sector_performance = {}
    for symbol, data in fo_data.items():
        sector = data['sector']
        if sector not in sector_performance:
            sector_performance[sector] = []
        sector_performance[sector].append(data['change_pct'])
    
    # Calculate average performance per sector
    sector_avg = {sector: np.mean(changes) for sector, changes in sector_performance.items()}
    
    # Sort by performance
    sorted_sectors = sorted(sector_avg.items(), key=lambda x: x[1], reverse=True)
    
    sectors = [item[0] for item in sorted_sectors]
    performances = [item[1] for item in sorted_sectors]
    colors = ['green' if perf > 0 else 'red' for perf in performances]
    
    fig = go.Figure(data=[
        go.Bar(
            y=sectors,
            x=performances,
            orientation='h',
            marker_color=colors,
            text=[f"{perf:.1f}%" for perf in performances],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Sector Performance",
        xaxis_title="Average Change %",
        height=400
    )
    
    return fig

def main():
    # Title
    st.markdown('<h1 class="main-header">🇮🇳 NSE F&O Dashboard</h1>', unsafe_allow_html=True)
    
    # Create columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Fetch data
    st.markdown('<div class="section-header">📊 Loading Market Data...</div>', unsafe_allow_html=True)
    
    # Fetch NIFTY data
    nifty_data = fetch_nifty_data()
    
    # Fetch F&O data
    fo_data = fetch_all_fo_data()
    
    if nifty_data is not None and fo_data:
        # Create layout
        chart_col, scan_col, dashboard_col = st.columns([2, 1, 1])
        
        # Charts Section
        with chart_col:
            st.markdown('<div class="section-header">📈 Charts</div>', unsafe_allow_html=True)
            nifty_chart = create_nifty_chart(nifty_data)
            if nifty_chart:
                st.plotly_chart(nifty_chart, use_container_width=True)
        
        # Scans Section
        with scan_col:
            st.markdown('<div class="section-header">🔍 Scans</div>', unsafe_allow_html=True)
            
            # Sort stocks by change percentage
            sorted_stocks = sorted(fo_data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            
            # Price Up
            st.markdown("**Price Up**")
            for symbol, data in sorted_stocks[:5]:
                name = symbol.replace('.NS', '')
                change_pct = data['change_pct']
                st.markdown(f'<span class="stock-gain">{name} +{change_pct:.1f}%</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Price Down
            st.markdown("**Price Down**")
            for symbol, data in sorted_stocks[-5:]:
                name = symbol.replace('.NS', '')
                change_pct = data['change_pct']
                st.markdown(f'<span class="stock-loss">{name} {change_pct:.1f}%</span>', unsafe_allow_html=True)
        
        # Dashboard Section
        with dashboard_col:
            st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
            
            # Calculate metrics
            total_stocks = len(fo_data)
            advancing = sum(1 for data in fo_data.values() if data['change_pct'] > 0)
            declining = total_stocks - advancing
            
            # Mock metrics (in real scenario, fetch from NSE API)
            put_call_ratio = 0.72
            vix = 16.2
            
            # Display metrics
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{put_call_ratio}</div>
                <div class="metric-label">Put/Call Ratio</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{vix}</div>
                <div class="metric-label">VIX</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{advancing}</div>
                <div class="metric-label">Advancing</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{declining}</div>
                <div class="metric-label">Declining</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Full width sections
        st.markdown('<div class="section-header">🎯 Heatmap</div>', unsafe_allow_html=True)
        heatmap = create_heatmap(fo_data)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)
        
        # Sectors and Adv-Dec
        sectors_col, advdec_col = st.columns(2)
        
        with sectors_col:
            st.markdown('<div class="section-header">🏢 Sectors</div>', unsafe_allow_html=True)
            sectors_chart = create_sectors_chart(fo_data)
            if sectors_chart:
                st.plotly_chart(sectors_chart, use_container_width=True)
        
        with advdec_col:
            st.markdown('<div class="section-header">📊 Adv-Dec</div>', unsafe_allow_html=True)
            
            # Create Adv-Dec chart
            fig = go.Figure(data=[
                go.Bar(
                    x=['Advancing', 'Declining'],
                    y=[advancing, declining],
                    marker_color=['green', 'red'],
                    text=[advancing, declining],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title=f"Advance/Decline: {advancing}/{declining}",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        st.markdown("*Data source: Yahoo Finance*")
    
    else:
        st.error("Failed to fetch market data. Please try again later.")

if __name__ == "__main__":
    main()