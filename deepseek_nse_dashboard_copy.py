"""
NSE F&O Dashboard - Financial Market Analytics Platform
Streamlit application for real-time monitoring of NSE F&O stocks with advanced visualization
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ========================
# CONFIGURATION SETTINGS
# ========================
st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional financial dashboard styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        color: #1f88e5;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #4a6491 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: bold;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    .metric-label {
        font-size: 1em;
        margin: 0;
        opacity: 0.9;
    }
    .section-header {
        font-size: 1.6em;
        font-weight: bold;
        color: #2c3e50;
        margin: 1.2rem 0 0.8rem 0;
        border-bottom: 3px solid #1f88e5;
        padding-bottom: 0.6rem;
        font-family: 'Arial', sans-serif;
    }
    .stock-gain {
        color: #00c853;
        font-weight: bold;
        font-size: 1.1em;
    }
    .stock-loss {
        color: #ff5252;
        font-weight: bold;
        font-size: 1.1em;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00c853 0%, #00796b 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-size: 1.1em;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ========================
# CONSTANTS DEFINITIONS
# ========================

# List of F&O stocks (NSE symbols)
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

# Sector classification mapping
SECTOR_MAPPING = {
    'RELIANCE.NS': 'Oil & Gas', 'TCS.NS': 'Technology', 'HDFCBANK.NS': 'Banking',
    'INFY.NS': 'Technology', 'HINDUNILVR.NS': 'FMCG', 'ICICIBANK.NS': 'Banking',
    'KOTAKBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 'BHARTIARTL.NS': 'Telecom',
    'ASIANPAINT.NS': 'Paint', 'ITC.NS': 'FMCG', 'LT.NS': 'Infrastructure',
    'AXISBANK.NS': 'Banking', 'MARUTI.NS': 'Automobile', 'TITAN.NS': 'Jewelry',
    'SUNPHARMA.NS': 'Pharma', 'ULTRACEMCO.NS': 'Cement', 'NESTLEIND.NS': 'FMCG',
    'WIPRO.NS': 'Technology', 'M&M.NS': 'Automobile', 'BAJFINANCE.NS': 'Finance',
    'ONGC.NS': 'Oil & Gas', 'NTPC.NS': 'Power', 'POWERGRID.NS': 'Power',
    'COALINDIA.NS': 'Mining', 'TATASTEEL.NS': 'Steel', 'ADANIENT.NS': 'Conglomerate',
    'TECHM.NS': 'Technology', 'HCLTECH.NS': 'Technology', 'TATAMOTORS.NS': 'Automobile',
    'DRREDDY.NS': 'Pharma', 'BAJAJFINSV.NS': 'Finance', 'GRASIM.NS': 'Textile',
    'CIPLA.NS': 'Pharma', 'BRITANNIA.NS': 'FMCG', 'APOLLOHOSP.NS': 'Healthcare',
    'DIVISLAB.NS': 'Pharma', 'EICHERMOT.NS': 'Automobile', 'BPCL.NS': 'Oil & Gas',
    'TATACONSUM.NS': 'FMCG'
}

# ========================
# DATA FETCHING FUNCTIONS
# ========================

@st.cache_data(ttl=300)
def fetch_stock_data(symbol: str, period: str = "1d") -> tuple:
    """
    Fetch stock data using Yahoo Finance API
    
    Args:
        symbol: Stock ticker symbol
        period: Time period for historical data
        
    Returns:
        tuple: (Historical data, Stock info)
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        info = stock.info
        return data, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None, None

@st.cache_data(ttl=300)
def fetch_nifty_data() -> pd.DataFrame:
    """
    Fetch NIFTY 50 index data with 5-minute intervals
    
    Returns:
        pd.DataFrame: Historical data for NIFTY 50
    """
    try:
        nifty = yf.Ticker("^NSEI")
        return nifty.history(period="5d", interval="5m")
    except Exception as e:
        st.error(f"Error fetching NIFTY data: {e}")
        return None

@st.cache_data(ttl=300)
def fetch_all_fo_data() -> dict:
    """
    Fetch data for all F&O stocks with progress tracking
    
    Returns:
        dict: Dictionary containing stock performance data
    """
    fo_data = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(FO_STOCKS):
        status_text.text(f'Loading {symbol}... ({i+1}/{len(FO_STOCKS)})')
        data, info = fetch_stock_data(symbol)
        if data is not None and not data.empty:
            # Calculate price changes
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            # Store relevant metrics
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

# ========================
# VISUALIZATION FUNCTIONS
# ========================

def create_nifty_chart(nifty_data: pd.DataFrame) -> go.Figure:
    """
    Create candlestick chart for NIFTY 50 with volume bars
    
    Args:
        nifty_data: Historical data for NIFTY 50
        
    Returns:
        go.Figure: Plotly figure object
    """
    if nifty_data is None or nifty_data.empty:
        return None
    
    # Create subplots with shared x-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('NIFTY 50 Price', 'Trading Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Add candlestick chart to first subplot
    fig.add_trace(
        go.Candlestick(
            x=nifty_data.index,
            open=nifty_data['Open'],
            high=nifty_data['High'],
            low=nifty_data['Low'],
            close=nifty_data['Close'],
            name="NIFTY 50",
            increasing_line_color='#2ecc71',
            decreasing_line_color='#e74c3c'
        ),
        row=1, col=1
    )
    
    # Add volume bars with color coding (green/red)
    colors = ['#e74c3c' if close < open else '#2ecc71' 
              for close, open in zip(nifty_data['Close'], nifty_data['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=nifty_data.index,
            y=nifty_data['Volume'],
            name="Volume",
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Update layout for professional appearance
    fig.update_layout(
        title="NIFTY 50 - Price & Volume Analysis",
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    # Format axes
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=1)
    
    return fig

def create_heatmap(fo_data: dict) -> go.Figure:
    """
    Create performance heatmap for F&O stocks
    
    Args:
        fo_data: Dictionary containing stock performance data
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not fo_data:
        return None
    
    # Prepare data for heatmap
    symbols = list(fo_data.keys())
    changes = [fo_data[symbol]['change_pct'] for symbol in symbols]
    
    # Create grid layout (8 rows x 5 columns)
    rows, cols = 8, 5
    
    # Pad with empty values for consistent grid
    while len(symbols) < rows * cols:
        symbols.append("")
        changes.append(0)
    
    # Reshape data into grid format
    symbols_grid = np.array(symbols[:rows*cols]).reshape(rows, cols)
    changes_grid = np.array(changes[:rows*cols]).reshape(rows, cols)
    
    # Create HTML-formatted text for each cell
    text_grid = []
    for i in range(rows):
        row_text = []
        for j in range(cols):
            if symbols_grid[i, j]:
                symbol_name = symbols_grid[i, j].replace('.NS', '')
                change_val = changes_grid[i, j]
                # Color code based on performance
                color = '#2ecc71' if change_val >= 0 else '#e74c3c'
                row_text.append(
                    f"<b>{symbol_name}</b><br>"
                    f"<span style='color:{color};'>{change_val:+.1f}%</span>"
                )
            else:
                row_text.append("")
        text_grid.append(row_text)
    
    # Create heatmap with corrected colorbar configuration
    fig = go.Figure(data=go.Heatmap(
        z=changes_grid,
        text=text_grid,  # HTML-formatted text
        texttemplate="%{text}",
        textfont={"size": 11},
        colorscale='RdYlGn',  # Red-Yellow-Green color scale
        zmid=0,  # Center color scale at zero
        showscale=True,  # Show color scale bar
        hoverinfo='text',  # Show custom text on hover
        # FIXED COLORBAR CONFIGURATION:
        colorbar=dict(
            title=dict(text="Change %", side="right"),  # Title configuration
            tickfont=dict(size=10),  # Tick label font
            thickness=15,  # Thickness of colorbar
            len=0.75  # Length of colorbar
        )
    ))
    
    # Update layout for clean presentation
    fig.update_layout(
        title="F&O Stocks Performance Heatmap",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        height=500,
        margin=dict(l=20, r=20, t=80, b=20),
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    return fig

def create_sectors_chart(fo_data: dict) -> go.Figure:
    """
    Create horizontal bar chart for sector performance
    
    Args:
        fo_data: Dictionary containing stock performance data
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not fo_data:
        return None
    
    # Calculate sector performance averages
    sector_performance = {}
    for symbol, data in fo_data.items():
        sector = data['sector']
        sector_performance.setdefault(sector, []).append(data['change_pct'])
    
    sector_avg = {sector: np.mean(changes) for sector, changes in sector_performance.items()}
    
    # Sort sectors by performance
    sorted_sectors = sorted(sector_avg.items(), key=lambda x: x[1], reverse=True)
    sectors = [item[0] for item in sorted_sectors]
    performances = [item[1] for item in sorted_sectors]
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=sectors,
            x=performances,
            orientation='h',
            marker_color=['#2ecc71' if perf > 0 else '#e74c3c' for perf in performances],
            text=[f"{perf:+.1f}%" for perf in performances],
            textposition='auto',
            hoverinfo='text',
            hovertemplate='<b>%{y}</b><br>Avg Change: %{x:.2f}%<extra></extra>'
        )
    ])
    
    # Professional layout configuration
    fig.update_layout(
        title="Sector Performance Analysis",
        xaxis_title="Average Daily Change (%)",
        height=500,
        template='plotly_white',
        margin=dict(l=120, r=20, t=80, b=50),
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    return fig

# ========================
# MAIN APPLICATION
# ========================

def main():
    """Main application function"""
    
    # Dashboard title with professional styling
    st.markdown(
        '<h1 class="main-header">🇮🇳 NSE F&O MARKET DASHBOARD</h1>', 
        unsafe_allow_html=True
    )
    
    # Refresh button in centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Market Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Data loading section
    st.markdown(
        '<div class="section-header">📊 REAL-TIME MARKET DATA</div>', 
        unsafe_allow_html=True
    )
    
    # Fetch market data
    with st.spinner("Loading NIFTY 50 data..."):
        nifty_data = fetch_nifty_data()
    
    with st.spinner("Analyzing F&O stocks..."):
        fo_data = fetch_all_fo_data()
    
    # Check if data loaded successfully
    if nifty_data is None or not fo_data:
        st.error("❌ Failed to fetch market data. Please check your connection and try again.")
        return
    
    # ========================
    # DASHBOARD LAYOUT
    # ========================
    
    # Main columns layout
    chart_col, scan_col, dashboard_col = st.columns([2, 1, 1])
    
    # ----- CHARTS SECTION -----
    with chart_col:
        st.markdown(
            '<div class="section-header">📈 MARKET CHARTS</div>', 
            unsafe_allow_html=True
        )
        nifty_chart = create_nifty_chart(nifty_data)
        if nifty_chart:
            st.plotly_chart(nifty_chart, use_container_width=True)
    
    # ----- SCANS SECTION -----
    with scan_col:
        st.markdown(
            '<div class="section-header">🔍 MARKET SCANS</div>', 
            unsafe_allow_html=True
        )
        
        # Sort stocks by performance
        sorted_stocks = sorted(
            fo_data.items(), 
            key=lambda x: x[1]['change_pct'], 
            reverse=True
        )
        
        # Top performers
        st.markdown("**🔺 TOP GAINERS**")
        for symbol, data in sorted_stocks[:5]:
            name = symbol.replace('.NS', '')
            change_pct = data['change_pct']
            st.markdown(
                f'<div class="stock-gain">▲ {name} +{change_pct:.1f}%</div>', 
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Bottom performers
        st.markdown("**🔻 TOP LOSERS**")
        for symbol, data in sorted_stocks[-5:]:
            name = symbol.replace('.NS', '')
            change_pct = data['change_pct']
            st.markdown(
                f'<div class="stock-loss">▼ {name} {change_pct:.1f}%</div>', 
                unsafe_allow_html=True
            )
    
    # ----- DASHBOARD METRICS -----
    with dashboard_col:
        st.markdown(
            '<div class="section-header">📊 MARKET METRICS</div>', 
            unsafe_allow_html=True
        )
        
        # Calculate market breadth
        total_stocks = len(fo_data)
        advancing = sum(1 for data in fo_data.values() if data['change_pct'] > 0)
        declining = total_stocks - advancing
        
        # Mock market indicators (would be real-time in production)
        put_call_ratio = 0.72
        vix = 16.2
        
        # Display metrics in professional cards
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{put_call_ratio}</div>
            <div class="metric-label">PUT/CALL RATIO</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{vix}</div>
            <div class="metric-label">VOLATILITY INDEX (VIX)</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{advancing}</div>
            <div class="metric-label">ADVANCING STOCKS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{declining}</div>
            <div class="metric-label">DECLINING STOCKS</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ----- MARKET HEATMAP -----
    st.markdown(
        '<div class="section-header">🎯 F&O STOCKS HEATMAP</div>', 
        unsafe_allow_html=True
    )
    heatmap = create_heatmap(fo_data)
    if heatmap:
        st.plotly_chart(heatmap, use_container_width=True)
    
    # ----- SECTOR ANALYSIS -----
    sectors_col, advdec_col = st.columns(2)
    
    with sectors_col:
        st.markdown(
            '<div class="section-header">🏢 SECTOR PERFORMANCE</div>', 
            unsafe_allow_html=True
        )
        sectors_chart = create_sectors_chart(fo_data)
        if sectors_chart:
            st.plotly_chart(sectors_chart, use_container_width=True)
    
    with advdec_col:
        st.markdown(
            '<div class="section-header">📊 MARKET BREADTH</div>', 
            unsafe_allow_html=True
        )
        
        # Create advance/decline chart
        fig = go.Figure(data=[
            go.Bar(
                x=['Advancing', 'Declining'],
                y=[advancing, declining],
                marker_color=['#2ecc71', '#e74c3c'],
                text=[f"{advancing} stocks", f"{declining} stocks"],
                textposition='auto',
                width=0.6
            )
        ])
        
        # Professional chart styling
        fig.update_layout(
            title=f"Advance/Decline Ratio: {advancing}:{declining}",
            height=350,
            template='plotly_white',
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis_title="",
            yaxis_title="Number of Stocks"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ----- FOOTER -----
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("*Data source: Yahoo Finance • Market data delayed by 15 minutes*")

if __name__ == "__main__":
    main()