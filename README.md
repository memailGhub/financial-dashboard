# Live NSE F&O Financial Trading Dashboard

## Overview
This project is a Python-based financial dashboard that provides a live view of the Indian National Stock Exchange (NSE) Futures & Options (F&O) segment. It's built using Streamlit to offer an interactive web interface, allowing users to monitor market movements, track specific F&O stocks, visualize NIFTY 50 performance, and gain insights through various charts and metrics. The dashboard aims to provide traders and investors with real-time data to inform their decisions.

## Key Features
*   **Live Data Fetching:** Connects directly to the NSE India website to attempt to fetch real-time stock quotes and index data. Includes a fallback to simulated data if live fetching fails.
*   **NIFTY 50 Chart:** Displays a live-updating candlestick chart for the NIFTY 50 index, including trading volume.
*   **F&O Stock Heatmap:** Visualizes the performance of selected F&O stocks using a color-coded heatmap based on percentage change.
*   **Sector Performance:** Shows the average performance of different market sectors based on the F&O stocks.
*   **Top Gainers & Losers:** Lists the top 5 advancing and declining F&O stocks.
*   **Live Metrics:** Displays key market metrics such as Put/Call Ratio (simulated), VIX (simulated), and market breadth (advancing/declining stocks).
*   **Auto-Refresh:** Data automatically refreshes every 30 seconds to provide a near real-time experience.
*   **Customizable Styling:** Includes custom CSS for an enhanced user interface.

## Technology Stack
*   **Python:** Core programming language.
*   **Streamlit:** For creating the interactive web application.
*   **Plotly & Plotly Express:** For generating interactive charts and visualizations.
*   **Pandas:** For data manipulation and analysis.
*   **NumPy:** For numerical operations.
*   **Requests:** For making HTTP requests to fetch data from the NSE website.
*   **urllib3:** Used by `requests` for HTTP connection pooling; warnings are disabled for SSL.

## Prerequisites
*   Python 3.7 or higher
*   pip (Python package installer)

## Installation
1.  **Clone the repository (if applicable):**
    ```bash
    # If you have this project in a git repository, clone it:
    # git clone <repository_url>
    # cd <repository_directory>
    ```
    If you've downloaded the files directly, navigate to the project directory.

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run
Once the prerequisites are met and dependencies are installed, run the dashboard using the following command in your terminal:
```bash
streamlit run nse_dashboard.py
```
This will typically open the dashboard in your default web browser.

## Project Structure
*   `nse_dashboard.py`: The main Streamlit application script that contains the logic for data fetching, UI layout, and visualizations.
*   `requirements.txt`: Lists all the Python dependencies required to run the project.
*   Other `.py` files: The repository contains several other Python scripts which appear to be different versions, experiments, or alternative dashboards (e.g., `copilot_nse_dashboard1.py`, `stock_dashboard.py`). This README focuses on `nse_dashboard.py`.

## Data Source
The dashboard attempts to fetch live F&O data and NIFTY 50 index information directly from the official NSE India website (`nseindia.com`).
**Fallback Mechanism:** In case the live NSE API cannot be reached or returns an error, the application has a fallback mechanism that uses randomly generated (simulated) data to ensure the dashboard remains functional for demonstration purposes. This is particularly useful if NSE changes its API structure or if there are network connectivity issues.

## Customization
*   **Stock List:** The list of F&O stocks (`FO_STOCKS`) and their sector mappings (`SECTOR_MAPPING`) are hardcoded at the beginning of `nse_dashboard.py`. You can modify these dictionaries to track different stocks or update sector information.
*   **API Endpoints:** The NSE API endpoints are defined in functions like `fetch_nse_quote` and `fetch_nse_indices`. These might need updates if NSE changes its API.

## Disclaimer
This dashboard is intended for educational and informational purposes only. It is NOT financial advice. The data provided, especially the simulated data, should not be used for making actual trading decisions. Always consult with a qualified financial advisor before making any investment decisions. The accuracy and timeliness of live data depend on the NSE India website and are not guaranteed.
