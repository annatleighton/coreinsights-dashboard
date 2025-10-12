import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CoreInsights",
    layout="wide"
)

# API Keys
TWELVE_DATA_API_KEY = "669aa5408f794ee09a609da9b11a82e0"
NEWS_API_KEY = "642f006c86ec41f8958c599de26a7b26"

def fetch_stock_quote(ticker):
    url = f"https://api.twelvedata.com/quote?symbol={ticker}"
    headers = {"Authorization": f"apikey {TWELVE_DATA_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get('status') == 'error' or not data.get('symbol'):
            return None
        
        return {
            'symbol': data['symbol'],
            'name': data['name'],
            'exchange': data['exchange'],
            'price': float(data['close']),
            'change': float(data['change']),
            'change_percent': float(data['percent_change']),
            'high': float(data['high']),
            'low': float(data['low']),
            'previous_close': float(data['previous_close']),
            'fifty_two_week': data.get('fifty_two_week', {}),
            'range': f"{data['low']} - {data['high']}"
        }
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def fetch_news(company_name, max_articles=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,
        'sortBy': 'publishedAt',
        'pageSize': max_articles,
        'language': 'en',
        'apiKey': NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'error':
            return []
        
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'title': article['title'],
                'description': article.get('description', 'No description'),
                'source': article['source']['name'],
                'published_at': article['publishedAt'],
                'url': article['url']
            })
        return articles
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def fetch_wikipedia_info(wiki_page_name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_page_name}"
    headers = {'User-Agent': 'CompetitorDashboard/1.0 (Educational Project; Python/requests)'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return {
            'title': data['title'],
            'description': data.get('description', ''),
            'extract': data.get('extract', ''),
            'url': data['content_urls']['desktop']['page']
        }
    except Exception as e:
        return None

def find_wikipedia_page(company_name):
    """Try different Wikipedia page name variations for a company"""
    # Try different common patterns
    variations = [
        company_name,  # e.g., "Microsoft"
        f"{company_name}_Inc.",  # e.g., "Apple_Inc."
        f"{company_name},_Inc.",  # e.g., "Tesla,_Inc."
        f"{company_name}_(company)",  # e.g., "Amazon_(company)"
        company_name.replace(" ", "_"),  # Replace spaces with underscores
    ]
    
    for variation in variations:
        result = fetch_wikipedia_info(variation)
        if result:
            return result
    
    return None

# Main UI
st.title("CoreInsights")
st.markdown("---")

# Sidebar for input
with st.sidebar:
    st.header("🔍 Search Parameters")
    
    # Preset companies
    preset = st.selectbox(
        "Quick Select",
        ["Custom", "Tesla", "Apple", "Microsoft", "Amazon", "Google", "Meta", "Netflix", "Nvidia", "Intel", "AMD", "Walmart", "JPMorgan", "Goldman Sachs", "Boeing", "Coca-Cola", "Disney", "Nike", "Visa", "McDonald's"]
    )
    
    # Set default values based on preset
    if preset == "Tesla":
        default_ticker = "TSLA"
        default_company = "Tesla"
        default_wiki = "Tesla,_Inc."
    elif preset == "Apple":
        default_ticker = "AAPL"
        default_company = "Apple"
        default_wiki = "Apple_Inc."
    elif preset == "Microsoft":
        default_ticker = "MSFT"
        default_company = "Microsoft"
        default_wiki = "Microsoft"
    elif preset == "Amazon":
        default_ticker = "AMZN"
        default_company = "Amazon"
        default_wiki = "Amazon_(company)"
    elif preset == "Google":
        default_ticker = "GOOGL"
        default_company = "Google"
        default_wiki = "Google"
    elif preset == "Meta":
        default_ticker = "META"
        default_company = "Meta"
        default_wiki = "Meta_Platforms"
    elif preset == "Netflix":
        default_ticker = "NFLX"
        default_company = "Netflix"
        default_wiki = "Netflix"
    elif preset == "Nvidia":
        default_ticker = "NVDA"
        default_company = "Nvidia"
        default_wiki = "Nvidia"
    elif preset == "Intel":
        default_ticker = "INTC"
        default_company = "Intel"
        default_wiki = "Intel"
    elif preset == "AMD":
        default_ticker = "AMD"
        default_company = "AMD"
        default_wiki = "Advanced_Micro_Devices"
    elif preset == "Walmart":
        default_ticker = "WMT"
        default_company = "Walmart"
        default_wiki = "Walmart"
    elif preset == "JPMorgan":
        default_ticker = "JPM"
        default_company = "JPMorgan Chase"
        default_wiki = "JPMorgan_Chase"
    elif preset == "Goldman Sachs":
        default_ticker = "GS"
        default_company = "Goldman Sachs"
        default_wiki = "Goldman_Sachs"
    elif preset == "Boeing":
        default_ticker = "BA"
        default_company = "Boeing"
        default_wiki = "Boeing"
    elif preset == "Coca-Cola":
        default_ticker = "KO"
        default_company = "Coca-Cola"
        default_wiki = "The_Coca-Cola_Company"
    elif preset == "Disney":
        default_ticker = "DIS"
        default_company = "Disney"
        default_wiki = "The_Walt_Disney_Company"
    elif preset == "Nike":
        default_ticker = "NKE"
        default_company = "Nike"
        default_wiki = "Nike,_Inc."
    elif preset == "Visa":
        default_ticker = "V"
        default_company = "Visa"
        default_wiki = "Visa_Inc."
    elif preset == "McDonald's":
        default_ticker = "MCD"
        default_company = "McDonald's"
        default_wiki = "McDonald%27s"
    else:
        default_ticker = ""
        default_company = ""
        default_wiki = ""
    
    # Three optional input fields
    st.caption("Enter at least one field to search")
    ticker = st.text_input("Stock Ticker (optional)", default_ticker).upper()
    company_name = st.text_input("Company Name (optional)", default_company)
    wiki_name = st.text_input("Wikipedia Page Name (optional)", default_wiki)
    
    max_news = st.slider("Number of News Articles", 3, 10, 5)
    
    search_button = st.button("Generate Report", type="primary", use_container_width=True)
    
    # Add a reset button if a report has been generated
    if 'report_generated' in st.session_state and st.session_state.report_generated:
        if st.button("🔄 New Search", use_container_width=True):
            st.session_state.report_generated = False
            st.rerun()

# Main content area
if search_button:
    # Check if at least one field is provided
    if not ticker and not company_name and not wiki_name:
        st.error("⚠️ Please enter at least one search parameter (Stock Ticker, Company Name, or Wikipedia Page Name)")
    else:
        st.session_state.report_generated = True
        
        # Initialize variables
        stock_data = None
        news_articles = []
        wiki_data = None
        display_company_name = company_name or "Unknown Company"
        
        with st.spinner(f"Fetching data..."):
            # Fetch stock data if ticker is provided
            if ticker:
                stock_data = fetch_stock_quote(ticker)
                if stock_data:
                    display_company_name = stock_data['name']
                    # If company name not provided, use the one from stock data
                    if not company_name:
                        company_name = stock_data['name']
            
            # Fetch news if company name is available
            if company_name:
                news_articles = fetch_news(company_name, max_news)
            
            # Fetch Wikipedia data if wiki name is provided
            if wiki_name:
                wiki_data = fetch_wikipedia_info(wiki_name)
            elif company_name:
                # Try to find Wikipedia page using company name if wiki name not provided
                wiki_data = find_wikipedia_page(company_name)
            
            # Display results
            # Company Overview Section
            st.header("🏢 Company Overview")
            
            if stock_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Company", stock_data['name'])
                with col2:
                    st.metric("Ticker", stock_data['symbol'])
                with col3:
                    st.metric("Exchange", stock_data['exchange'])
            else:
                st.info(f"**{display_company_name}**")
                if ticker:
                    st.warning(f"⚠️ Could not fetch stock data for ticker: {ticker}")
            
            if wiki_data:
                st.info(f"**{wiki_data['description']}**")
                st.write(wiki_data['extract'])
                st.markdown(f"[View on Wikipedia]({wiki_data['url']})")
            else:
                if wiki_name or company_name:
                    st.warning("Wikipedia information not available for this company")
            
            st.markdown("---")
            
            # Stock Performance Section (only if stock data available)
            if stock_data:
                st.header("📊 Stock Performance")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current Price",
                        f"${stock_data['price']:.2f}",
                        f"{stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)"
                    )
                    st.metric("Previous Close", f"${stock_data['previous_close']:.2f}")
                
                with col2:
                    st.metric("Day High", f"${stock_data['high']:.2f}")
                    st.metric("Day Low", f"${stock_data['low']:.2f}")
                
                with col3:
                    # 52-week range if available
                    if stock_data.get('fifty_two_week'):
                        high_val = float(stock_data['fifty_two_week'].get('high', 0)) if 'high' in stock_data['fifty_two_week'] else None
                        low_val = float(stock_data['fifty_two_week'].get('low', 0)) if 'low' in stock_data['fifty_two_week'] else None
                        
                        if high_val:
                            st.metric("Performance High (Last 12 Months)", f"${high_val:.2f}")
                        if low_val:
                            st.metric("Performance Low (Last 12 Months)", f"${low_val:.2f}")
                
                st.markdown("---")
            
            # News Section
            st.header("📰 Recent News")
            
            if news_articles:
                st.success(f"Found {len(news_articles)} recent articles")
                
                for i, article in enumerate(news_articles, 1):
                    with st.expander(f"📄 {article['title']}"):
                        st.write(f"**Source:** {article['source']}")
                        st.write(f"**Published:** {article['published_at']}")
                        st.write(article['description'])
                        st.markdown(f"[Read full article]({article['url']})")
            else:
                if company_name:
                    st.warning("No recent news articles found")
                else:
                    st.info("Enter a company name to fetch news articles")
            
            st.markdown("---")
            
            # Download Report (only if we have some data)
            if stock_data or news_articles or wiki_data:
                st.header("💾 Export Report")
                
                report = {
                    'company': {
                        'name': display_company_name,
                        'ticker': stock_data['symbol'] if stock_data else ticker,
                        'exchange': stock_data['exchange'] if stock_data else 'N/A'
                    },
                    'stock': stock_data,
                    'news': news_articles,
                    'wikipedia': wiki_data,
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                report_json = json.dumps(report, indent=2)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Download Report",
                        data=report_json,
                        file_name=f"{ticker or company_name.replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    st.info(f"Report generated at: {report['generated_at']}")

else:
    # Welcome screen
    st.info("👈 Select a company from the sidebar or enter custom details, then click 'Generate Report'")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Stock Data")
        st.write("Real-time stock quotes, prices, and performance metrics")
    
    with col2:
        st.markdown("### 📰 News Feed")
        st.write("Latest news articles about the company")
    
    with col3:
        st.markdown("### 📚 Company Info")
        st.write("Background information from Wikipedia")

# Footer
st.markdown("---")
st.caption("Data sources: Twelve Data API, NewsAPI, Wikipedia API")
