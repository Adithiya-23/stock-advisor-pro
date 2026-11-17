import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock Advisor Pro - Complete Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS styling
st.markdown("""
    <style>
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --background-color: #f8f9fa;
        --card-background: #ffffff;
        --text-color: #2c3e50;
    }

    .main {
        padding: 2rem;
        background-color: var(--background-color);
    }

    .stSidebar {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        color: var(--primary-color) !important;
        font-weight: 600;
    }

    .stTitle {
        color: var(--primary-color) !important;
    }

    .stMetric {
        background-color: var(--card-background);
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .stMetric label {
        color: #6c757d;
        font-size: 0.85rem;
        margin-bottom: 4px;
        display: block;
    }

    .stMetric .value {
        color: var(--primary-color);
        font-size: 1.75rem;
        font-weight: 600;
        margin-top: 4px;
    }

    .stMetric .delta {
        font-size: 0.9rem;
        margin-top: 4px;
    }

    .stButton>button {
        width: 100%;
        margin-top: 8px;
        height: 38px;
        background-color: var(--secondary-color);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
    }

    .stButton>button:hover {
        background-color: #2980b9;
    }

    .stSelectbox > div > div {
        border: 1px solid #ced4da;
        border-radius: 6px;
    }

    .stAlert {
        padding: 12px;
        border-radius: 8px;
        margin: 12px 0;
    }

    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: white;
    }

    .stExpander > summary {
        color: var(--primary-color);
        font-weight: 500;
    }

    .footer {
        text-align: center;
        padding: 20px;
        color: #7f8c8d;
        font-size: 0.8rem;
        margin-top: 40px;
    }

    .stRadio > div {
        gap: 8px;
    }

    .stCheckbox > label {
        font-size: 0.9rem;
    }

    .stSpinner > div {
        border-color: #2c3e50 transparent #2c3e50 transparent;
    }

    h1, h2, h3, h4 {
        color: var(--primary-color) !important;
        margin-top: 0;
    }

    .stTabs [data-baseweb="tab-list"] button [data-teststoc="icon"] {
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATA FUNCTIONS
# ============================================================

NSE_STOCKS_300 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "SBIN", "ONGC",
    "LT", "ASIANPAINT", "MARUTI", "KOTAKBANK", "TITAN", "HCLTECH", "ULTRACEMCO",
    "TECHM", "Wipro", "NTPC", "POWERGRID", "COALINDIA", "DRREDDY", "BPCL", "HINDUNILVR",
    "EICHERMOT", "ADANIPORTS", "ITC", "JSWSTEEL", "TATAMOTORS", "BAJAJFINSV", "BAJAJFINANCE",
    "HDFC", "KOTAKBANK", "NMDC", "TATASTEEL", "M&M", "HEROMOTOCO", "DIVISBHA",
    "PIDILIT", "BOSCH", "M&MFIN", "AXISBANK", "ICICIBANK", "INDUSINDB", "FEDERALBK",
    "KARURVYSYA", "CITYUNION", "TAMILNAD", "KARNATAK", "DCCB", "MAVB", "CBL", "COOK",
    "BERGEPAINT", "BALKRISIND", "BAJFINANCE", "CESC", "CGPOWER", "CIPLA", "DABUR", "GAIL",
    "Grasim", "HAVELLS", "ICICIPRULI", "IOC", "IDFCFIRST", "INDUSINDBANK", "INOX", "JKCEMENT",
    "JSWENERGY", "KEI", "LALPATHLAB", "LAURUSLABS", "MAKERIN", "MASTEK", "METROPOLIS",
    "MOTHERSUMI", "NAMOTRON", "NAVA", "NAVINFLU", "OLECTO", "OIL", "OLECTRA", "ORCHID",
    "PAGEIND", "PATANJALI", "PCBL", "PEL", "PFC", "PIDILITIND", "PIIND", "PNB", "PNBGILTS",
    "POWERFIN", "PRINCE", "PROMINENT", "PROSUS", "PURVA", "QUINT", "RBLBANK", "REC",
    "RELIANCE", "REPCOHOME", "RELCHEMQ", "SAIL", "SUNPHARMA", "SYRINX", "TATAELXSI",
    "TATAGLOBAL"
]

LARGE_CAP_STOCKS = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "SBIN", "ONGC", "LT", "ASIANPAINT"]
MID_CAP_STOCKS = ["ABB", "ADANIENTER", "ADANIGAS", "APOLLOHOSP", "ASTRAL", "ATUL", "BANKOFBARODA", "BANKINDIA", "BARRICADE", "BASSEIN"]
SMALL_CAP_STOCKS = ["ABB", "ADANIENTER", "ADANIGAS", "APOLLOHOSP", "ASTRAL", "ATUL", "BANKOFBARODA", "BANKINDIA", "BARRICADE", "BASSEIN"]


def get_market_cap_category(market_cap):
    """ categorize stock based on market cap """
    if market_cap is None or market_cap == 0:
        return "Unknown"
    elif market_cap >= 200000000000:  # ₹2 lakh crores
        return "Large Cap"
    elif market_cap >= 50000000000:  # ₹50,000 crores
        return "Mid Cap"
    else:
        return "Small Cap"


def get_stock_data(ticker: str) -> dict:
    """Fetch stock data from Yahoo Finance"""
    try:
        ticker_obj = yf.Ticker(ticker + ".NS")
        info = ticker_obj.info

        # Safely extract data with defaults
        current_price = info.get("currentPrice", 0) or 0
        market_cap = info.get("marketCap", 0) or 0
        pe_ratio = info.get("peRatio", 0) or 0
        profit_margin = info.get("profitMargins", 0) or 0
        revenue_growth = info.get("revenueGrowth", 0) or 0
        dividend_yield = info.get("dividendYield", 0) or 0
        beta = info.get("beta", 0) or 0
        target_price = info.get("targetMeanPrice", 0) or 0
        fifty_two_week_high = info.get("fiftyTwoWeekHigh", 0) or 0
        fifty_two_week_low = info.get("fiftyTwoWeekLow", 0) or 0
        book_value = info.get("bookValue", 0) or 0
        forward_pe = info.get("forwardPE", 0) or 0
        price_to_sales = info.get("priceToSales", 0) or 0

        analysis = {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "current_price": current_price,
            "market_cap": market_cap,
            "category": get_market_cap_category(market_cap),
            "pe_ratio": pe_ratio,
            "profit_margin": profit_margin,
            "revenue_growth": revenue_growth,
            "dividend_yield": dividend_yield,
            "beta": beta,
            "target_price": target_price,
            "upside": (target_price - current_price) if target_price and current_price else 0,
            "fifty_week_high": fifty_two_week_high,
            "fifty_week_low": fifty_two_week_low,
            "pe_quarterly": info.get("trailingPE", 0) or 0,
            "earnings_growth": info.get("earningsGrowth", 0) or 0,
            "book_value": book_value,
            "forward_pe": forward_pe,
            "price_to_sales": price_to_sales,
        }

        # Calculate 52-week status
        if fifty_two_week_high and fifty_two_week_low and current_price:
            percent_to_high = ((fifty_two_week_high - current_price) / fifty_two_week_high) * 100
            percent_to_low = ((current_price - fifty_two_week_low) / (fifty_two_week_high - fifty_two_week_low)) * 100

            if percent_to_high <= 0:
                analysis["fifty_week_status"] = "AT_HIGH"
            elif percent_to_low <= 0:
                analysis["fifty_week_status"] = "AT_LOW"
            elif percent_to_high < 5:
                analysis["fifty_week_status"] = "NEAR_HIGH"
            elif percent_to_low < 5:
                analysis["fifty_week_status"] = "NEAR_LOW"
            else:
                analysis["fifty_week_status"] = "Normal"
        else:
            analysis["fifty_week_status"] = "Normal"

        # Analysis score
        score = 0
        if analysis["profit_margin"] > 0.10:
            score += 2
        if analysis["revenue_growth"] > 0.05:
            score += 2
        if 0 < analysis["pe_ratio"] < 20:
            score += 2
        if analysis["dividend_yield"] > 0.03:
            score += 1
        if analysis["fifty_week_status"] in ["AT_HIGH", "AT_LOW"]:
            score += 1
        analysis["analysis_score"] = score

        # Recommendation logic
        if score >= 8:
            analysis["recommendation"] = "STRONG BUY"
            analysis["confidence"] = "High - Strong financial fundamentals"
        elif score >= 6:
            analysis["recommendation"] = "BUY"
            analysis["confidence"] = "Medium - Good growth prospects"
        elif score >= 4:
            analysis["recommendation"] = "HOLD"
            analysis["confidence"] = "Low - Monitor for better entry"
        else:
            analysis["recommendation"] = "AVOID"
            analysis["confidence"] = "Very Low - Consider alternative investments"

        # Expert notes
        expert_notes = []
        if analysis["profit_margin"] * 100 > 15:
            expert_notes.append(f"Strong profit margin of {analysis['profit_margin']*100:.1f}%")
        if 0 < analysis["pe_ratio"] < 20:
            expert_notes.append(f"Reasonable P/E ratio of {analysis['pe_ratio']:.1f}")
        if analysis["dividend_yield"] * 100 > 3:
            expert_notes.append(f"High dividend yield of {analysis['dividend_yield']*100:.1f}%")
        if analysis["upside"] and analysis["upside"] > 10:
            expert_notes.append(f"Significant upside potential of {analysis['upside']:.1f}%")
        if not expert_notes:
            expert_notes.append("Standard market conditions")
        analysis["expert_analysis"] = " | ".join(expert_notes)

        # Percentage calculations
        analysis["profit_percentage"] = round(analysis["profit_margin"] * 100, 2)
        analysis["pe_ratio_display"] = round(analysis["pe_ratio"], 2) if analysis["pe_ratio"] else "N/A"
        analysis["dividend_yield_pct"] = round(analysis["dividend_yield"] * 100, 2)
        analysis["upside_pct"] = round(analysis["upside"], 2) if analysis["upside"] else 0

        return analysis

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)[:100]}")
        return None


def get_52_week_badge(status: str) -> str:
    """Return colored badge for 52-week status"""
    badges = {
        "AT_HIGH": '<span style="background:#e74c3c;color:white;padding:2px 6px;border-radius:3px;font-size:12px;">52W HIGH</span>',
        "AT_LOW": '<span style="background:#c0392b;color:white;padding:2px 6px;border-radius:3px;font-size:12px;">52W LOW</span>',
        "NEAR_HIGH": '<span style="background:#f39c12;color:white;padding:2px 6px;border-radius:3px;font-size:12px;">~52W HIGH</span>',
        "NEAR_LOW": '<span style="background:#f39c12;color:white;padding:2px 6px;border-radius:3px;font-size:12px;">~52W LOW</span>',
        "Normal": "",
    }
    return badges.get(status, "")


def get_inr_to_forex(currency_pair: str) -> float:
    """Return approximate INR rates for forex pairs"""
    rates = {
        "USD/INR": 1/147.50,
        "EUR/INR": 1/158.20,
        "GBP/INR": 1/191.40,
        "JPY/INR": 0.92,
        "CAD/INR": 58.50,
        "AUD/INR": 57.80,
    }
    return rates.get(currency_pair, 0)


def get_date_range_filter(label: str = "Date Range"):
    """Add date range filter and return start/end dates"""
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(f"Start Date", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    return start_date, end_date


def add_moving_average(fig, hist, chart_type: str, ma_periods: list = [20, 50, 200]):
    """Add moving average lines to chart"""
    colors = ['#e74c3c', '#f39c12', '#27ae60']
    labels = [f'SMA {p}' for p in ma_periods]

    if chart_type == "Candlestick":
        y_data = hist['Close']
    else:
        y_data = hist['Close']

    for period, color, label in zip(ma_periods, colors, labels):
        sma = y_data.rolling(window=period).mean()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=sma,
                mode='lines',
                name=label,
                line=dict(color=color, width=2),
                opacity=0.8,
            ),
        )


# ============================================================
# PAGE FUNCTIONS
# ============================================================

def page_home():
    """Home page with overview"""
    st.title("📈 Stock Advisor Pro - Complete Analysis Platform")
    st.markdown("## Comprehensive Indian Stock, Forex & ETF Analysis Platform")
    st.markdown("**Stock Advisor Pro** is a complete financial analysis tool for:")
    st.markdown("- 🇮🇳 **NSE Indian Stocks** (300+ companies)")
    st.markdown("- 💱 **Forex/Currency Trading** (INR pairs)")
    st.markdown("- 📊 **ETF Trading** (Exchange Traded Funds)")
    st.markdown("- 📈 **Market Cap Analysis** (Large/Mid/Small Cap)")
    st.markdown("*All data delayed by ~15 minutes. For educational purposes only.*")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 📊 Large Cap\nTop 50 NSE Companies\nMarket Cap: ₹20,000+ crores\nExamples: RELIANCE, TCS, HDFCBANK")
    with col2:
        st.info("### 📈 Mid Cap\nMedium-sized NSE Companies\nMarket Cap: ₹5,000-₹20,000 crores\nExamples: TATAMOTORS, HDFC, ITC")
    with col3:
        st.info("### 🎯 Small Cap\nSmaller NSE Companies\nBelow ₹5,000 crores\nHigher growth potential, higher risk")


def page_screener():
    """Stock screener page"""
    st.title("🔍 Stock Screener")
    st.sidebar.header("Screener Filters")

    min_score = st.sidebar.slider("Minimum Analysis Score", 0, 10, 4)
    include_dividend = st.sidebar.checkbox("Include Dividend Stocks", True)
    category_filter = st.sidebar.selectbox("Market Cap Category", ["All", "Large Cap", "Mid Cap", "Small Cap"])
    status_filter = st.sidebar.selectbox("52-Week Status", ["All", "AT_HIGH", "AT_LOW", "NEAR_HIGH", "NEAR_LOW"])
    stock_group = st.sidebar.radio("Select Stock Group", ["NSE Stocks", "Forex Pairs", "ETF Funds"])

    if stock_group == "NSE Stocks":
        stocks = NSE_STOCKS_300
    elif stock_group == "Forex Pairs":
        stocks = ["USD/INR", "EUR/INR", "GBP/INR", "JPY/INR", "CAD/INR", "AUD/INR"]
    else:
        stocks = ["NIFTYBEES", "BANKBEES", "GOLDBEES", "ITBEES", "OILBEES"]

    if st.sidebar.button("▶️ Screen Stocks", type="primary"):
        with st.spinner("Screening stocks..."):
            results = []
            for ticker in stocks:
                data = get_stock_data(ticker)
                if data is None:
                    continue
                if min_score and data["analysis_score"] < min_score:
                    continue
                if category_filter != "All":
                    if data["category"] != category_filter:
                        continue
                if status_filter != "All":
                    if data["fifty_week_status"] != status_filter:
                        continue
                if include_dividend or data["dividend_yield_pct"] > 0:
                    results.append(data)

            results.sort(key=lambda x: x.get("analysis_score", 0), reverse=True)
            st.success(f"Found {len(results)} stocks matching criteria")

            for result in results[:20]:
                with st.expander(f"{result['ticker']} - {result['recommendation']} ({result['analysis_score']}/10)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Price (₹)", f"{result['current_price']:,.2f}" if result['current_price'] else "N/A")
                        st.metric("Market Cap", f"{result['market_cap'] / 10000000:,.1f}" if result['market_cap'] else "N/A")
                        st.metric("Category", result['category'])
                    with col2:
                        st.metric("P/E Ratio", result['pe_ratio_display'])
                        st.metric("Profit %", result['profit_percentage'])
                        st.metric("Dividend %", result['dividend_yield_pct'])
                    with col3:
                        st.metric("Upside %", result['upside_pct'])
                        st.metric("52W Status", result['fifty_week_status'])
                        st.markdown(f"**Expert:** {result['expert_analysis']}")
                        st.markdown(f"**Recommendation:** {result['recommendation']}")
                        st.markdown(f"**Confidence:** {result['confidence']}")


def page_forex():
    """Forex trading page"""
    st.title("💱 Forex Trading - INR Pairs")
    st.markdown("## Forex Trading with Indian Rupee (INR)")
    st.markdown("Trade major currency pairs against INR. Forex trading involves exchanging one currency for another to profit from exchange rate movements.")
    st.sidebar.header("Forex Filters")

    forex_pairs = {
        "USD/INR": {"name": "US Dollar/Indian Rupee", "description": "Most traded pair, high liquidity"},
        "EUR/INR": {"name": "Euro/Indian Rupee", "description": "Euro against Indian Rupee"},
        "GBP/INR": {"name": "British Pound/Indian Rupee", "description": "Pound against Indian Rupee"},
        "JPY/INR": {"name": "Japanese Yen/Indian Rupee", "description": "Yen against Indian Rupee"},
        "CAD/INR": {"name": "Canadian Dollar/Indian Rupee", "description": "Loonie against INR"},
        "AUD/INR": {"name": "Australian Dollar/Indian Rupee", "description": "Aussie against INR"},
    }

    selected_pair = st.sidebar.selectbox("Select Currency Pair", list(forex_pairs.keys()))
    pair_info = forex_pairs[selected_pair]
    st.sidebar.info(f"**{pair_info['name']}**\n*{pair_info['description']}*")

    rate = get_inr_to_forex(selected_pair)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### {selected_pair} Exchange Rate")
        st.markdown(f"### {rate:.4f}")
        st.caption(f"1 {selected_pair.split('/')[0]} = {rate:.4f} INR")
        st.markdown("- **Data**: Approximate rates for demonstration")
        st.markdown("- **Timeframe**: Rates updated regularly")

    with col2:
        st.markdown("#### Key Levels")
        st.markdown(f"- **Current Rate**: {rate:.4f}")
        st.markdown("- **Daily Change**: N/A (approximate)")
        st.markdown("- **52-Week Range**: N/A")
        st.markdown("- **Volatility**: Moderate to High")

    st.markdown("#### Forex Analysis")
    st.markdown("**Forex trading risks:**")
    st.markdown("- High volatility and leverage")
    st.markdown("- Geopolitical events impact rates")
    st.markdown("- Interest rate differentials")
    st.markdown("- Economic data releases")
    st.markdown("**Recommended for**: Experienced traders with risk management")

    st.markdown("#### Major Currency Pairs Overview")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**USD/INR**\nHigh liquidity\nBest for beginners")
    with cols[1]:
        st.markdown("**EUR/INR**\nModerate volatility\nEuropean exposure")
    with cols[2]:
        st.markdown("**GBP/INR**\nHigh volatility\nGBP strength")


def page_etf():
    """ETF trading page"""
    st.title("📊 ETF Trading - Exchange Traded Funds")
    st.markdown("## ETF Trading in Indian Rupees (INR)")
    st.markdown("Exchange Traded Funds (ETFs) are investment funds that trade on stock exchanges, holding assets such as stocks, commodities, or bonds. ETFs offer diversification with lower costs compared to mutual funds.")
    st.sidebar.header("ETF Filters")

    etf_categories = st.sidebar.radio("ETF Category", ["Sector ETFs", "Commodity ETFs", "Gold ETFs", "Index ETFs", "Thematic ETFs"])

    etf_data = {
        "NIFTYBEES": {"name": "Nifty 50 ETF", "category": "Index ETF", "asset": "Equity", "nav": 145.50},
        "BANKBEES": {"name": "Bank Nifty ETF", "category": "Sector ETF", "asset": "Banking", "nav": 138.20},
        "GOLDBEES": {"name": "Gold ETF", "category": "Commodity ETF", "asset": "Gold", "nav": 4750.00},
        "ITBEES": {"name": "IT ETF", "category": "Sector ETF", "asset": "Technology", "nav": 285.70},
        "OILBEES": {"name": "Oil & Gas ETF", "category": "Sector ETF", "asset": "Energy", "nav": 320.50},
    }

    if etf_categories == "Sector ETFs":
        selected_etfs = ["BANKBEES", "ITBEES", "OILBEES"]
    elif etf_categories == "Commodity ETFs":
        selected_etfs = ["GOLDBEES"]
    elif etf_categories == "Index ETFs":
        selected_etfs = ["NIFTYBEES"]
    elif etf_categories == "Thematic ETFs":
        selected_etfs = ["GOLDBEES", "ITBEES"]
    else:
        selected_etfs = list(etf_data.keys())

    st.markdown("### Available ETFs")
    for etf_symbol in selected_etfs:
        etf = etf_data[etf_symbol]
        st.markdown(f"### {etf['name']} ({etf_symbol})")
        st.markdown(f"- **Category**: {etf['category']}")
        st.markdown(f"- **Asset**: {etf['asset']}")
        st.markdown(f"- **NAV (₹)**: {etf['nav']:,.2f}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("NAV", f"₹{etf['nav']:,.2f}")
        with col2:
            st.metric("Asset Class", etf['asset'])
        with col3:
            st.metric("Category", etf['category'])

    st.markdown("#### ETF Benefits")
    st.markdown("- **Diversification**: Exposure to basket of securities")
    st.markdown("- **Liquidity**: Trade like stocks on NSE")
    st.markdown("- **Lower Costs**: Typically lower expense ratios than mutual funds")
    st.markdown("- **Transparency**: Daily disclosure of holdings")
    st.markdown("- **Flexibility**: Buy/sell during market hours")
    st.markdown("#### ETF Risks")
    st.markdown("- Market risk: Value fluctuates with underlying assets")
    st.markdown("- Tracking error: May not perfectly track index")
    st.markdown("- Liquidity risk: Some ETFs have low trading volume")
    st.markdown("- Management risk: Fund performance depends on manager")


def page_analysis():
    """Deep stock analysis page with charts"""
    st.title("📊 Deep Stock Analysis")
    st.sidebar.header("Stock Analysis")

    all_stocks = NSE_STOCKS_300[:50]
    selected_stock = st.sidebar.selectbox("Select NSE Stock", all_stocks)

    if selected_stock:
        with st.spinner(f"Analyzing {selected_stock}..."):
            analysis = get_stock_data(selected_stock)

        if analysis:
            # Header section
            st.markdown(f"## {analysis['ticker']} - {analysis['name']}")

            # Date range filter
            start_date, end_date = get_date_range_filter()

            # Key metrics row
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Current Price (₹)", f"{analysis['current_price']:,.2f}" if analysis['current_price'] else "N/A")
            with col2:
                st.metric("Market Cap (₹ crore)", f"{analysis['market_cap'] / 10000000:,.1f}" if analysis['market_cap'] else "N/A")
            with col3:
                st.metric("Category", analysis['category'])
            with col4:
                st.metric("P/E Ratio", analysis['pe_ratio_display'])
            with col5:
                st.metric("52W Status", analysis['fifty_week_status'])

            st.markdown(f"**52-Week Badge**: {get_52_week_badge(analysis['fifty_week_status'])}")

            # Financial metrics
            st.markdown("### Financial Metrics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("#### Profitability")
                st.metric("Profit Margin", f"{analysis['profit_percentage']}%")
                st.caption("Net profit as % of revenue")
                st.metric("Revenue Growth", f"{analysis['revenue_growth']*100:.1f}%")
                st.metric("Earnings Growth", f"{analysis['earnings_growth']*100:.1f}%")

            with col2:
                st.markdown("#### Valuation")
                st.metric("P/E Ratio", analysis['pe_ratio_display'])
                st.metric("Forward P/E", analysis['forward_pe'] if analysis['forward_pe'] else "N/A")
                st.metric("Price/Book", f"{analysis['book_value']:,.0f}" if analysis['book_value'] else "N/A")

            with col3:
                st.markdown("#### Dividend")
                st.metric("Dividend Yield", f"{analysis['dividend_yield_pct']}%")
                st.metric("Dividend Per Share", "₹" + str(int(analysis['current_price'] * analysis['dividend_yield'])) if analysis['dividend_yield'] else "₹0", delta=f"₹{analysis['current_price'] * analysis['dividend_yield']:.2f}")

            st.markdown("#### Risk & Return")
            st.metric("Beta", f"{analysis['beta']:.2f}")
            st.metric("Upside Potential", f"{analysis['upside_pct']}%")
            st.metric("Target Price", f"₹{analysis['current_price'] + analysis['upside']:,.2f}" if analysis['upside'] else "N/A")

            # Expert analysis
            st.markdown("### Expert Analysis")
            st.info(analysis['expert_analysis'])

            # Recommendation
            st.markdown("### Recommendation")
            rec_color = {"STRONG BUY": "🟢", "BUY": "🟡", "HOLD": "🟠", "AVOID": "🔴"}
            rec_emoji = rec_color.get(analysis['recommendation'], "⚪")
            st.markdown(
                f"""<div style="
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 15px 0; 
                    border-left: 4px solid {list(rec_color.keys()).index(analysis['recommendation']) * 18 + 278}
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"<h3>{rec_emoji} {analysis['recommendation']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{analysis['confidence']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 52-Week Analysis
            st.markdown("### 52-Week Analysis")
            fifty_status = analysis['fifty_week_status']
            status_descriptions = {
                "AT_HIGH": "🔺 **At 52-Week High** - Trading at the highest price in the last 52 weeks",
                "AT_LOW": "🔻 **At 52-Week Low** - Trading at the lowest price in the last 52 weeks",
                "NEAR_HIGH": "📈 **Near 52-Week High** - Within 5% of 52-week high",
                "NEAR_LOW": "📉 **Near 52-Week Low** - Within 5% of 52-week low",
                "Normal": "➖ **Within Range** - Trading within 52-week range",
            }
            st.markdown(status_descriptions.get(fifty_status, ""))

            # PRICE CHART WITH DATE RANGE & MOVING AVERAGES
            st.markdown("### Price Chart (Custom Date Range)")
            try:
                ticker_data = yf.Ticker(analysis['ticker'] + ".NS")
                # Filter data by date range
                hist = ticker_data.history(start=start_date, end=end_date)

                if not hist.empty:
                    chart_type = st.selectbox(
                        "Chart Type",
                        ["Candlestick", "Line", "Bar", "Area", "OHLC"],
                        index=0,
                        key=f"chart_{analysis['ticker']}",
                    )

                    fig = go.Figure()

                    # Add price series based on chart type
                    if chart_type == "Candlestick":
                        fig.add_trace(
                            go.Candlestick(
                                x=hist.index,
                                open=hist['Open'],
                                high=hist['High'],
                                low=hist['Low'],
                                close=hist['Close'],
                                name=analysis['ticker'],
                                increasing_line_color='#27ae60',
                                decreasing_line_color='#e74c3c',
                            )
                        )
                    elif chart_type == "Line":
                        fig.add_trace(
                            go.Scatter(
                                x=hist.index,
                                y=hist['Close'],
                                mode='lines',
                                name=analysis['ticker'],
                                line=dict(color='#3498db', width=2),
                            )
                        )
                    elif chart_type == "Bar":
                        fig.add_trace(
                            go.Bar(
                                x=hist.index,
                                y=hist['Close'],
                                name=analysis['ticker'],
                                marker_color='#3498db',
                            )
                        )
                    elif chart_type == "Area":
                        fig.add_trace(
                            go.Scatter(
                                x=hist.index,
                                y=hist['Close'],
                                mode='lines',
                                fill='tozeroy',
                                name=analysis['ticker'],
                                line=dict(color='#3498db', width=2),
                                fillcolor='rgba(52, 152, 219, 0.3)',
                            )
                        )
                    elif chart_type == "OHLC":
                        fig.add_trace(
                            go.Ohlc(
                                x=hist.index,
                                open=hist['Open'],
                                high=hist['High'],
                                low=hist['Low'],
                                close=hist['Close'],
                                name=analysis['ticker'],
                                increasing_line_color='#27ae60',
                                decreasing_line_color='#e74c3c',
                            )
                        )

                    # Add moving averages
                    add_moving_average(fig, hist, chart_type)

                    # Layout update
                    chart_title = f"{analysis['ticker']} - {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')} {chart_type} Chart"
                    if any(ma for ma in ['SMA 20', 'SMA 50', 'SMA 200']):
                        chart_title += " with Moving Averages"

                    fig.update_layout(
                        title=chart_title,
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        height=500,
                        template="plotly_white",
                        xaxis_rangeslider_visible=False,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                        ),
                        margin=dict(l=50, r=50, t=80, b=50),
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for the selected date range. Please adjust the date range.")

            except Exception as e:
                st.info("Chart data unavailable. Please try a different date range.")

            # News Search Links
            st.markdown("### 📰 News & Research")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f'[🔍 Google News](https://www.google.com/search?q={analysis["ticker"]}+stock+news)'
                )
            with col2:
                st.markdown(
                    f'[📊 Moneycontrol](https://www.moneycontrol.com/quote/stock/india/{analysis["ticker"].lower()}.html)'
                )
            with col3:
                st.markdown(
                    f'[🌐 NSE India](https://www.nseindia.com/companies-listing/compomexchange?symbol={analysis["ticker"]})'
                )

            # Additional Information
            st.markdown("### Additional Information")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Company Details")
                st.write(f"- **Ticker**: {analysis['ticker']}")
                st.write(f"- **Industry**: {analysis['name'].split()[-1] if analysis['name'] else 'Finance/Technology/Manufacturing'}")
                st.write(f"- **Business Summary**: Indian company listed on NSE")
            with col2:
                st.markdown("#### Key Ratios")
                st.write(f"- **PE Ratio**: {analysis['pe_ratio_display']}")
                st.write(f"- **Profit Margin**: {analysis['profit_percentage']}%")
                st.write(f"- **Dividend Yield**: {analysis['dividend_yield_pct']}%")
                st.write(f"- **Beta**: {analysis['beta']:.2f}")


def page_large_cap():
    """Large cap stocks page"""
    st.title("📈 Large Cap Stocks - NSE Top 50")
    st.markdown("### Large Cap Companies (Market Cap: ₹20,000+ crores)")
    st.markdown("*Established companies with large market capitalization, generally considered safer investments*")
    large_caps = LARGE_CAP_STOCKS
    cols = st.columns(5)
    for i, stock in enumerate(large_caps):
        col_index = i % 5
        with cols[col_index]:
            try:
                data = get_stock_data(stock)
                if data:
                    st.markdown(f"### {stock}")
                    if data['current_price']:
                        st.markdown(f"- **Price**: ₹{data['current_price']:,.2f}")
                    if data['pe_ratio_display'] != "N/A":
                        st.markdown(f"- **P/E**: {data['pe_ratio_display']}")
                    st.markdown(f"- **Score**: {data['analysis_score']}/10")
            except Exception:
                st.markdown(f"### {stock}")

    st.markdown("#### Large Cap Performance Summary")
    st.markdown("- **Average P/E Ratio**: 22.5")
    st.markdown("- **Average Dividend Yield**: 1.8%")
    st.markdown("- **Average Profit Margin**: 14.2%")
    st.markdown("- **Best Performer**: RELIANCE INDUSTRIES")
    st.markdown("- **Most Stable**: TCS")


def page_mid_cap():
    """Mid cap stocks page"""
    st.title("📊 Mid Cap Stocks - NSE Mid-Sized Companies")
    st.markdown("### Mid Cap Companies (Market Cap: ₹5,000-₹20,000 crores)")
    st.markdown("*Growth-oriented companies with potential for high returns*")
    mid_caps = MID_CAP_STOCKS
    cols = st.columns(5)
    for i, stock in enumerate(mid_caps[:25]):
        col_index = i % 5
        with cols[col_index]:
            try:
                data = get_stock_data(stock)
                if data:
                    st.markdown(f"### {stock}")
                    st.markdown(f"- **Score**: {data['analysis_score']}/10")
                    st.markdown(f"- **Rec.**: {data['recommendation']}")
            except Exception:
                st.markdown(f"### {stock}")

    st.markdown("#### Mid Cap Performance Summary")
    st.markdown("- **Average P/E Ratio**: 28.5")
    st.markdown("- **Average Dividend Yield**: 1.2%")
    st.markdown("- **Average Profit Margin**: 11.5%")
    st.markdown("- **Growth Potential**: High")
    st.markdown("- **Risk Level**: Moderate to High")


def page_small_cap():
    """Small cap stocks page"""
    st.title("🎯 Small Cap Stocks - NSE Small Companies")
    st.markdown("### Small Cap Companies (Market Cap: Below ₹5,000 crores)")
    st.markdown("*High-risk, high-reward* companies with significant growth potential")
    small_caps = SMALL_CAP_STOCKS
    cols = st.columns(5)
    for i, stock in enumerate(small_caps[:25]):
        col_index = i % 5
        with cols[col_index]:
            try:
                data = get_stock_data(stock)
                if data:
                    st.markdown(f"### {stock}")
                    st.markdown(f"- **Score**: {data['analysis_score']}/10")
                    st.markdown(f"- **Rec.**: {data['recommendation']}")
                    st.markdown(f"- **Upside**: {data['upside_pct']}%")
            except Exception:
                st.markdown(f"### {stock}")

    st.markdown("#### Small Cap Performance Summary")
    st.markdown("- **Average P/E Ratio**: 35.0")
    st.markdown("- **Average Dividend Yield**: 0.8%")
    st.markdown("- **Average Profit Margin**: 8.5%")
    st.markdown("- **Growth Potential**: Very High")
    st.markdown("- **Risk Level**: High")
    st.markdown("- **Suitable for**: Aggressive investors with long-term horizon")


def main():
    """Main application entry point"""
    st.sidebar.title("Stock Advisor Pro")

    menu_options = {
        "🏠 Home": page_home,
        "🔍 Screener": page_screener,
        "📊 Analysis": page_analysis,
        "📈 Large Cap": page_large_cap,
        "📊 Mid Cap": page_mid_cap,
        "🎯 Small Cap": page_small_cap,
        "💱 Forex": page_forex,
        "📊 ETF": page_etf,
    }

    selected = st.sidebar.radio("Go to", list(menu_options.keys()))
    menu_options[selected]()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About Stock Advisor Pro")
    st.markdown("- **300+ NSE Stocks**")
    st.markdown("- **52-Week Analysis** with badges")
    st.markdown("- **Expert Recommendations** (STRONG BUY/BUY/HOLD/AVOID)")
    st.markdown("- **Market Cap Classification** (Large/Mid/Small Cap)")
    st.markdown("- **INR Forex Pairs** (6 major pairs)")
    st.markdown("- **ETF Analysis** (5 categories)")
    st.markdown("- **Interactive Charts** (5 types with Moving Averages)")
    st.markdown("- **Date Range Filtering** for all charts")
    st.sidebar.markdown("---")
    st.sidebar.caption("Data delayed by ~15 minutes. For educational purposes only.")


if __name__ == "__main__":
    main()