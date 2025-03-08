import os
import sqlite3
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # sqlite or postgres
DB_PATH = os.getenv("DB_PATH", "crypto_data.db")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "crypto_analysis")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_db_connection():
    """
    Establishes a database connection based on configuration
    
    Returns:
        Connection: Database connection object
    """
    if DB_TYPE.lower() == "sqlite":
        # SQLite connection
        return sqlite3.connect(DB_PATH)
    else:
        # PostgreSQL connection
        try:
            import psycopg2
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
        except ImportError:
            print("Error: psycopg2 module not found. Using SQLite instead.")
            return sqlite3.connect(DB_PATH)

def init_database():
    """
    Initializes the database with required tables
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create market data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS market_data (
        date TEXT,
        market_cap REAL,
        volume REAL,
        btc_dominance REAL,
        PRIMARY KEY (date)
    )
    ''')
    
    # Create token data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS token_data (
        token TEXT,
        date TEXT,
        price REAL,
        market_cap REAL,
        volume REAL,
        PRIMARY KEY (token, date)
    )
    ''')
    
    # Create analysis results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        token TEXT,
        date TEXT,
        analysis_type TEXT,
        result TEXT,
        PRIMARY KEY (token, date, analysis_type)
    )
    ''')
    
    # Create trending topics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trending_topics (
        date TEXT,
        topics TEXT,
        PRIMARY KEY (date)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_data(market_data, token_data):
    """
    Saves market and token data to the database
    
    Args:
        market_data (pd.DataFrame): Market data
        token_data (dict): Dictionary of token data
    """
    try:
        # Initialize database if needed
        init_database()
        
        conn = get_db_connection()
        
        # Save market data
        df_market = pd.DataFrame(market_data)
        
        # Convert datetime to string
        df_market['date'] = df_market['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert into database
        df_market.to_sql('market_data', conn, if_exists='append', index=False)
        
        # Save token data
        for token, data in token_data.items():
            df_token = pd.DataFrame(data)
            df_token['token'] = token
            
            #
            # Select only needed columns
            df_token = df_token[['token', 'date', 'price', 'market_cap', 'volume']]
            
            # Insert into database
            df_token.to_sql('token_data', conn, if_exists='append', index=False)
        
        # Commit changes
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"Error saving data to database: {e}")

def get_historical_data(start_date=None, end_date=None):
    """
    Retrieves historical data from the database
    
    Args:
        start_date (str, optional): Start date for filtering
        end_date (str, optional): End date for filtering
    
    Returns:
        tuple: (market_data, token_data)
    """
    try:
        conn = get_db_connection()
        
        # Construct date filter
        date_filter = ""
        params = []
        
        if start_date:
            date_filter += " WHERE date >= ?"
            params.append(start_date)
        
        if end_date:
            if start_date:
                date_filter += " AND date <= ?"
            else:
                date_filter += " WHERE date <= ?"
            params.append(end_date)
        
        # Query market data
        market_query = f"SELECT * FROM market_data{date_filter} ORDER BY date"
        df_market = pd.read_sql_query(market_query, conn, params=params)
        
        # Convert date strings to datetime
        df_market['date'] = pd.to_datetime(df_market['date'])
        
        # Query unique tokens
        token_query = "SELECT DISTINCT token FROM token_data"
        tokens = pd.read_sql_query(token_query, conn)['token'].tolist()
        
        # Query token data for each token
        token_data = {}
        for token in tokens:
            token_params = [token] + params
            token_filter = date_filter.replace("WHERE", "WHERE token = ? AND") if date_filter else " WHERE token = ?"
            query = f"SELECT * FROM token_data{token_filter} ORDER BY date"
            df_token = pd.read_sql_query(query, conn, params=token_params)
            
            # Convert date strings to datetime
            df_token['date'] = pd.to_datetime(df_token['date'])
            
            token_data[token] = df_token
        
        conn.close()
        
        return df_market.to_dict('list'), token_data
    
    except Exception as e:
        print(f"Error retrieving historical data: {e}")
        return None, None

def save_analysis_result(token, analysis_type, result):
    """
    Saves analysis results to the database
    
    Args:
        token (str): Token symbol
        analysis_type (str): Type of analysis (e.g., 'prediction', 'whitepaper')
        result (dict): Analysis result
    """
    try:
        # Initialize database if needed
        init_database()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Current date
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert result to JSON
        result_json = json.dumps(result)
        
        # Insert or replace analysis result
        cursor.execute(
            "INSERT OR REPLACE INTO analysis_results (token, date, analysis_type, result) VALUES (?, ?, ?, ?)",
            (token, current_date, analysis_type, result_json)
        )
        
        # Commit changes
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"Error saving analysis result: {e}")

def get_analysis_result(token, analysis_type, limit=1):
    """
    Retrieves analysis results from the database
    
    Args:
        token (str): Token symbol
        analysis_type (str): Type of analysis
        limit (int, optional): Maximum number of results to retrieve
    
    Returns:
        list: List of analysis results
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query analysis results
        cursor.execute(
            "SELECT date, result FROM analysis_results WHERE token = ? AND analysis_type = ? ORDER BY date DESC LIMIT ?",
            (token, analysis_type, limit)
        )
        
        results = []
        for date, result_json in cursor.fetchall():
            result = json.loads(result_json)
            results.append({
                'date': date,
                'result': result
            })
        
        conn.close()
        
        return results
    
    except Exception as e:
        print(f"Error retrieving analysis result: {e}")
        return []

def save_trending_topics(topics_data):
    """
    Saves trending topics to the database
    
    Args:
        topics_data (dict): Trending topics data
    """
    try:
        # Initialize database if needed
        init_database()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Current date
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert topics to JSON
        topics_json = json.dumps(topics_data)
        
        # Insert or replace trending topics
        cursor.execute(
            "INSERT OR REPLACE INTO trending_topics (date, topics) VALUES (?, ?)",
            (current_date, topics_json)
        )
        
        # Commit changes
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"Error saving trending topics: {e}")

def get_trending_topics(limit=1):
    """
    Retrieves trending topics from the database
    
    Args:
        limit (int, optional): Maximum number of results to retrieve
    
    Returns:
        list: List of trending topics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query trending topics
        cursor.execute(
            "SELECT date, topics FROM trending_topics ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        
        results = []
        for date, topics_json in cursor.fetchall():
            topics = json.loads(topics_json)
            results.append({
                'date': date,
                'topics': topics
            })
        
        conn.close()
        
        return results
    
    except Exception as e:
        print(f"Error retrieving trending topics: {e}")
        return [] Convert datetime to string
            df_token['date'] = df_token['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            #