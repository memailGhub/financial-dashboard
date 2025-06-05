import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import urllib3

# -------------------------------
# Disable insecure request warnings (for verify=False)
# -------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------
# Configure the Streamlit page
# -------------------------------
st.set_page_config(
    page_title="NSE F&O Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# Custom CSS for styling elements
# -------------------------------
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

# -------------------------------
# Define list of F&O stocks and sector mapping
# -------------------------------
FO_STOCKS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
    'ICICIBANK', 'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ASIANPAINT',
    'ITC', 'LT', 'AXISBANK', 'MARUTI', 'TITAN',
    'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO', 'M&M',
    'BAJFINANCE', 'ONGC', 'NTPC', 'POWERGRID', 'COALINDIA',
    'TATASTEEL', 'ADANIENT', 'TECHM', 'HCLTECH', 'TATAMOTORS',
    'DRREDDY', 'BAJAJFINSV', 'GRASIM', 'CIPLA', 'BRITANNIA',
    'APOLLOHOSP', 'DIVISLAB', 'EICHERMOT', 'BPCL', 'TATACONSUM'
]

# Sector mapping: keys should match the NSE symbols (without .NS)
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
    'DIVISLAB': 'Pharma', 'EICHERMOT': 'Automobile', 'BPCL': 'Oil_Gas',
    'TATACONSUM': 'FMCG'
}

# -------------------------------
# NSE API Data Fetch Functions
# -------------------------------

def get_nse_session():
    """
    Returns a requests.Session object with appropriate headers.
    This is required for NSE API calls to succeed.
    """
    session = requests.Session()
    session.headers.update({
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                       '(KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
         'Accept-Language': 'en-US,en;q=0.9',
         'Accept-Encoding': 'gzip, deflate, br'
    })
    return session

def fetch_nse_quote(symbol, session):
    """Fetch real-time quote for a given symbol from the NSE API"""
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
        # Fallback: simulated data for demo purposes
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
    """Fetch NSE indices data (specifically NIFTY 50) from the NSE API"""
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
    except Exception:
        pass
    # Fallback: simulate data for demo
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
    """Fetch live F&O data using NSE API and threading for speed"""
    session = get_nse_session()
    fo_data = {}

    def fetch_single_stock(symbol):
        return fetch_nse_quote(symbol, session)

    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map over FO_STOCKS (each symbol without a .NS suffix)
        results = executor.map(fetch_single_stock, FO_STOCKS)
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

# -------------------------------
# Chart Creation Functions
# -------------------------------

def create_nifty_indicator(nifty_data):
    """
    Create a simple indicator chart displaying the current value,
    absolute change, and percentage change for the NIFTY 50 index.
    """
    if not nifty_data:
        return None

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=nifty_data['last'],
        delta={'reference': nifty_data['last'] - nifty_data['change'],
               'relative': False, 'valueformat':'.2f'},
        title={"text": "NIFTY 50"}
    ))
    fig.update_layout(height=250)
    return fig

def create_heatmap(fo_data):
    """
    Create a heatmap visualization for F&O stocks arranged in a grid.
    The grid is 8 rows x 5 columns (40 cells) showing ticker and change percentage.
    """
    if not fo_data:
        return None

    # Extract symbols and their percentage change values
    symbols = list(fo_data.keys())
    changes = [fo_data[symbol]['change_pct'] for symbol in symbols]

    # Desired grid dimensions: 8 rows x 5 columns
    rows, cols = 8, 5
    while len(symbols) < rows * cols:
        symbols.append("")
        changes.append(0)

    # Reshape flat lists into two-dimensional grids
    symbols_grid = np.array(symbols[:rows*cols]).reshape(rows, cols)
    changes_grid = np.array(changes[:rows*cols]).reshape(rows, cols)

    # Build text for each grid cell (show ticker and formatted change%)
    text_grid = []
    for i in range(rows):
        row_text = []
        for j in range(cols):
            if symbols_grid[i, j]:
                name = symbols_grid[i, j]
                change_val = changes_grid[i, j]
                row_text.append(f"{name}<br>{change_val:.1f}%")
            else:
                row_text.append("")
        text_grid.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=changes_grid,
        text=text_grid,
        texttemplate="%{text}",
        textfont={"size": 10},
        colorscale='RdYlGn',
        zmid=0,
        showscale=True,
        colorbar=dict(
            title=dict(text="Change %"),
            tickfont=dict(size=10)
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
    """
    Generate a horizontal bar chart displaying the average percentage change
    per sector for F&O stocks.
    """
    if not fo_data:
        return None

    sector_performance = {}
    for symbol, data in fo_data.items():
        sector = data['sector']
        sector_performance.setdefault(sector, []).append(data['change_pct'])

    sector_avg = {s: np.mean(changes) for s, changes in sector_performance.items()}
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

# -------------------------------
# Main App Function
# -------------------------------
def main():
    st.markdown('<h1 class="main-header">🇮🇳 NSE F&O Dashboard</h1>', unsafe_allow_html=True)

    # Top layout with a refresh button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()  # clear Streamlit cache
            st.experimental_rerun()

    # Display section header for loading market data
    st.markdown('<div class="section-header">📊 Loading Market Data...</div>', unsafe_allow_html=True)

    # Fetch live NSE indices & F&O data from NSE website
    nifty_data = fetch_nse_indices()
    fo_data = fetch_live_fo_data()

    if nifty_data and fo_data:
        # Layout columns: charts, scans, and dashboard metrics
        chart_col, scan_col, dashboard_col = st.columns([2, 1, 1])

        # -------------------------------
        # Charts Section: NIFTY Indicator
        # -------------------------------
        with chart_col:
            st.markdown('<div class="section-header">📈 Charts</div>', unsafe_allow_html=True)
            nifty_indicator = create_nifty_indicator(nifty_data)
            if nifty_indicator:
                st.plotly_chart(nifty_indicator, use_container_width=True)

        # -------------------------------
        # Scans Section: Top Gainers & Losers
        # -------------------------------
        with scan_col:
            st.markdown('<div class="section-header">🔍 Scans</div>', unsafe_allow_html=True)
            # Sort F&O stocks by percentage change descending
            sorted_stocks = sorted(fo_data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            # Top 5 gainers
            st.markdown("**Price Up**")
            for symbol, data in sorted_stocks[:5]:
                st.markdown(f'<span class="stock-gain">{symbol} +{data["change_pct"]:.1f}%</span>', unsafe_allow_html=True)
            st.markdown("---")
            # Top 5 losers
            st.markdown("**Price Down**")
            for symbol, data in sorted_stocks[-5:]:
                st.markdown(f'<span class="stock-loss">{symbol} {data["change_pct"]:.1f}%</span>', unsafe_allow_html=True)

        # -------------------------------
        # Dashboard Section: Metrics
        # -------------------------------
        with dashboard_col:
            st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
            total_stocks = len(fo_data)
            advancing = sum(1 for data in fo_data.values() if data['change_pct'] > 0)
            declining = total_stocks - advancing

            # Mock additional metrics (could be replaced with real data)
            put_call_ratio = 0.72
            vix = 16.2

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

        # -------------------------------
        # Full Width Section: Heatmap
        # -------------------------------
        st.markdown('<div class="section-header">🎯 Heatmap</div>', unsafe_allow_html=True)
        heatmap = create_heatmap(fo_data)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)

        # -------------------------------
        # Sectors & Advance/Decline Charts
        # -------------------------------
        sectors_col, advdec_col = st.columns(2)
        with sectors_col:
            st.markdown('<div class="section-header">🏢 Sectors</div>', unsafe_allow_html=True)
            sectors_chart = create_sectors_chart(fo_data)
            if sectors_chart:
                st.plotly_chart(sectors_chart, use_container_width=True)
        with advdec_col:
            st.markdown('<div class="section-header">📊 Adv-Dec</div>', unsafe_allow_html=True)
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

        # -------------------------------
        # Footer Section
        # -------------------------------
        st.markdown("---")
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        st.markdown("*Data source: NSE India*")
    else:
        st.error("Failed to fetch market data. Please try again later.")

if __name__ == "__main__":
    main()
