# Financial Sentiment Dashboard

A real-time financial analytics dashboard that combines stock market data with news sentiment analysis to provide comprehensive market insights. This Streamlit-based application fetches live stock data and relevant news articles, analyzing the sentiment of market coverage to help investors make more informed decisions.

## Features

- Real-time stock price tracking with interactive charts
- News sentiment analysis using NLTK's VADER sentiment analyzer
- Live sentiment trend visualization
- Comprehensive company metrics display
- Automated news fetching and analysis for selected stocks
- Customizable refresh rates for real-time updates
- Sentiment distribution visualization through interactive charts
- Detailed news article listing with sentiment scores

## Requirements

- Python 3.7+
- Streamlit
- yfinance
- pandas
- NLTK
- NewsAPI
- plotly
- datetime

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install streamlit yfinance pandas nltk newsapi-python plotly
```
3. Download required NLTK data:
```python
import nltk
nltk.download('vader_lexicon')
```
4. Replace the NewsAPI key in the code with your own key from [NewsAPI](https://newsapi.org/)

## Usage

1. Run the dashboard:
```bash
streamlit run app.py
```

2. Enter a stock ticker in the sidebar (default is "AAPL")
3. Adjust the refresh rate as needed (30-300 seconds)
4. Monitor real-time stock prices, sentiment analysis, and news coverage

## Dashboard Components

- **Stock Price Chart**: Real-time price tracking with interactive visualization
- **Key Metrics**: Current price, market cap, and volume
- **Sentiment Analysis**:
  - Sentiment trend chart
  - Sentiment distribution pie chart
  - Statistical breakdown of positive/negative coverage
- **News Feed**: Recent articles with sentiment scores and detailed breakdowns

## Customization

The dashboard allows for several customizations:
- Stock ticker selection
- Data refresh rate
- News article count
- Time period for historical data

## Technical Details

- Stock data is fetched using the yfinance API
- News articles are retrieved using the NewsAPI
- Sentiment analysis is performed using NLTK's VADER sentiment analyzer
- Visualization is handled by Plotly and Streamlit
- Data is automatically refreshed based on user-defined intervals


## Note

Make sure to replace the NewsAPI key in the code with your own key to ensure proper functionality. You can obtain a key by registering at [NewsAPI](https://newsapi.org/).
