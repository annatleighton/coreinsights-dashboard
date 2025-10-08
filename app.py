import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CoreInsights",
    page_icon="🎯",
    layout="wide"
)

# API Keys (in production, use st.secrets or environment variables)
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
            'volume': int(data['volume']),
            'previous_close': float(data['previous_close'])
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

# Main UI
st.title("CoreInsights")
st.markdown("---")

# Sidebar for input
with st.sidebar:
    st.header("🔍 Search Parameters")
    
    # Preset companies
    preset = st.selectbox(
        "Quick Select",
        ["Custom", "Tesla", "Apple", "Microsoft", "Amazon", "Google"]
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
    else:
        default_ticker = "TSLA"
        default_company = "Tesla"
        default_wiki = "Tesla,_Inc."
    
    # Always show input fields with preset values
    ticker = st.text_input("Stock Ticker", default_ticker).upper()
    company_name = st.text_input("Company Name", default_company)
    wiki_name = st.text_input("Wikipedia Page Name", default_wiki)
    
    max_news = st.slider("Number of News Articles", 3, 10, 5)
    
    search_button = st.button("Generate Report", type="primary", use_container_width=True)
    
    # Add a reset button if a report has been generated
    if 'report_generated' in st.session_state and st.session_state.report_generated:
        if st.button("🔄 New Search", use_container_width=True):
            st.session_state.report_generated = False
            st.rerun()

# Main content area
if search_button:
    st.session_state.report_generated = True
    with st.spinner(f"Fetching data for {company_name}..."):
        # Fetch all data
        stock_data = fetch_stock_quote(ticker)
        news_articles = fetch_news(company_name, max_news)
        wiki_data = fetch_wikipedia_info(wiki_name)
        
        if not stock_data:
            st.error("❌ Failed to fetch stock data. Please check the ticker symbol.")
        else:
            # Company Overview Section
            st.header("🏢 Company Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Company", stock_data['name'])
            with col2:
                st.metric("Ticker", stock_data['symbol'])
            with col3:
                st.metric("Exchange", stock_data['exchange'])
            
            if wiki_data:
                st.info(f"**{wiki_data['description']}**")
                with st.expander("📖 Read More"):
                    st.write(wiki_data['extract'])
                    st.markdown(f"[View on Wikipedia]({wiki_data['url']})")
            
            st.markdown("---")
            
            # Stock Performance Section
            st.header("📊 Stock Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${stock_data['price']:.2f}",
                    f"{stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)"
                )
            
            with col2:
                st.metric("Day High", f"${stock_data['high']:.2f}")
            
            with col3:
                st.metric("Day Low", f"${stock_data['low']:.2f}")
            
            with col4:
                st.metric("Volume", f"{stock_data['volume']:,}")
            
            # Additional stock info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Previous Close", f"${stock_data['previous_close']:.2f}")
            with col2:
                change_amount = stock_data['price'] - stock_data['previous_close']
                st.metric("Change Amount", f"${change_amount:+.2f}")
            
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
                st.warning("No recent news articles found")
            
            st.markdown("---")
            
            # Download Report
            st.header("💾 Export Report")
            
            report = {
                'company': {
                    'name': stock_data['name'],
                    'ticker': stock_data['symbol'],
                    'exchange': stock_data['exchange']
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
                    label="📥 Download JSON Report",
                    data=report_json,
                    file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
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