import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import urllib3
import random

# -------------------------------
# Disable insecure request warnings
# -------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------
# UI CONFIGURATION from provided JSON
# -------------------------------
ui_config = {
    "appName": "myfio",
    "header": {
        "search": "Q MARKETS STOCKS OPTIONS NIFTY (Ful) 24728.90",
        "marketStatus": {
            "index": "NIFTY",
            "price": 24728.90,
            "change": "+53.60 (+0.2%)",
            "time": "3:15pm"
        },
        "navigation": ["Wall", "ALL", "widgets view", "Save head"]
    },
    "mainTabs": ["Charts", "Scans", "Dashboard", "Heatmap", "Adv-Dec", "Sectors"],
    "components": {
        "chartSection": {
            "title": "NIFTY 24728.90 +53.6 ▲ 0.2%",
            "type": "priceVolumeChart",
            "priceRange": {
                "high": 24700,
                "low": 24423,
                "current": 24675
            },
            "volume": [13, 24, 22],
            "timeLabels": ["10", "11", "12", "1", "2", "3"]
        },
        "scansSection": {
            "priceScanners": {
                "gainers": [
                    {"stock": "RVNL", "change": "+6.7"},
                    {"stock": "POLICYBZR", "change": "+5.4"},
                    {"stock": "CESC", "change": "+4.7"},
                    {"stock": "JUBLFOOD", "change": "+4.3"},
                    {"stock": "APLAPOLLO", "change": "+4.2"}
                ],
                "losers": [
                    {"stock": "ABFRL", "change": "-10.6"},
                    {"stock": "CHOLAFIN", "change": "-3.3"},
                    {"stock": "BAIJAFINSV", "change": "-2.2"},
                    {"stock": "PHOENIXLTD", "change": "-2.0"},
                    {"stock": "MANAPPURAM", "change": "-1.7%"}
                ]
            },
            "oiScanners": {
                "oiGainers": [
                    {"stock": "ABFRL", "change": "+151.6"},
                    {"stock": "RVNL", "change": "+78.5"},
                    {"stock": "UNOMINDA", "change": "+62.4"},
                    {"stock": "FORTS", "change": "+42.1"},
                    {"stock": "KAYNES", "change": "+38.4"}
                ],
                "oiLosers": [
                    {"stock": "IDEA", "change": "-92.8%"},
                    {"stock": "SIVN", "change": "-3.9%"},
                    {"stock": "MANAPPURAM", "change": "-3.0%"},
                    {"stock": "ETERNAL", "change": "-2.4%"},
                    {"stock": "TATAMOTORS", "change": "-1.9%"}
                ]
            }
        },
        "dashboard": {
            "metrics": [
                {"name": "pc", "value": 0.74, "change": "+0.09"},
                {"name": "iv", "value": 16.3, "change": "-1.1"},
                {"name": "basis", "value": 112.00, "change": "-20.80"},
                {"name": "rollover", "value": 24, "change": ""}
            ]
        },
        "heatmap": {
            "type": "grid",
            "rows": 8,
            "columns": 6,
            "cells": [
                {"stock": "ETERNA", "change": "+2.9%"},
                {"stock": "JOPHN", "change": "+2.0%"},
                {"stock": "TATAMO", "change": "+1.7%"},
                {"stock": "INDUSTRIAL", "change": "+1.6%"},
                {"stock": "ADANIE", "change": "+1.5%"},
                {"stock": "TECHN", "change": "+1.0%"},
                {"stock": "CELL7", "change": "+0.5%"},
                {"stock": "CELL8", "change": "-0.7%"},
                {"stock": "CELL9", "change": "+1.2%"},
                {"stock": "CELL10", "change": "-1.0%"},
                {"stock": "CELL11", "change": "+0.8%"},
                {"stock": "TREMT", "change": "-1.5%"},
                {"stock": "BAJAJF", "change": "+2.2%"}
            ]
        },
        "advanceDecline": {
            "advancers": 148,
            "decliners": 76
        },
        "sectorPerformance": {
            "type": "horizontalBarChart",
            "sectors": [
                {"name": "Power", "value": 16},
                {"name": "Telecom", "value": 14},
                {"name": "Chemicals", "value": 13},
                {"name": "New_Age", "value": 13},
                {"name": "Infrastruct..", "value": 12},
                {"name": "Technology", "value": 9},
                {"name": "Capital_Go..", "value": 7},
                {"name": "Media", "value": 6},
                {"name": "Automobile", "value": 5},
                {"name": "Oil_Gas", "value": 3},
                {"name": "Index", "value": 9},
                {"name": "Pharma", "value": 2},
                {"name": "Banking", "value": 1},
                {"name": "FMCG", "value": 1},
                {"name": "Cement", "value": 3}
            ]
        }
    },
    "layoutType": "Financial Dashboard",
    "visualFeatures": [
        "Color-coded heatmap (green/red for positive/negative)",
        "Sparkline charts",
        "Horizontal bar charts",
        "Metric cards with delta indicators",
        "Tab-based navigation",
        "Grid-based stock scanners"
    ]
}

# -------------------------------
# Common Styling and Layout
# -------------------------------
st.set_page_config(page_title="NSE F&O Dashboard", layout="wide")
st.markdown("""
<style>
    .header {font-size: 2em; font-weight: bold; text-align: center; margin-bottom: 1rem; color: #1f88e5;}
    .subheader {font-size: 1.2em; text-align: center; margin-bottom: 0.5rem;}
    .metric-card {background: linear-gradient(90deg, #667eea, #764ba2); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 0.5rem;}
    .metric-value {font-size: 2em; margin: 0; font-weight: bold;}
    .metric-label {font-size: 0.9em; margin: 0;}
    .nav-links {text-align: center; font-size: 0.95em; margin-bottom: 1rem; color: #444;}
    .section-title {font-size: 1.8em; font-weight: bold; margin: 1.5rem 0 1rem 0; border-bottom: 2px solid #1f88e5; padding-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Define F&O Stocks and Sector Mapping
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
# NSE API Data Fetch Functions (with fallback)
# -------------------------------
def get_nse_session():
    """
    Returns a requests.Session object with required headers.
    Priming the session with the NSE homepage is necessary.
    """
    session = requests.Session()
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/85.0.4183.83 Safari/537.36'),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    session.headers.update(headers)
    try:
        session.get("https://www.nseindia.com", timeout=10, verify=False)
    except Exception:
        pass
    return session

def fetch_nse_quote(symbol, session):
    """Fetch a real-time quote for a symbol from NSE API with simulation fallback."""
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
                    'volume': (data.get('marketDeptOrderBook', {}).get('totalBuyQuantity', 0) +
                               data.get('marketDeptOrderBook', {}).get('totalSellQuantity', 0)),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
    except Exception:
        pass
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

def fetch_nse_indices():
    """Fetch NSE indices data (NIFTY 50) from the NSE API with simulation fallback."""
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
    """Fetch live F&O data using multi-threaded calls from NSE API with fallback data."""
    session = get_nse_session()
    fo_data = {}
    def fetch_single_stock(symbol):
        return fetch_nse_quote(symbol, session)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_single_stock, FO_STOCKS)
        for result in results:
            if result:
                sym = result['symbol']
                fo_data[sym] = {
                    'current_price': result['ltp'],
                    'change': result['change'],
                    'change_pct': result['pChange'],
                    'volume': result['volume'],
                    'high': result['high'],
                    'low': result['low'],
                    'open': result['open'],
                    'close': result['close'],
                    'sector': SECTOR_MAPPING.get(sym, "Others"),
                    'timestamp': result['timestamp']
                }
    return fo_data

# -------------------------------
# Chart and Visualization Functions
# -------------------------------
def create_nifty_indicator(nifty_data):
    if not nifty_data:
        return None
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=nifty_data['last'],
        delta={'reference': nifty_data['last'] - nifty_data['change'], 'valueformat': '.2f'},
        title={"text": ui_config["components"]["chartSection"]["title"]}
    ))
    fig.update_layout(height=250)
    return fig

def create_heatmap_from_ui(ui_heatmap):
    rows = ui_heatmap.get("rows", 8)
    cols = ui_heatmap.get("columns", 6)
    cells = ui_heatmap.get("cells", [])
    while len(cells) < rows * cols:
        cells.append({"stock": "", "change": "0%"})
    stocks = [cell["stock"] for cell in cells[:rows * cols]]
    changes = []
    for cell in cells[:rows * cols]:
        ch_str = cell["change"].replace("%", "")
        try:
            changes.append(float(ch_str))
        except Exception:
            changes.append(0)
    stocks_grid = np.array(stocks).reshape(rows, cols)
    changes_grid = np.array(changes).reshape(rows, cols)
    text_grid = []
    for i in range(rows):
        row_text = []
        for j in range(cols):
            if stocks_grid[i, j]:
                row_text.append(f"{stocks_grid[i, j]}<br>{changes_grid[i, j]:.1f}%")
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
    fig.update_layout(title="F&O Stocks Heatmap", 
                      xaxis=dict(showticklabels=False), 
                      yaxis=dict(showticklabels=False), 
                      height=400)
    return fig

def create_sector_bar_chart(ui_sector):
    sectors = [s["name"] for s in ui_sector.get("sectors", [])]
    values = [s["value"] for s in ui_sector.get("sectors", [])]
    colors = ['green' if v >= 0 else 'red' for v in values]
    fig = go.Figure(data=[go.Bar(
        y=sectors, 
        x=values, 
        orientation='h', 
        marker_color=colors, 
        text=[f"{v}" for v in values], 
        textposition='auto'
    )])
    fig.update_layout(title="Sector Performance", xaxis_title="Average Change %", height=400)
    return fig

# -------------------------------
# Build the App UI (Single Page Layout)
# -------------------------------
def main():
    # HEADER
    st.markdown(f"<div class='header'>{ui_config['appName']} - NSE F&O Dashboard</div>", unsafe_allow_html=True)
    header_status = ui_config["header"]
    st.markdown(f"<div class='subheader'>{header_status['search']}</div>", unsafe_allow_html=True)
    market = header_status["marketStatus"]
    st.markdown(f"<div class='subheader'>{market['index']} {market['price']} {market['change']} @ {market['time']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='nav-links'>{' | '.join(header_status['navigation'])}</div>", unsafe_allow_html=True)
    
    # FETCH LIVE DATA FROM NSE
    nifty_data = fetch_nse_indices()
    fo_data  = fetch_live_fo_data()
    
    # Ensure we show all sections even if data fetching fails (fallback simulated data always available)
    # SECTION: Charts
    st.markdown("<div class='section-title'>Charts</div>", unsafe_allow_html=True)
    nifty_indicator = create_nifty_indicator(nifty_data)
    if nifty_indicator:
        st.plotly_chart(nifty_indicator, use_container_width=True)
    chart = ui_config["components"]["chartSection"]
    st.markdown(f"**Price Range:** High {chart['priceRange']['high']}, Low {chart['priceRange']['low']}, Current {chart['priceRange']['current']}")
    st.markdown(f"**Volume:** {chart['volume']} at times {', '.join(chart['timeLabels'])}")
    
    # SECTION: Scans
    st.markdown("<div class='section-title'>Scans</div>", unsafe_allow_html=True)
    scans = ui_config["components"]["scansSection"]
    st.markdown("### Price Scanners")
    st.markdown("**Gainers:**")
    for stock in scans["priceScanners"]["gainers"]:
        st.markdown(f"- {stock['stock']} {stock['change']}")
    st.markdown("**Losers:**")
    for stock in scans["priceScanners"]["losers"]:
        st.markdown(f"- {stock['stock']} {stock['change']}")
    st.markdown("### OI Scanners")
    st.markdown("**OI Gainers:**")
    for stock in scans["oiScanners"]["oiGainers"]:
        st.markdown(f"- {stock['stock']} {stock['change']}")
    st.markdown("**OI Losers:**")
    for stock in scans["oiScanners"]["oiLosers"]:
        st.markdown(f"- {stock['stock']} {stock['change']}")
    
    # SECTION: Dashboard
    st.markdown("<div class='section-title'>Dashboard</div>", unsafe_allow_html=True)
    dashboard = ui_config["components"]["dashboard"]["metrics"]
    dash_cols = st.columns(len(dashboard))
    for i, metric in enumerate(dashboard):
        with dash_cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metric["value"]}</div>
                <div class="metric-label">{metric["name"].upper()} {metric["change"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # SECTION: Heatmap
    st.markdown("<div class='section-title'>Heatmap</div>", unsafe_allow_html=True)
    heatmap_fig = create_heatmap_from_ui(ui_config["components"]["heatmap"])
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # SECTION: Advance/Decline
    st.markdown("<div class='section-title'>Advance/Decline</div>", unsafe_allow_html=True)
    adv_dec = ui_config["components"]["advanceDecline"]
    advdec_fig = go.Figure(data=[go.Bar(
        x=["Advancing", "Declining"],
        y=[adv_dec["advancers"], adv_dec["decliners"]],
        marker_color=['green', 'red'],
        text=[adv_dec["advancers"], adv_dec["decliners"]],
        textposition='auto'
    )])
    advdec_fig.update_layout(title=f"Advance/Decline: {adv_dec['advancers']}/{adv_dec['decliners']}", height=300)
    st.plotly_chart(advdec_fig, use_container_width=True)
    
    # SECTION: Sectors
    st.markdown("<div class='section-title'>Sectors</div>", unsafe_allow_html=True)
    sector_fig = create_sector_bar_chart(ui_config["components"]["sectorPerformance"])
    if sector_fig:
        st.plotly_chart(sector_fig, use_container_width=True)
    
    # FOOTER
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("*Data source: NSE India (or simulated data)*")

if __name__ == "__main__":
    main()
