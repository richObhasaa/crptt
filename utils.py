import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import random

def format_currency(value, precision=2):
    """
    Formats a value as currency with appropriate suffixes
    
    Args:
        value (float): Value to format
        precision (int): Decimal precision
    
    Returns:
        str: Formatted currency string
    """
    if value is None:
        return "N/A"
    
    abs_value = abs(value)
    
    if abs_value >= 1e12:
        formatted = f"${abs_value / 1e12:.{precision}f}T"
    elif abs_value >= 1e9:
        formatted = f"${abs_value / 1e9:.{precision}f}B"
    elif abs_value >= 1e6:
        formatted = f"${abs_value / 1e6:.{precision}f}M"
    elif abs_value >= 1e3:
        formatted = f"${abs_value / 1e3:.{precision}f}K"
    else:
        formatted = f"${abs_value:.{precision}f}"
    
    # Add negative sign if needed
    if value < 0:
        formatted = f"-{formatted}"
    
    return formatted

def format_percentage(value, precision=2):
    """
    Formats a value as percentage
    
    Args:
        value (float): Value to format
        precision (int): Decimal precision
    
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value:.{precision}f}%"

def calculate_date_range(timeframe):
    """
    Calculates date range based on timeframe
    
    Args:
        timeframe (str): Time period for data retrieval
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.now()
    
    if timeframe == "24h":
        start_date = end_date - timedelta(days=1)
    elif timeframe == "7d":
        start_date = end_date - timedelta(days=7)
    elif timeframe == "30d":
        start_date = end_date - timedelta(days=30)
    elif timeframe == "90d":
        start_date = end_date - timedelta(days=90)
    elif timeframe == "1y":
        start_date = end_date - timedelta(days=365)
    else:  # All time
        start_date = datetime(2013, 4, 28)  # Bitcoin's first appearance on CoinGecko
    
    return start_date, end_date

def generate_random_data(start_date, end_date, base_value, volatility=0.05):
    """
    Generates random time series data for testing
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        base_value (float): Base value for the series
        volatility (float): Volatility level (0-1)
    
    Returns:
        pd.DataFrame: DataFrame with random time series data
    """
    # Calculate number of days
    days = (end_date - start_date).days + 1
    
    # Generate dates
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate random walk
    values = [base_value]
    for i in range(1, days):
        change = random.uniform(-volatility, volatility)
        values.append(values[-1] * (1 + change))
    
    # Create dataframe
    df = pd.DataFrame({
        'date': dates,
        'value': values
    })
    
    return df

def extract_time_period(text):
    """
    Extracts time period from text description
    
    Args:
        text (str): Text containing time period
    
    Returns:
        str: Standardized time period
    """
    text = text.lower()
    
    if "24h" in text or "24 hour" in text or "day" in text:
        return "24h"
    elif "7d" in text or "7 day" in text or "week" in text:
        return "7d"
    elif "30d" in text or "30 day" in text or "month" in text:
        return "30d"
    elif "90d" in text or "90 day" in text or "3 month" in text or "quarter" in text:
        return "90d"
    elif "1y" in text or "year" in text or "12 month" in text or "365 day" in text:
        return "1y"
    else:
        return "All Time"

def get_comparable_tokens(token, top_tokens, count=3):
    """
    Returns a list of tokens comparable to the given token
    
    Args:
        token (str): Token to find comparables for
        top_tokens (list): List of available tokens
        count (int): Number of comparable tokens to return
    
    Returns:
        list: List of comparable token symbols
    """
    # Common token groups
    token_groups = {
        "layer1": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
        "defi": ["UNI", "AAVE", "COMP", "MKR", "SNX", "SUSHI"],
        "exchange": ["BNB", "CRO", "FTT", "KCS", "OKB", "HT"],
        "meme": ["DOGE", "SHIB", "ELON", "FLOKI", "SAMO"],
        "gaming": ["AXS", "MANA", "SAND", "ENJ", "ILV", "GALA"],
        "oracle": ["LINK", "BAND", "API3", "TRB"],
        "privacy": ["XMR", "ZEC", "DASH", "SCRT"],
        "storage": ["FIL", "STORJ", "AR", "SC"]
    }
    
    # Find group for the token
    token_group = None
    for group, tokens in token_groups.items():
        if token in tokens:
            token_group = group
            break
    
    # If token is in a group, return other tokens from the same group
    if token_group:
        comparable_tokens = [t for t in token_groups[token_group] if t != token and t in top_tokens]
        
        # If not enough tokens in the group, add from other groups
        if len(comparable_tokens) < count:
            additional_tokens = [t for t in top_tokens if t != token and t not in comparable_tokens]
            comparable_tokens.extend(additional_tokens[:count - len(comparable_tokens)])
        
        return comparable_tokens[:count]
    
    # If token is not in a group, return top tokens excluding the given token
    return [t for t in top_tokens if t != token][:count]

def sanitize_input(text):
    """
    Sanitizes user input to prevent injection attacks
    
    Args:
        text (str): User input text
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[\\\'";`$<>&|]', '', text)
    
    return sanitized