# Timeframe options for analysis
TIMEFRAMES = [
    "24h",
    "7d",
    "30d",
    "90d",
    "1y",
    "All Time"
]

# Top tokens for default selection
TOP_TOKENS = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "ADA",
    "SOL",
    "DOT",
    "DOGE",
    "AVAX",
    "LINK"
]

# API configuration
API_CONFIG = {
    # CoinGecko API settings
    "coingecko": {
        "base_url": "https://api.coingecko.com/api/v3",
        "endpoints": {
            "market_data": "/global",
            "historical_market_data": "/global/history",
            "coin_list": "/coins/list",
            "coin_data": "/coins/{id}",
            "historical_coin_data": "/coins/{id}/market_chart/range"
        },
        "request_limit": 50,  # Requests per minute (free tier)
        "retry_delay": 60,     # Seconds to wait after hitting limit
    },
    
    # CoinMarketCap API settings
    "coinmarketcap": {
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "endpoints": {
            "listings": "/cryptocurrency/listings/latest",
            "quotes": "/cryptocurrency/quotes/latest",
            "metadata": "/cryptocurrency/info"
        },
        "request_limit": 30,   # Requests per minute (basic tier)
        "retry_delay": 60,     # Seconds to wait after hitting limit
    },
    
    # Binance API settings
    "binance": {
        "base_url": "https://api.binance.com/api/v3",
        "endpoints": {
            "ticker": "/ticker/24hr",
            "klines": "/klines"
        },
        "request_limit": 1200, # Requests per minute
        "retry_delay": 60,     # Seconds to wait after hitting limit
    },
    
    # News API settings
    "newsapi": {
        "base_url": "https://newsapi.org/v2",
        "endpoints": {
            "everything": "/everything",
            "top_headlines": "/top-headlines"
        },
        "request_limit": 100,  # Requests per day (developer tier)
        "retry_delay": 86400,  # Seconds to wait after hitting limit (1 day)
    },
    
    # Crypto Panic API settings
    "cryptopanic": {
        "base_url": "https://cryptopanic.com/api/v1",
        "endpoints": {
            "posts": "/posts/"
        },
        "request_limit": 60,   # Requests per hour (free tier)
        "retry_delay": 3600,   # Seconds to wait after hitting limit (1 hour)
    }
}

# Machine learning model configuration
ML_CONFIG = {
    "ARIMA": {
        "order": (5, 1, 0),
        "seasonal_order": (1, 1, 0, 7),
        "trend": "c"
    },
    "LSTM": {
        "units": 50,
        "dropout": 0.2,
        "epochs": 50,
        "batch_size": 32,
        "window_size": 14
    },
    "Prophet": {
        "changepoint_prior_scale": 0.05,
        "seasonality_mode": "multiplicative",
        "yearly_seasonality": True,
        "weekly_seasonality": True,
        "daily_seasonality": False
    }
}

# AI analysis configuration
AI_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.2,
    "max_tokens": 1000,
    "analysis_types": ["security", "growth", "risk", "technology", "summary"],
    "whitepaper_max_length": 15000  # Characters
}

# Chart colors for consistency across the app
CHART_COLORS = {
    "BTC": "#F7931A",
    "ETH": "#627EEA",
    "BNB": "#F3BA2F",
    "XRP": "#23292F",
    "ADA": "#0033AD",
    "SOL": "#00FFA3",
    "DOT": "#E6007A",
    "DOGE": "#C3A634",
    "AVAX": "#E84142",
    "LINK": "#2A5ADA",
    "default": "#4A90E2",
    "total_market": "#7E57C2",
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#9E9E9E"
}

# App UI configuration
UI_CONFIG = {
    "theme": "light",
    "css": """
        .main {
            background-color: #f5f5f5;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4f8bf9;
            color: white;
        }
    """
}

# Database configuration
DB_CONFIG = {
    "type": "sqlite",
    "path": "crypto_data.db",
    "tables": {
        "market_data": {
            "columns": ["date", "market_cap", "volume", "btc_dominance"],
            "primary_key": ["date"]
        },
        "token_data": {
            "columns": ["token", "date", "price", "market_cap", "volume"],
            "primary_key": ["token", "date"]
        },
        "analysis_results": {
            "columns": ["token", "date", "analysis_type", "result"],
            "primary_key": ["token", "date", "analysis_type"]
        },
        "trending_topics": {
            "columns": ["date", "topics"],
            "primary_key": ["date"]
        }
    }
}