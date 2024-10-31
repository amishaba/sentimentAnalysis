import streamlit as st
import yfinance as yf
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Download required NLTK data
nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Initialize NewsAPI client (you'll need to replace with your API key)
newsapi = NewsApiClient(api_key='206c41dcba0e456981dd7438404aaa62')


def categorize_sentiment(score):
    """Categorize sentiment scores into meaningful labels"""
    if score >= 0.5:
        return "Very Positive"
    elif score >= 0.1:
        return "Positive"
    elif score > -0.1:
        return "Neutral"
    elif score > -0.5:
        return "Negative"
    else:
        return "Very Negative"


# Streamlit app setup
st.set_page_config(page_title="Financial Sentiment Dashboard", layout="wide")
st.title("Real-time Financial Sentiment Dashboard")

# Sidebar for user input
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=30, max_value=300, value=60)

def get_stock_data(ticker):
    """Fetch real-time stock data"""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")
    return hist, stock.info

# def get_news_sentiment(ticker):
#     """Fetch and analyze news sentiment"""
#     try:
#         # Get news articles
#         news = newsapi.get_everything(
#             q=ticker,
#             language='en',
#             sort_by='publishedAt',
#             page_size=10
#         )
        
#         # Analyze sentiment for each article
#         sentiments = []
#         for article in news['articles']:
#             sentiment = sia.polarity_scores(article['title'] + ' ' + article['description'])
#             sentiments.append({
#                 'title': article['title'],
#                 'sentiment': sentiment['compound'],
#                 'time': article['publishedAt'],
#                 'url': article['url']
#             })
        
#         return pd.DataFrame(sentiments)
#     except Exception as e:
#         st.error(f"Error fetching news: {str(e)}")
#         return pd.DataFrame()

def get_news_sentiment(ticker):
    """Fetch and analyze news sentiment"""
    try:
        # Get company name from yfinance
        company = yf.Ticker(ticker)
        company_name = company.info.get('longName', ticker)
        
        # Create a more specific search query
        search_query = f'"{ticker}" OR "{company_name}" stock OR "{company_name}" shares OR "{company_name}" earnings'
        
        # Get news articles
        news = newsapi.get_everything(
            q=search_query,
            language='en',
            sort_by='relevancy',
            page_size=10,
            from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        )
        
        # Only process if we have articles
        if news['articles']:
            sentiments = []
            for article in news['articles']:
                # Extract title and description from article, convert None to empty string
                title = article.get('title', '') or ''
                description = article.get('description', '') or ''
                
                # Skip if both title and description are empty
                if not title and not description:
                    continue
                    
                # Combine text for sentiment analysis
                text_to_analyze = f"{title} {description}".strip()
                
                sentiment = sia.polarity_scores(text_to_analyze)
                sentiments.append({
                    'title': title,  # Use our safe title value
                    'sentiment': sentiment['compound'],
                    'sentiment_category': categorize_sentiment(sentiment['compound']),
                    'positive': sentiment['pos'],
                    'negative': sentiment['neg'],
                    'neutral': sentiment['neu'],
                    'time': article['publishedAt'],
                    'url': article['url']
                })
            
            return pd.DataFrame(sentiments)
        else:
            st.warning(f"No news articles found for {ticker}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return pd.DataFrame()

def main():
    # Create placeholders for real-time updates
    stock_price_chart = st.empty()
    sentiment_chart = st.empty()
    news_container = st.empty()
    
    while True:
        try:
            # Fetch real-time data
            stock_data, stock_info = get_stock_data(ticker)
            sentiment_df = get_news_sentiment(ticker)
            
            # Create stock price chart
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name='Stock Price'
            ))
            fig_price.update_layout(
                title=f"{ticker} Stock Price",
                yaxis_title="Price ($)",
                height=400
            )
            stock_price_chart.plotly_chart(fig_price, use_container_width=True)
            
            # Display company info
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${stock_data['Close'][-1]:.2f}")
            col2.metric("Market Cap", f"${stock_info['marketCap']:,.0f}")
            col3.metric("Volume", f"{stock_info['volume']:,}")
            
            if not sentiment_df.empty:
                # Sentiment distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sentiment trends chart
                    fig_sentiment = go.Figure()
                    fig_sentiment.add_trace(go.Scatter(
                        x=pd.to_datetime(sentiment_df['time']),
                        y=sentiment_df['sentiment'],
                        mode='markers+lines',
                        name='News Sentiment'
                    ))
                    fig_sentiment.update_layout(
                        title="News Sentiment Trend",
                        yaxis_title="Sentiment Score",
                        height=300
                    )
                    st.plotly_chart(fig_sentiment, use_container_width=True)

                with col2:
                    # Sentiment distribution pie chart
                    sentiment_counts = sentiment_df['sentiment_category'].value_counts()
                    fig_dist = go.Figure(data=[go.Pie(
                        labels=sentiment_counts.index,
                        values=sentiment_counts.values,
                        hole=.3
                    )])
                    fig_dist.update_layout(
                        title="Sentiment Distribution",
                        height=300
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)

                # Sentiment statistics
                st.markdown("### Sentiment Statistics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Average Sentiment", f"{sentiment_df['sentiment'].mean():.2f}")
                col2.metric("Most Common Sentiment", sentiment_df['sentiment_category'].mode()[0])
                col3.metric("Positive Articles", f"{(sentiment_df['sentiment'] > 0).sum()}/{len(sentiment_df)}")
                col4.metric("Negative Articles", f"{(sentiment_df['sentiment'] < 0).sum()}/{len(sentiment_df)}")

                # Display recent news with enhanced sentiment information
                st.markdown("### Recent News")
                for _, row in sentiment_df.iterrows():
                    sentiment_color = "green" if row['sentiment'] > 0 else "red" if row['sentiment'] < 0 else "gray"
                    st.markdown(
                        f"- [{row['title']}]({row['url']}) \n"
                        f"  - Sentiment: <span style='color:{sentiment_color}'>{row['sentiment_category']}</span> "
                        f"(Score: {row['sentiment']:.2f})\n"
                        f"  - Details: {row['positive']*100:.0f}% Positive, {row['negative']*100:.0f}% Negative, "
                        f"{row['neutral']*100:.0f}% Neutral",
                        unsafe_allow_html=True
                    )
            
            # Wait for refresh
            time.sleep(refresh_rate)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            time.sleep(refresh_rate)

if __name__ == "__main__":
    main()