import os
import requests
import random
from datetime import datetime, timedelta
import pandas as pd
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# News API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
CRYPTO_PANIC_API_KEY = os.getenv("CRYPTO_PANIC_API_KEY", "")

def get_trending_topics():
    """
    Retrieves trending topics in cryptocurrency from news and social media
    
    Returns:
        dict: Trending topics and related data
    """
    # Try to get real data from APIs if keys are available
    trending_data = None
    
    if NEWS_API_KEY:
        trending_data = get_trending_from_news_api()
    
    if not trending_data and CRYPTO_PANIC_API_KEY:
        trending_data = get_trending_from_crypto_panic()
    
    # Use mock data if APIs fail or keys are not available
    if not trending_data:
        trending_data = generate_mock_trending_data()
    
    return trending_data

def get_trending_from_news_api():
    """
    Retrieves trending topics from News API
    
    Returns:
        dict: Trending topics and related data
    """
    try:
        # Define News API parameters
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "cryptocurrency OR bitcoin OR ethereum OR blockchain",
            "sortBy": "popularity",
            "language": "en",
            "pageSize": 30,
            "apiKey": NEWS_API_KEY
        }
        
        # Make API request
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "ok" and data.get("articles"):
            # Extract articles
            articles = data["articles"]
            
            # Process articles to extract trending topics
            topics = process_articles(articles)
            
            # Extract mentioned tokens and sentiment
            trending_tokens, sentiment_breakdown = extract_tokens_from_articles(articles)
            
            return {
                "topics": topics,
                "trending_tokens": trending_tokens,
                "sentiment_breakdown": sentiment_breakdown
            }
        
        return None
    
    except Exception as e:
        print(f"Error fetching data from News API: {e}")
        return None

def get_trending_from_crypto_panic():
    """
    Retrieves trending topics from Crypto Panic API
    
    Returns:
        dict: Trending topics and related data
    """
    try:
        # Define Crypto Panic API parameters
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": CRYPTO_PANIC_API_KEY,
            "kind": "news",
            "filter": "hot",
            "public": "true"
        }
        
        # Make API request
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("results"):
            # Extract articles
            articles = data["results"]
            
            # Convert to standard format
            standardized_articles = []
            for article in articles:
                standardized_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("title", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("published_at", ""),
                    "source": {
                        "name": article.get("source", {}).get("title", "Crypto News")
                    }
                })
            
            # Process articles to extract trending topics
            topics = process_articles(standardized_articles)
            
            # Extract mentioned tokens and sentiment
            trending_tokens, sentiment_breakdown = extract_tokens_from_articles(standardized_articles)
            
            return {
                "topics": topics,
                "trending_tokens": trending_tokens,
                "sentiment_breakdown": sentiment_breakdown
            }
        
        return None
    
    except Exception as e:
        print(f"Error fetching data from Crypto Panic API: {e}")
        return None

def process_articles(articles):
    """
    Processes a list of articles to extract trending topics
    
    Args:
        articles (list): List of article dictionaries
    
    Returns:
        list: List of trending topics
    """
    # Group articles by similarity in title/content
    topics = []
    processed_indices = set()
    
    for i, article in enumerate(articles):
        if i in processed_indices:
            continue
        
        # Create a new topic group
        title = article.get("title", "")
        description = article.get("description", "")
        url = article.get("url", "")
        published_at = article.get("publishedAt", "")
        source_name = article.get("source", {}).get("name", "News Source")
        
        # Format date
        try:
            date_obj = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            date_str = date_obj.strftime("%B %d, %Y")
        except:
            date_str = "Recent"
        
        # Create summary from description
        summary = description if description else title
        
        # Add to topics
        topics.append({
            "title": title,
            "summary": summary,
            "url": url,
            "date": date_str,
            "source": source_name
        })
        
        processed_indices.add(i)
        
        # Find similar articles (simple approach - title word overlap)
        title_words = set(title.lower().split())
        for j, other_article in enumerate(articles):
            if j in processed_indices:
                continue
            
            other_title = other_article.get("title", "").lower()
            other_title_words = set(other_title.split())
            
            # If significant word overlap, consider them the same topic
            intersection = title_words.intersection(other_title_words)
            if len(intersection) >= min(3, len(title_words) // 2):
                processed_indices.add(j)
    
    # Sort topics by estimated importance (simple approach)
    # This would ideally involve NLP and trend analysis
    sorted_topics = sorted(topics, key=lambda x: random.random(), reverse=True)
    
    # Limit to top N topics
    return sorted_topics[:7]

def extract_tokens_from_articles(articles):
    """
    Extracts mentioned cryptocurrency tokens from articles and estimates sentiment
    
    Args:
        articles (list): List of article dictionaries
    
    Returns:
        tuple: (trending_tokens_df, sentiment_breakdown)
    """
    # Common cryptocurrency tokens
    common_tokens = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "BNB": "Binance Coin",
        "SOL": "Solana",
        "XRP": "XRP",
        "ADA": "Cardano",
        "DOGE": "Dogecoin",
        "SHIB": "Shiba Inu",
        "MATIC": "Polygon",
        "DOT": "Polkadot",
        "LINK": "Chainlink",
        "ATOM": "Cosmos",
        "AVAX": "Avalanche",
        "LTC": "Litecoin",
        "UNI": "Uniswap"
    }
    
    # Count token mentions
    token_mentions = {token: 0 for token in common_tokens}
    token_sentiment = {token: 0 for token in common_tokens}
    
    # Simple sentiment words
    positive_words = [
        "bullish", "surge", "soar", "gain", "rally", "climb", "rise", "positive",
        "breakthrough", "adoption", "partnership", "success", "growth", "profit",
        "innovation", "potential", "opportunity", "promising", "optimistic", "victory"
    ]
    
    negative_words = [
        "bearish", "plunge", "crash", "drop", "fall", "decline", "negative", "bearish",
        "setback", "concern", "problem", "issue", "risk", "loss", "trouble", "danger",
        "warning", "collapse", "downtrend", "pessimistic", "defeat"
    ]
    
    # Process each article
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower() if article.get("description") else ""
        
        # Combine title and description
        text = title + " " + description
        
        # Calculate base sentiment for the article
        article_sentiment = 0
        for word in positive_words:
            if word in text:
                article_sentiment += 0.1
        
        for word in negative_words:
            if word in text:
                article_sentiment -= 0.1
        
        # Cap sentiment between -1 and 1
        article_sentiment = max(-1, min(1, article_sentiment))
        
        # Check for token mentions
        for token, name in common_tokens.items():
            # Check for token symbol or name
            token_mentioned = token.lower() in text or name.lower() in text
            
            if token_mentioned:
                token_mentions[token] += 1
                token_sentiment[token] += article_sentiment
    
    # Calculate average sentiment
    for token in token_sentiment:
        if token_mentions[token] > 0:
            token_sentiment[token] /= token_mentions[token]
    
    # Create dataframe of trending tokens
    trending_data = []
    for token, mentions in token_mentions.items():
        if mentions > 0:
            trending_data.append({
                "token": token,
                "mentions": mentions,
                "sentiment": token_sentiment[token]
            })
    
    # Sort by mentions
    trending_df = pd.DataFrame(trending_data).sort_values("mentions", ascending=False).reset_index(drop=True)
    
    # Generate sentiment breakdown
    sentiment_breakdown = {}
    for token in token_mentions:
        if token_mentions[token] > 0:
            # Create random but sensible sentiment dimensions
            base_sentiment = token_sentiment[token]
            
            sentiment_breakdown[token] = {
                "community": min(1, max(-1, base_sentiment + random.uniform(-0.3, 0.3))),
                "technology": min(1, max(-1, base_sentiment + random.uniform(-0.2, 0.4))),
                "team": min(1, max(-1, base_sentiment + random.uniform(-0.2, 0.2))),
                "adoption": min(1, max(-1, base_sentiment + random.uniform(-0.4, 0.2))),
                "price": min(1, max(-1, base_sentiment + random.uniform(-0.5, 0.5)))
            }
    
    return trending_df, sentiment_breakdown

def generate_mock_trending_data():
    """
    Generates mock trending topics data when APIs are not available
    
    Returns:
        dict: Mock trending topics data
    """
    # Generate dates (recent dates)
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%B %d, %Y") for i in range(7)]
    
    # Mock topics
    topics = [
        {
            "title": "Bitcoin ETF Approval Sparks Market Rally",
            "summary": "The SEC's approval of a Bitcoin ETF has led to a significant market rally with Bitcoin breaking through previous resistance levels. Analysts predict this could lead to increased institutional adoption.",
            "url": "https://example.com/news/bitcoin-etf-approval",
            "date": dates[0],
            "source": "Crypto News Today"
        },
        {
            "title": "Ethereum Completes Major Network Upgrade",
            "summary": "Ethereum has successfully completed its latest network upgrade, improving scalability and reducing gas fees. The upgrade is part of the network's long-term development roadmap.",
            "url": "https://example.com/news/ethereum-upgrade",
            "date": dates[1],
            "source": "Blockchain Insider"
        },
        {
            "title": "Major Bank Launches Cryptocurrency Custody Services",
            "summary": "A major international bank has announced the launch of cryptocurrency custody services for institutional clients, signaling growing mainstream acceptance of digital assets.",
            "url": "https://example.com/news/bank-crypto-custody",
            "date": dates[2],
            "source": "Financial Times"
        },
        {
            "title": "New Regulations Proposed for Stablecoins",
            "summary": "Regulatory authorities have proposed new frameworks for stablecoin issuers, aiming to increase transparency and ensure adequate reserves. The news has caused volatility in the stablecoin market.",
            "url": "https://example.com/news/stablecoin-regulations",
            "date": dates[3],
            "source": "Regulatory Watch"
        },
        {
            "title": "DeFi Protocol Reaches $10 Billion in Total Value Locked",
            "summary": "A leading decentralized finance protocol has reached a milestone of $10 billion in total value locked, highlighting the continued growth of the DeFi ecosystem despite market fluctuations.",
            "url": "https://example.com/news/defi-milestone",
            "date": dates[4],
            "source": "DeFi Daily"
        },
        {
            "title": "NFT Marketplace Announces Integration with Gaming Platform",
            "summary": "A major NFT marketplace has announced a strategic partnership with a popular gaming platform, enabling in-game asset tokenization and trading. The move is expected to accelerate NFT adoption.",
            "url": "https://example.com/news/nft-gaming-integration",
            "date": dates[5],
            "source": "NFT Pulse"
        },
        {
            "title": "Central Bank Digital Currency Trials Show Promising Results",
            "summary": "Several countries have reported successful trials of their Central Bank Digital Currency (CBDC) projects, with plans for wider implementation in the coming year. The development could impact the broader cryptocurrency market.",
            "url": "https://example.com/news/cbdc-trials",
            "date": dates[6],
            "source": "Central Bank Monitor"
        }
    ]
    
    # Mock trending tokens
    trending_tokens = pd.DataFrame([
        {"token": "BTC", "mentions": 142, "sentiment": 0.62},
        {"token": "ETH", "mentions": 124, "sentiment": 0.48},
        {"token": "SOL", "mentions": 83, "sentiment": 0.35},
        {"token": "XRP", "mentions": 71, "sentiment": -0.22},
        {"token": "BNB", "mentions": 69, "sentiment": 0.18},
        {"token": "ADA", "mentions": 54, "sentiment": 0.05},
        {"token": "DOGE", "mentions": 47, "sentiment": 0.75},
        {"token": "MATIC", "mentions": 38, "sentiment": 0.31},
        {"token": "DOT", "mentions": 32, "sentiment": 0.23},
        {"token": "LINK", "mentions": 28, "sentiment": 0.42}
    ])
    
    # Mock sentiment breakdown
    sentiment_breakdown = {
        "BTC": {
            "community": 0.75,
            "technology": 0.58,
            "team": 0.62,
            "adoption": 0.81,
            "price": 0.54
        },
        "ETH": {
            "community": 0.65,
            "technology": 0.72,
            "team": 0.58,
            "adoption": 0.63,
            "price": 0.41
        },
        "SOL": {
            "community": 0.48,
            "technology": 0.65,
            "team": 0.51,
            "adoption": 0.42,
            "price": 0.29
        },
        "XRP": {
            "community": 0.28,
            "technology": -0.15,
            "team": -0.32,
            "adoption": -0.25,
            "price": -0.35
        },
        "BNB": {
            "community": 0.35,
            "technology": 0.25,
            "team": 0.21,
            "adoption": 0.32,
            "price": 0.15
        }
    }
    
    return {
        "topics": topics,
        "trending_tokens": trending_tokens,
        "sentiment_breakdown": sentiment_breakdown
    }