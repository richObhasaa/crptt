import pandas as pd
import numpy as np
from scipy import stats

def process_historical_data(data_dict):
    """
    Processes raw historical data for analysis
    
    Args:
        data_dict (dict): Dictionary with date, price, market_cap, volume keys
    
    Returns:
        pd.DataFrame: Processed dataframe with additional metrics
    """
    # Convert to DataFrame
    df = pd.DataFrame(data_dict)
    
    # Ensure data is sorted by date
    df = df.sort_values('date')
    
    # Calculate additional metrics
    
    # Calculate daily returns and volatility
    if 'price' in df.columns:
        df['daily_return'] = df['price'].pct_change() * 100
        # Calculate rolling volatility (10-day window)
        df['volatility'] = df['daily_return'].rolling(window=10).std()
    
    # Calculate market cap change
    if 'market_cap' in df.columns:
        df['market_cap_change'] = df['market_cap'].pct_change() * 100
    
    # Calculate volume to market cap ratio (indicator of trading activity)
    if 'volume' in df.columns and 'market_cap' in df.columns:
        df['volume_to_mcap'] = df['volume'] / df['market_cap']
    
    # Calculate 7-day and 30-day moving averages
    for col in ['price', 'market_cap', 'volume']:
        if col in df.columns:
            df[f'{col}_7d_ma'] = df[col].rolling(window=7).mean()
            df[f'{col}_30d_ma'] = df[col].rolling(window=30).mean()
    
    # Fill NA values
    df = df.fillna(method='bfill')
    
    return df

def calculate_stats(df):
    """
    Calculates statistical metrics for the data
    
    Args:
        df (pd.DataFrame): Processed dataframe
    
    Returns:
        dict: Dictionary with statistical measures
    """
    stats_dict = {}
    
    # Price statistics (if available)
    if 'price' in df.columns:
        price_stats = pd.DataFrame({
            'Metric': [
                'Mean', 'Median', 'Min', 'Max', 'Std Dev', 
                'Skewness', 'Kurtosis', '7-Day Change (%)', '30-Day Change (%)'
            ],
            'Value': [
                f"${df['price'].mean():.4f}",
                f"${df['price'].median():.4f}",
                f"${df['price'].min():.4f}",
                f"${df['price'].max():.4f}",
                f"${df['price'].std():.4f}",
                f"{stats.skew(df['price'].dropna()):.4f}",
                f"{stats.kurtosis(df['price'].dropna()):.4f}",
                f"{((df['price'].iloc[-1] / df['price'].iloc[-min(7, len(df))]) - 1) * 100:.2f}%",
                f"{((df['price'].iloc[-1] / df['price'].iloc[-min(30, len(df))]) - 1) * 100:.2f}%"
            ]
        })
        stats_dict['price_stats'] = price_stats.set_index('Metric')
    
    # Market cap statistics (if available)
    if 'market_cap' in df.columns:
        market_cap_stats = pd.DataFrame({
            'Metric': [
                'Mean', 'Median', 'Min', 'Max', 'Std Dev', 
                '7-Day Change (%)', '30-Day Change (%)'
            ],
            'Value': [
                f"${df['market_cap'].mean():.2e}",
                f"${df['market_cap'].median():.2e}",
                f"${df['market_cap'].min():.2e}",
                f"${df['market_cap'].max():.2e}",
                f"${df['market_cap'].std():.2e}",
                f"{((df['market_cap'].iloc[-1] / df['market_cap'].iloc[-min(7, len(df))]) - 1) * 100:.2f}%",
                f"{((df['market_cap'].iloc[-1] / df['market_cap'].iloc[-min(30, len(df))]) - 1) * 100:.2f}%"
            ]
        })
        stats_dict['market_cap_stats'] = market_cap_stats.set_index('Metric')
    
    # Volume statistics (if available)
    if 'volume' in df.columns:
        volume_stats = pd.DataFrame({
            'Metric': [
                'Mean', 'Median', 'Min', 'Max', 'Std Dev', 
                '7-Day Change (%)', '30-Day Change (%)'
            ],
            'Value': [
                f"${df['volume'].mean():.2e}",
                f"${df['volume'].median():.2e}",
                f"${df['volume'].min():.2e}",
                f"${df['volume'].max():.2e}",
                f"${df['volume'].std():.2e}",
                f"{((df['volume'].iloc[-1] / df['volume'].iloc[-min(7, len(df))]) - 1) * 100:.2f}%",
                f"{((df['volume'].iloc[-1] / df['volume'].iloc[-min(30, len(df))]) - 1) * 100:.2f}%"
            ]
        })
        stats_dict['volume_stats'] = volume_stats.set_index('Metric')
    
    # Volatility statistics (if available)
    if 'volatility' in df.columns:
        volatility_stats = pd.DataFrame({
            'Metric': [
                'Mean', 'Median', 'Min', 'Max', 'Current'
            ],
            'Value': [
                f"{df['volatility'].mean():.2f}%",
                f"{df['volatility'].median():.2f}%",
                f"{df['volatility'].min():.2f}%",
                f"{df['volatility'].max():.2f}%",
                f"{df['volatility'].iloc[-1]:.2f}%"
            ]
        })
        stats_dict['volatility_stats'] = volatility_stats.set_index('Metric')
    
    return stats_dict

def calculate_correlation_matrix(token_data_dict):
    """
    Calculates correlation matrix between different tokens
    
    Args:
        token_data_dict (dict): Dictionary with token data
    
    Returns:
        pd.DataFrame: Correlation matrix
    """
    # Extract price data for each token
    price_data = {}
    
    for token, data in token_data_dict.items():
        df = pd.DataFrame(data)
        price_data[token] = df.set_index('date')['price']
    
    # Create a combined dataframe
    price_df = pd.DataFrame(price_data)
    
    # Calculate correlation matrix
    corr_matrix = price_df.corr()
    
    return corr_matrix

def detect_outliers(df, column, threshold=3):
    """
    Detects outliers in the data using Z-score method
    
    Args:
        df (pd.DataFrame): Dataframe with the data
        column (str): Column to check for outliers
        threshold (float): Z-score threshold for outlier detection
    
    Returns:
        pd.DataFrame: Dataframe with outliers
    """
    if column not in df.columns:
        return pd.DataFrame()
    
    # Calculate Z-scores
    z_scores = np.abs(stats.zscore(df[column].dropna()))
    
    # Find outliers
    outliers_idx = np.where(z_scores > threshold)[0]
    
    # Return dataframe with outliers
    if len(outliers_idx) > 0:
        return df.iloc[outliers_idx].copy()
    else:
        return pd.DataFrame()

def calculate_risk_metrics(df):
    """
    Calculates risk metrics for the data
    
    Args:
        df (pd.DataFrame): Processed dataframe with price data
    
    Returns:
        dict: Dictionary with risk metrics
    """
    if 'price' not in df.columns or 'daily_return' not in df.columns:
        return {}
    
    # Calculate risk metrics
    risk_metrics = {}
    
    # Sharpe ratio (using 2% as risk-free rate)
    risk_free_rate = 0.02 / 365  # Daily risk-free rate
    mean_return = df['daily_return'].mean()
    std_return = df['daily_return'].std()
    
    if std_return > 0:
        sharpe_ratio = (mean_return - risk_free_rate) / std_return
        risk_metrics['sharpe_ratio'] = sharpe_ratio * np.sqrt(365)  # Annualized
    else:
        risk_metrics['sharpe_ratio'] = 0
    
    # Maximum drawdown
    cumulative_returns = (1 + df['daily_return'] / 100).cumprod()
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns / running_max - 1) * 100
    max_drawdown = drawdown.min()
    risk_metrics['max_drawdown'] = max_drawdown
    
    # Value at Risk (VaR) - 95% confidence
    var_95 = np.percentile(df['daily_return'], 5)
    risk_metrics['var_95'] = var_95
    
    # Conditional VaR (CVaR) - 95% confidence
    cvar_95 = df['daily_return'][df['daily_return'] <= var_95].mean()
    risk_metrics['cvar_95'] = cvar_95
    
    return risk_metrics