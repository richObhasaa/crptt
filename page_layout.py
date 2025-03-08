import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from config import CHART_COLORS, UI_CONFIG

def create_header():
    """
    Creates a consistent header with logo and title
    """
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # Use emoji as logo
        st.markdown("<h1 style='font-size: 3rem; margin-bottom: 0;'>📊</h1>", unsafe_allow_html=True)
    
    with col2:
        st.title("Crypto Market Cap Analysis & Prediction")
        st.markdown(
            """
            <p style='margin-top: -0.8rem; font-size: 1.1rem; color: #777777;'>
            Analyze, visualize, and predict cryptocurrency market trends
            </p>
            """, 
            unsafe_allow_html=True
        )

def create_sidebar_filters():
    """
    Creates standard sidebar filters for the app
    
    Returns:
        dict: Selected filter values
    """
    from config import TIMEFRAMES, TOP_TOKENS
    
    filters = {}
    
    st.sidebar.title("Analysis Settings")
    
    # Date range selector
    st.sidebar.subheader("Time Period")
    filters["timeframe"] = st.sidebar.selectbox("Select Time Period", TIMEFRAMES)
    
    # Token selection
    st.sidebar.subheader("Cryptocurrency Selection")
    
    try:
        from api_service import get_token_list
        all_tokens = get_token_list()
    except:
        all_tokens = TOP_TOKENS
    
    filters["selected_tokens"] = st.sidebar.multiselect(
        "Select Cryptocurrencies to Compare",
        options=all_tokens,
        default=TOP_TOKENS[:5]
    )
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        filters["show_indicators"] = st.checkbox("Show Technical Indicators", value=False)
        filters["log_scale"] = st.checkbox("Logarithmic Scale", value=False)
        filters["dark_mode"] = st.checkbox("Dark Mode", value=False)
    
    # API status
    st.sidebar.markdown("---")
    st.sidebar.subheader("API Status")
    
    # Check API keys from environment
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_status = {
        "CoinGecko": "✅ Connected" if os.getenv("COINGECKO_API_KEY") else "⚠️ Limited",
        "OpenAI": "✅ Connected" if os.getenv("OPENAI_API_KEY") else "❌ Disconnected",
        "News API": "✅ Connected" if os.getenv("NEWS_API_KEY") else "❌ Disconnected"
    }
    
    for api, status in api_status.items():
        st.sidebar.markdown(f"**{api}**: {status}")
    
    return filters

def create_metric_cards(metrics, num_columns=4):
    """
    Creates metric cards in a row
    
    Args:
        metrics (list): List of metric dictionaries with 'label', 'value', and optional 'delta'
        num_columns (int): Number of columns to display
    """
    columns = st.columns(num_columns)
    
    for i, metric in enumerate(metrics):
        with columns[i % num_columns]:
            if 'delta' in metric and metric['delta'] is not None:
                st.metric(
                    label=metric['label'],
                    value=metric['value'],
                    delta=metric['delta']
                )
            else:
                st.metric(
                    label=metric['label'],
                    value=metric['value']
                )

def create_chart(chart_type, data, **kwargs):
    """
    Creates a chart with consistent styling
    
    Args:
        chart_type (str): Type of chart ('line', 'bar', 'pie', 'scatter')
        data (pd.DataFrame): Data for the chart
        **kwargs: Additional arguments for the chart
    
    Returns:
        fig: Plotly figure object
    """
    # Set default title
    title = kwargs.get('title', '')
    
    # Set default height
    height = kwargs.get('height', 500)
    
    # Set default colors
    if 'color_discrete_map' not in kwargs:
        # Generate color map for tokens
        if 'color' in kwargs and kwargs['color'] in data.columns:
            unique_values = data[kwargs['color']].unique()
            color_map = {}
            
            for i, value in enumerate(unique_values):
                if value in CHART_COLORS:
                    color_map[value] = CHART_COLORS[value]
                else:
                    # Use default color or cycle through colors
                    color_map[value] = CHART_COLORS.get('default', '#4A90E2')
            
            kwargs['color_discrete_map'] = color_map
    
    # Create appropriate chart type
    if chart_type == 'line':
        fig = px.line(data, **kwargs)
    elif chart_type == 'bar':
        fig = px.bar(data, **kwargs)
    elif chart_type == 'pie':
        fig = px.pie(data, **kwargs)
    elif chart_type == 'scatter':
        fig = px.scatter(data, **kwargs)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    # Apply consistent styling
    fig.update_layout(
        title_text=title,
        height=height,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_section_header(title, description=None):
    """
    Creates a consistent section header with optional description
    
    Args:
        title (str): Section title
        description (str, optional): Section description
    """
    st.markdown(f"## {title}")
    
    if description:
        st.markdown(f"<p style='color: #777777; margin-top: -0.5rem;'>{description}</p>", unsafe_allow_html=True)
    
    st.markdown("---")

def create_footer():
    """
    Creates a consistent footer with credits and update time
    """
    current_year = datetime.now().year
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"© {current_year} Crypto Market Analysis | Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.markdown(
            """
            <div style='text-align: right;'>
            Data sources: CoinGecko, CoinMarketCap, Binance
            </div>
            """, 
            unsafe_allow_html=True
        )

def apply_theme(dark_mode=False):
    """
    Applies the selected theme to the app
    
    Args:
        dark_mode (bool): Whether to use dark mode
    """
    if dark_mode:
        st.markdown(
            """
            <style>
            .main {
                background-color: #121212;
                color: #f0f0f0;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #1e1e1e;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
                color: #f0f0f0;
            }
            .stTabs [aria-selected="true"] {
                background-color: #2c5ade;
                color: white;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #f0f0f0;
            }
            .stSidebar {
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(UI_CONFIG['css'], unsafe_allow_html=True)