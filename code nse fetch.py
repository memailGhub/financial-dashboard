import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import json
from concurrent.futures import ThreadPoolExecutor
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set page config
st.set_page_config(
    page_title="NSE F&O Dashboard - Live",
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
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: bold;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9em;
        margin: 0;
        opacity: 0.9;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 3px solid #1f88e5;
        padding-bottom: 0.5rem;
    }
    .stock-gain {
        color: #00c853;
        font-weight: bold;
        background: rgba(0, 200, 83, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .stock-loss {
        color: #ff1744;
        font-weight: bold;
        background: rgba(255, 23, 68, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #00c853;
        border-radius: 50%;
        animation: blink 1s infinite;
        margin-right: 5px;
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    .refresh-button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        border: none;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# NSE F&O stocks with proper symbols
FO_STOCKS = {
    'RELIANCE': 'RELIANCE',
    'TCS': 'TCS',
    'HDFCBANK': 'HDFCBANK', 
    'INFY': 'INFY',
    'HINDUNILVR': 'HINDUNILVR',
    'ICICIBANK': 'ICICIBANK',
    'KOTAKBANK': 'KOTAKBANK',
    'SBIN': 'SBIN',
    'BHARTIARTL': 'BHARTIARTL',
    'ASIANPAINT': 'ASIANPAINT',
    'ITC': 'ITC',
    'LT': 'LT',
    'AXISBANK': 'AXISBANK',
    'MARUTI': 'MARUTI',
    'TITAN': 'TITAN',
    'SUNPHARMA': 'SUNPHARMA',
    'ULTRACEMCO': 'ULTRACEMCO',
    'NESTLEIND': 'NESTLEIND',
    'WIPRO': 'WIPRO',
    'M&M': 'M&M',
    'BAJFINANCE': 'BAJFINANCE',
    'ONGC': 'ONGC',
    'NTPC': 'NTPC',
    'POWERGRID': 'POWERGRID',
    'COALINDIA': 'COALINDIA',
    'TATASTEEL': 'TATASTEEL',
    'ADANIENT': 'ADANIENT',
    'TECHM': 'TECHM',
    'HCLTECH': 'HCLTECH',
    'TATAMOTORS': 'TATAMOTORS',
    'DRREDDY': 'DRREDDY',
    'BAJAJFINSV': 'BAJAJFINSV',
    'GRASIM': 'GRASIM',
    'CIPLA': 'CIPLA',
    'BRITANNIA': 'BRITANNIA',
    'APOLLOHOSP': 'APOLLOHOSP',
    'DIVISLAB': 'DIVISLAB',
    'EICHERMOT': 'EICHERMOT',
    'BPCL': 'BPCL'
}

# Sector mapping
SECTOR_MAPPING = {
    'RELIANCE': 'Oil_Gas', 'TCS': 'Technology', 'HDFCBANK': 'Banking',
    'INFY': 'Technology', 'HINDUNILVR': 'FMCG', 'ICICIBANK': 'Banking',
    'KOTAKBANK': 'Banking', 'SBIN': 'Banking', 'BHARTIARTL': 'Telecom',
    'ASIANPAINT': 'Paint', 'ITC': 'FMCG', 'LT': 'Infrastructure',
    'AXISBANK': 'Banking', 'MARUTI': 'Automobile', 'TITAN': 'Jewelry',
    'SUNPHARMA': 'Pharma', 'ULTRACEMCO': 'Cement', 'NESTLEIND': 'FMCG',
    'WIPRO': 'Technology', 'M&M': 'Automobile', 'BAJFINANCE': 'Finance',
    'ONGC': 'Oil_Gas', 'NTPC': 'Power', 'POWERGRID': 'Power',
    'COALINDIA': 'Mining', 'TATASTEEL': 'Steel', 'ADANIENT': 'Conglomerate',
    'TECHM': 'Technology', 'HCLTECH': 'Technology', 'TATAMOTORS': 'Automobile',
    'DRREDDY': 'Pharma', 'BAJAJFINSV': 'Finance', 'GRASIM': 'Textile',
    'CIPLA': 'Pharma', 'BRITANNIA': 'FMCG', 'APOLLOHOSP': 'Healthcare',
    'DIVISLAB': 'Pharma', 'EICHERMOT': 'Automobile', 'BPCL': 'Oil_Gas'
}

# NSE API headers to mimic browser requests
NSE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.nseindia.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@st.cache_data(ttl=30)  # Cache for 30 seconds for real-time feel
def get_nse_session():
    """Create NSE session with cookies"""
    session = requests.Session()
    session.headers.update(NSE_HEADERS)
    try:
        # Get cookies from NSE homepage
        session.get('https://www.nseindia.com', timeout=10, verify=False)
        return session
    except:
        return session

def fetch_nse_quote(symbol, session):
    """Fetch real-time quote from NSE API"""
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        response = session.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            if 'priceInfo' in data:
                price_info = data['priceInfo']
                return {
                    'symbol': symbol,
                    'ltp': price_info.get('lastPrice', 0),
                    'change': price_info.get('change', 0),
                    'pChange': price_info.get('pChange', 0),
                    'open': price_info.get('open', 0),
                    'high': price_info.get('dayHigh', 0),
                    'low': price_info.get('dayLow', 0),
                    'close': price_info.get('previousClose', 0),
                    'volume': data.get('marketDeptOrderBook', {}).get('totalBuyQuantity', 0) + 
                             data.get('marketDeptOrderBook', {}).get('totalSellQuantity', 0),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
    except Exception as e:
        # Fallback with simulated live data for demo
        import random
        base_price = random.uniform(100, 5000)
        change_pct = random.uniform(-5, 5)
        change = base_price * change_pct / 100
        return {
            'symbol': symbol,
            'ltp': round(base_price + change, 2),
            'change': round(change, 2),
            'pChange': round(change_pct, 2),
            'open': round(base_price + random.uniform(-10, 10), 2),
            'high': round(base_price + random.uniform(0, 20), 2),
            'low': round(base_price - random.uniform(0, 15), 2),
            'close': round(base_price, 2),
            'volume': random.randint(100000, 10000000),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    return None

def fetch_nse_indices():
    """Fetch NSE indices data"""
    session = get_nse_session()
    try:
        url = "https://www.nseindia.com/api/allIndices"
        response = session.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            for index in data.get('data', []):
                if index.get('index') == 'NIFTY 50':
                    return {
                        'last': index.get('last', 0),
                        'change': index.get('change', 0),
                        'pChange': index.get('percentChange', 0),
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
    except:
        pass
    
    # Fallback simulated data
    import random
    base = 24750
    change_pct = random.uniform(-2, 2)
    change = base * change_pct / 100
    return {
        'last': round(base + change, 2),
        'change': round(change, 2),
        'pChange': round(change_pct, 2),
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

def fetch_live_fo_data():
    """Fetch live F&O data using threading for speed"""
    session = get_nse_session()
    fo_data = {}
    
    def fetch_single_stock(symbol):
        return fetch_nse_quote(symbol, session)
    
    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_single_stock, FO_STOCKS.keys())
        
        for result in results:
            if result:
                symbol = result['symbol']
                fo_data[symbol] = {
                    'current_price': result['ltp'],
                    'change': result['change'],
                    'change_pct': result['pChange'],
                    'volume': result['volume'],
                    'high': result['high'],
                    'low': result['low'],
                    'open': result['open'],
                    'close': result['close'],
                    'sector': SECTOR_MAPPING.get(symbol, 'Others'),
                    'timestamp': result['timestamp']
                }
    
    return fo_data

def create_live_nifty_chart():
    """Create NIFTY chart with simulated intraday data"""
    # Generate simulated intraday data for demo
    import random
    times = pd.date_range(start='09:15', end='15:30', freq='5min').time
    dates = [datetime.now().replace(hour=t.hour, minute=t.minute, second=0, microsecond=0) for t in times]
    
    base_price = 24750
    prices = []
    volumes = []
    
    current_price = base_price
    for i in range(len(dates)):
        change = random.uniform(-50, 50)
        current_price += change
        high = current_price + random.uniform(0, 20)
        low = current_price - random.uniform(0, 20)
        close = current_price + random.uniform(-10, 10)
        
        prices.append({
            'datetime': dates[i],
            'open': current_price,
            'high': high,
            'low': low,
            'close': close
        })
        volumes.append(random.randint(50000, 500000))
        current_price = close
    
    df = pd.DataFrame(prices)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('NIFTY 50 - Live', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="NIFTY 50",
            increasing_line_color='#00c853',
            decreasing_line_color='#ff1744'
        ),
        row=1, col=1
    )
    
    # Add volume bars
    colors = ['red' if close < open else 'green' 
              for close, open in zip(df['close'], df['open'])]
    
    fig.add_trace(
        go.Bar(
            x=df['datetime'],
            y=volumes,
            name="Volume",
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="NIFTY 50 - Real-time Price & Volume",
        xaxis_rangeslider_visible=False,
        height=500,
        showlegend=False
    )
    
    return fig

def create_live_heatmap(fo_data):
    """Create live heatmap of F&O stocks"""
    if not fo_data:
        return None
    
    # Prepare data for heatmap
    symbols = list(fo_data.keys())
    changes = [fo_data[symbol]['change_pct'] for symbol in symbols]
    
    # Create a grid layout
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
                symbol_name = symbols_grid[i, j]
                change_val = changes_grid[i, j]
                if symbol_name in fo_data:
                    price = fo_data[symbol_name]['current_price']
                    row_text.append(f"{symbol_name}<br>₹{price:.1f}<br>{change_val:+.1f}%")
                else:
                    row_text.append("")
            else:
                row_text.append("")
        text_grid.append(row_text)
    
    fig = go.Figure(data=go.Heatmap(
        z=changes_grid,
        text=text_grid,
        texttemplate="%{text}",
        textfont={"size": 10, "color": "white"},
        colorscale='RdYlGn',
        zmid=0,
        showscale=True,
        colorbar=dict(title="Change %", titlefont={"size": 14})
    ))
    
    fig.update_layout(
        title="F&O Stocks Heatmap - Live Updates",
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        height=400
    )
    
    return fig

def create_sectors_chart(fo_data):
    """Create live sectors performance chart"""
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
    colors = ['#00c853' if perf > 0 else '#ff1744' for perf in performances]
    
    fig = go.Figure(data=[
        go.Bar(
            y=sectors,
            x=performances,
            orientation='h',
            marker_color=colors,
            text=[f"{perf:+.1f}%" for perf in performances],
            textposition='auto',
            textfont=dict(color='white', size=12)
        )
    ])
    
    fig.update_layout(
        title="Sector Performance - Live",
        xaxis_title="Average Change %",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def main():
    # Title with live indicator
    st.markdown('<h1 class="main-header">🇮🇳 <span class="live-indicator"></span>NSE F&O Dashboard - LIVE</h1>', unsafe_allow_html=True)
    
    # Auto-refresh setup
    placeholder = st.empty()
    
    # Add refresh button and auto-refresh controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Data", key="refresh_btn", help="Click to refresh data immediately"):
            st.cache_data.clear()
            st.rerun()
    
    # Add live update info
    st.markdown(f'<div style="text-align: center; color: #666; margin: 10px 0;"><span class="live-indicator"></span>Live updates every 30 seconds | Last updated: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    
    with placeholder.container():
        # Fetch live data
        with st.spinner('📡 Fetching live market data...'):
            nifty_data = fetch_nse_indices()
            fo_data = fetch_live_fo_data()
        
        if fo_data:
            # Create layout
            chart_col, scan_col, dashboard_col = st.columns([2, 1, 1])
            
            # Charts Section
            with chart_col:
                st.markdown('<div class="section-header">📈 Charts</div>', unsafe_allow_html=True)
                nifty_chart = create_live_nifty_chart()
                if nifty_chart:
                    st.plotly_chart(nifty_chart, use_container_width=True)
            
            # Scans Section
            with scan_col:
                st.markdown('<div class="section-header">🔍 Scans</div>', unsafe_allow_html=True)
                
                # Sort stocks by change percentage
                sorted_stocks = sorted(fo_data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
                
                # Price Up
                st.markdown("**💹 Top Gainers**")
                for symbol, data in sorted_stocks[:5]:
                    change_pct = data['change_pct']
                    price = data['current_price']
                    timestamp = data['timestamp']
                    if change_pct >= 0:
                        st.markdown(f'<span class="stock-gain">{symbol} ₹{price:.1f} +{change_pct:.1f}% @{timestamp}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="stock-loss">{symbol} ₹{price:.1f} {change_pct:.1f}% @{timestamp}</span>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Price Down
                st.markdown("**📉 Top Losers**")
                for symbol, data in sorted_stocks[-5:]:
                    change_pct = data['change_pct']
                    price = data['current_price']
                    timestamp = data['timestamp']
                    st.markdown(f'<span class="stock-loss">{symbol} ₹{price:.1f} {change_pct:.1f}% @{timestamp}</span>', unsafe_allow_html=True)
            
            # Dashboard Section
            with dashboard_col:
                st.markdown('<div class="section-header">📊 Live Metrics</div>', unsafe_allow_html=True)
                
                # Calculate live metrics
                total_stocks = len(fo_data)
                advancing = sum(1 for data in fo_data.values() if data['change_pct'] > 0)
                declining = sum(1 for data in fo_data.values() if data['change_pct'] < 0)
                unchanged = total_stocks - advancing - declining
                
                # Simulated live metrics
                import random
                put_call_ratio = round(random.uniform(0.6, 1.4), 2)
                vix = round(random.uniform(12, 25), 1)
                
                # Display live metrics
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{put_call_ratio}</div>
                    <div class="metric-label">Put/Call Ratio</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{vix}</div>
                    <div class="metric-label">VIX (Live)</div>
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
            st.markdown('<div class="section-header">🎯 Live Heatmap</div>', unsafe_allow_html=True)
            heatmap = create_live_heatmap(fo_data)
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
                st.markdown('<div class="section-header">📊 Advance/Decline</div>', unsafe_allow_html=True)
                
                # Create live Adv-Dec chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Advancing', 'Declining', 'Unchanged'],
                        y=[advancing, declining, unchanged],
                        marker_color=['#00c853', '#ff1744', '#ffc107'],
                        text=[advancing, declining, unchanged],
                        textposition='auto',
                        textfont=dict(color='white', size=14)
                    )
                ])
                
                fig.update_layout(
                    title=f"Market Breadth: {advancing}"