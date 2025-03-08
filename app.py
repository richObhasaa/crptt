import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Import custom modules
from api_service import get_market_data, get_token_data, get_token_list
from data_processor import calculate_stats, process_historical_data
from ml_predictor import predict_prices
from ai_analyzer import analyze_whitepaper
from news_analyzer import get_trending_topics
from database import save_data, get_historical_data
from config import TIMEFRAMES, TOP_TOKENS

# Set page configuration
st.set_page_config(
    page_title="Crypto Market Cap Analysis & Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS styling
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Crypto Analysis Settings")

# Date range selector
st.sidebar.subheader("Time Period")
timeframe = st.sidebar.selectbox("Select Time Period", TIMEFRAMES)

# Token selection
st.sidebar.subheader("Cryptocurrency Selection")
all_tokens = get_token_list()
selected_tokens = st.sidebar.multiselect(
    "Select Cryptocurrencies to Compare",
    options=all_tokens,
    default=TOP_TOKENS
)

# Main app layout
st.title("Cryptocurrency Market Cap Analysis & Prediction")

# Create tabs for different sections
tabs = st.tabs([
    "📊 Market Overview", 
    "📈 Data Visualization", 
    "🔍 Statistical Analysis",
    "⚖️ Comparison", 
    "📉 Price Prediction", 
    "🧠 Project Analysis",
    "📢 Trending Topics"
])

# Load data
@st.cache_data(ttl=3600)
def load_market_data(period):
    market_data = get_market_data(period)
    return market_data

@st.cache_data(ttl=3600)
def load_token_data(tokens, period):
    token_data = {}
    for token in tokens:
        token_data[token] = get_token_data(token, period)
    return token_data

# Get data
try:
    market_data = load_market_data(timeframe)
    token_data = load_token_data(selected_tokens, timeframe)
    
    # Process data
    processed_market_data = process_historical_data(market_data)
    processed_token_data = {token: process_historical_data(data) for token, data in token_data.items()}
    
    # Save to database for historical record
    save_data(processed_market_data, processed_token_data)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Tab 1: Market Overview
with tabs[0]:
    st.header("Global Cryptocurrency Market Overview")
    
    # Market metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_market_cap = processed_market_data['market_cap'].iloc[-1]
        st.metric("Total Market Cap", f"${current_market_cap:,.0f}")
    
    with col2:
        market_cap_change = (processed_market_data['market_cap'].iloc[-1] / 
                             processed_market_data['market_cap'].iloc[-2] - 1) * 100
        st.metric("24h Change", f"{market_cap_change:.2f}%", 
                  delta=f"{market_cap_change:.2f}%")
    
    with col3:
        total_volume = processed_market_data['volume'].iloc[-1]
        st.metric("24h Volume", f"${total_volume:,.0f}")
    
    with col4:
        active_tokens = len(all_tokens)
        st.metric("Active Cryptocurrencies", active_tokens)
    
    # Market cap over time chart
    st.subheader("Total Market Capitalization Over Time")
    fig = px.line(
        processed_market_data, 
        x='date', 
        y='market_cap',
        title="Total Cryptocurrency Market Cap",
        labels={"market_cap": "Market Cap (USD)", "date": "Date"}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Data Visualization
with tabs[1]:
    st.header("Cryptocurrency Data Visualization")
    
    # Visualization type selection
    viz_type = st.selectbox(
        "Select Visualization Type",
        ["Line Chart", "Bar Chart", "Pie Chart", "Scatter Plot/Heatmap"]
    )
    
    if viz_type == "Line Chart":
        st.subheader("Market Cap Trends")
        
        # Create combined dataframe for plotting
        df_combined = pd.DataFrame({'date': processed_market_data['date'],
                                   'Total Market': processed_market_data['market_cap']})
        
        for token, data in processed_token_data.items():
            df_combined[token] = data['market_cap']
        
        # Multi-line chart
        fig = px.line(
            df_combined, 
            x='date',
            y=df_combined.columns[1:],
            title="Market Cap Comparison",
            labels={"value": "Market Cap (USD)", "date": "Date", "variable": "Cryptocurrency"}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Bar Chart":
        st.subheader("Market Cap Comparison")
        
        # Get latest data for each token
        latest_data = {'Token': [], 'Market Cap': []}
        
        for token, data in processed_token_data.items():
            latest_data['Token'].append(token)
            latest_data['Market Cap'].append(data['market_cap'].iloc[-1])
        
        df_latest = pd.DataFrame(latest_data)
        df_latest = df_latest.sort_values('Market Cap', ascending=False)
        
        # Bar chart
        fig = px.bar(
            df_latest,
            x='Token',
            y='Market Cap',
            title="Current Market Cap by Token",
            color='Market Cap',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Pie Chart":
        st.subheader("Market Share Distribution")
        
        # Calculate market share
        latest_data = {'Token': [], 'Market Cap': []}
        
        for token, data in processed_token_data.items():
            latest_data['Token'].append(token)
            latest_data['Market Cap'].append(data['market_cap'].iloc[-1])
        
        df_latest = pd.DataFrame(latest_data)
        total_selected = df_latest['Market Cap'].sum()
        others = processed_market_data['market_cap'].iloc[-1] - total_selected
        
        if others > 0:
            df_latest = pd.concat([
                df_latest,
                pd.DataFrame({'Token': ['Others'], 'Market Cap': [others]})
            ])
        
        # Pie chart
        fig = px.pie(
            df_latest,
            names='Token',
            values='Market Cap',
            title="Market Share Distribution",
            hole=0.4
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Scatter Plot/Heatmap
        st.subheader("Price vs. Volume Analysis")
        
        # Create dataframe for scatter plot
        scatter_data = {'Token': [], 'Price': [], 'Volume': [], 'Market Cap': []}
        
        for token, data in processed_token_data.items():
            scatter_data['Token'].append(token)
            scatter_data['Price'].append(data['price'].iloc[-1])
            scatter_data['Volume'].append(data['volume'].iloc[-1])
            scatter_data['Market Cap'].append(data['market_cap'].iloc[-1])
        
        df_scatter = pd.DataFrame(scatter_data)
        
        # Scatter plot
        fig = px.scatter(
            df_scatter,
            x='Price',
            y='Volume',
            size='Market Cap',
            color='Token',
            hover_name='Token',
            log_x=True,
            log_y=True,
            title="Price vs. Volume (bubble size = Market Cap)",
            labels={"Price": "Price (USD, log scale)", "Volume": "24h Volume (USD, log scale)"}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Statistical Analysis
with tabs[2]:
    st.header("Statistical Analysis")
    
    token_for_stats = st.selectbox(
        "Select Token for Statistical Analysis",
        ["Total Market"] + selected_tokens
    )
    
    if token_for_stats == "Total Market":
        data_for_stats = processed_market_data
    else:
        data_for_stats = processed_token_data[token_for_stats]
    
    # Calculate statistics
    stats = calculate_stats(data_for_stats)
    
    # Display statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Statistics")
        st.table(stats['price_stats'])
    
    with col2:
        st.subheader("Market Cap Statistics")
        st.table(stats['market_cap_stats'])
    
    # Volatility analysis
    st.subheader("Volatility Analysis")
    
    fig = px.line(
        data_for_stats,
        x='date',
        y='volatility',
        title=f"Price Volatility for {token_for_stats}",
        labels={"volatility": "Volatility (% Change)", "date": "Date"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Comparison
with tabs[3]:
    st.header("Cryptocurrency Comparison")
    
    # Select tokens to compare
    tokens_to_compare = st.multiselect(
        "Select Tokens to Compare",
        options=selected_tokens,
        default=selected_tokens[:min(3, len(selected_tokens))]
    )
    
    if not tokens_to_compare:
        st.warning("Please select at least one token to compare.")
    else:
        # Metrics to compare
        metrics = ["Market Cap", "Price", "Volume", "Volatility"]
        selected_metric = st.radio("Select Metric for Comparison", metrics)
        
        # Map selected metric to dataframe column
        metric_map = {
            "Market Cap": "market_cap",
            "Price": "price",
            "Volume": "volume",
            "Volatility": "volatility"
        }
        
        column = metric_map[selected_metric]
        
        # Create dataframe for comparison
        df_comparison = pd.DataFrame({'date': processed_market_data['date']})
        
        # Include total market if comparing market cap
        if selected_metric == "Market Cap":
            df_comparison['Total Market'] = processed_market_data['market_cap']
        
        # Add selected tokens data
        for token in tokens_to_compare:
            df_comparison[token] = processed_token_data[token][column]
        
        # Plot comparison
        fig = px.line(
            df_comparison,
            x='date',
            y=df_comparison.columns[1:],
            title=f"{selected_metric} Comparison",
            labels={"value": selected_metric, "date": "Date", "variable": "Token"}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display percentage change
        st.subheader("Percentage Change Analysis")
        
        timeframes = ["7 Days", "30 Days", "90 Days", "Year to Date", "1 Year", "All Time"]
        selected_timeframe = st.selectbox("Select Time Period for % Change", timeframes)
        
        # Calculate start index based on selected timeframe
        today = datetime.now()
        if selected_timeframe == "7 Days":
            days_ago = 7
        elif selected_timeframe == "30 Days":
            days_ago = 30
        elif selected_timeframe == "90 Days":
            days_ago = 90
        elif selected_timeframe == "Year to Date":
            days_ago = (today - datetime(today.year, 1, 1)).days
        elif selected_timeframe == "1 Year":
            days_ago = 365
        else:  # All Time
            days_ago = None
        
        # Create table data
        pct_change_data = {'Token': []}
        
        if days_ago is not None:
            start_date = today - timedelta(days=days_ago)
            
            for col in df_comparison.columns[1:]:
                token_data = df_comparison[df_comparison['date'] >= start_date]
                if not token_data.empty:
                    start_value = token_data[col].iloc[0]
                    end_value = token_data[col].iloc[-1]
                    pct_change = ((end_value / start_value) - 1) * 100
                    pct_change_data['Token'].append(col)
                    pct_change_data[f'% Change ({selected_timeframe})'] = [f"{pct:.2f}%" for pct in pct_change_data.get(f'% Change ({selected_timeframe})', []) + [pct_change]]
        else:
            for col in df_comparison.columns[1:]:
                start_value = df_comparison[col].iloc[0]
                end_value = df_comparison[col].iloc[-1]
                pct_change = ((end_value / start_value) - 1) * 100
                pct_change_data['Token'].append(col)
                pct_change_data[f'% Change ({selected_timeframe})'] = [f"{pct:.2f}%" for pct in pct_change_data.get(f'% Change ({selected_timeframe})', []) + [pct_change]]
        
        # Display table
        st.table(pd.DataFrame(pct_change_data))

# Tab 5: Price Prediction
with tabs[4]:
    st.header("Cryptocurrency Price Prediction")
    
    # Select token for prediction
    token_for_prediction = st.selectbox(
        "Select Token for Price Prediction",
        options=selected_tokens
    )
    
    # Select prediction model
    model_type = st.selectbox(
        "Select Prediction Model",
        ["ARIMA", "LSTM", "Prophet"]
    )
    
    # Select prediction period
    prediction_days = st.slider(
        "Prediction Period (Days)",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    
    # Run prediction
    if st.button("Generate Prediction"):
        with st.spinner(f"Generating {prediction_days} day prediction using {model_type}..."):
            try:
                # Get historical data for the selected token
                historical_data = processed_token_data[token_for_prediction]
                
                # Run prediction
                prediction_result = predict_prices(
                    historical_data,
                    model_type,
                    prediction_days
                )
                
                # Display prediction chart
                fig = go.Figure()
                
                # Add historical data
                fig.add_trace(go.Scatter(
                    x=historical_data['date'],
                    y=historical_data['price'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='blue')
                ))
                
                # Add prediction
                fig.add_trace(go.Scatter(
                    x=prediction_result['date'],
                    y=prediction_result['predicted_price'],
                    mode='lines',
                    name='Predicted Price',
                    line=dict(color='red', dash='dash')
                ))
                
                # Add confidence intervals if available
                if 'upper_bound' in prediction_result and 'lower_bound' in prediction_result:
                    fig.add_trace(go.Scatter(
                        x=prediction_result['date'],
                        y=prediction_result['upper_bound'],
                        mode='lines',
                        name='Upper Bound (95% CI)',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=prediction_result['date'],
                        y=prediction_result['lower_bound'],
                        mode='lines',
                        name='Lower Bound (95% CI)',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(255, 0, 0, 0.1)',
                        showlegend=False
                    ))
                
                fig.update_layout(
                    title=f"{token_for_prediction} Price Prediction ({prediction_days} Days)",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    height=600,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show prediction metrics
                st.subheader("Prediction Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    current_price = historical_data['price'].iloc[-1]
                    predicted_price = prediction_result['predicted_price'].iloc[-1]
                    price_change = ((predicted_price / current_price) - 1) * 100
                    
                    st.metric(
                        "Current Price",
                        f"${current_price:.2f}"
                    )
                
                with col2:
                    st.metric(
                        f"Predicted Price ({prediction_days} days)",
                        f"${predicted_price:.2f}",
                        delta=f"{price_change:.2f}%"
                    )
                
                with col3:
                    if 'accuracy' in prediction_result:
                        st.metric(
                            "Model Accuracy",
                            f"{prediction_result['accuracy']:.2f}%"
                        )
                    else:
                        st.metric(
                            "Model",
                            model_type
                        )
                
                # Show detailed prediction table
                st.subheader("Prediction Details")
                
                prediction_table = prediction_result[['date', 'predicted_price']].copy()
                prediction_table.columns = ['Date', 'Predicted Price (USD)']
                
                st.dataframe(prediction_table)
                
            except Exception as e:
                st.error(f"Prediction error: {e}")

# Tab 6: Project Analysis
with tabs[5]:
    st.header("Cryptocurrency Project Analysis")
    
    # Project selection or custom analysis
    analysis_option = st.radio(
        "Analysis Option",
        ["Select from existing projects", "Analyze a whitepaper URL"]
    )
    
    if analysis_option == "Select from existing projects":
        project = st.selectbox(
            "Select Project for Analysis",
            options=selected_tokens
        )
        
        url = st.text_input("Project URL (optional)")
        
    else:
        project = st.text_input("Project Name")
        url = st.text_input("Whitepaper URL (required)")
    
    # Run analysis
    if st.button("Analyze Project"):
        if analysis_option == "Analyze a whitepaper URL" and not url:
            st.warning("Please enter a whitepaper URL for analysis.")
        else:
            with st.spinner("Analyzing project with AI..."):
                try:
                    analysis_result = analyze_whitepaper(project, url)
                    
                    # Display analysis results
                    st.subheader(f"Analysis Results for {project}")
                    
                    # Security Analysis
                    st.write("### Security Analysis")
                    st.write(analysis_result['security'])
                    
                    # Growth Potential
                    st.write("### Growth Potential")
                    st.write(analysis_result['growth'])
                    
                    # Investment Risk
                    st.write("### Investment Risk")
                    st.write(analysis_result['risk'])
                    
                    # Technology Uniqueness
                    st.write("### Technology Uniqueness")
                    st.write(analysis_result['technology'])
                    
                    # Overall Summary
                    st.write("### Overall Summary")
                    st.write(analysis_result['summary'])
                    
                    # Ratings
                    st.subheader("AI Ratings (0-10)")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Security Rating", f"{analysis_result['security_rating']}/10")
                    
                    with col2:
                        st.metric("Growth Rating", f"{analysis_result['growth_rating']}/10")
                    
                    with col3:
                        st.metric("Risk Rating", f"{analysis_result['risk_rating']}/10")
                    
                    with col4:
                        st.metric("Innovation Rating", f"{analysis_result['tech_rating']}/10")
                    
                except Exception as e:
                    st.error(f"Analysis error: {e}")

# Tab 7: Trending Topics
with tabs[6]:
    st.header("Cryptocurrency Trending Topics")
    
    # Refresh button for trending topics
    if st.button("Refresh Trending Topics"):
        with st.spinner("Fetching latest cryptocurrency trends..."):
            try:
                trending_data = get_trending_topics()
                
                # Display trending topics
                st.subheader("Current Trending Topics in Cryptocurrency")
                
                for i, topic in enumerate(trending_data['topics']):
                    st.write(f"### {i+1}. {topic['title']}")
                    st.write(topic['summary'])
                    st.write(f"Source: {topic['source']} | Date: {topic['date']}")
                    st.write("---")
                
                # Display trending tokens
                st.subheader("Trending Cryptocurrencies")
                
                trending_tokens = pd.DataFrame(trending_data['trending_tokens'])
                
                fig = px.bar(
                    trending_tokens,
                    x='token',
                    y='mentions',
                    color='sentiment',
                    color_continuous_scale=px.colors.diverging.RdBu,
                    color_continuous_midpoint=0,
                    title="Top Mentioned Cryptocurrencies by Sentiment",
                    labels={"token": "Cryptocurrency", "mentions": "Mentions", "sentiment": "Sentiment Score"}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Sentiment breakdown
                st.subheader("Sentiment Analysis for Top Cryptos")
                
                # Create radar chart for sentiment dimensions
                categories = ['Community', 'Technology', 'Team', 'Adoption', 'Price']
                
                fig = go.Figure()
                
                for token in trending_tokens['token'].head(5):
                    token_data = trending_data['sentiment_breakdown'].get(token, {})
                    values = [
                        token_data.get('community', 0),
                        token_data.get('technology', 0),
                        token_data.get('team', 0),
                        token_data.get('adoption', 0),
                        token_data.get('price', 0)
                    ]
                    
                    # Close the polygon
                    values.append(values[0])
                    radar_categories = categories + [categories[0]]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=radar_categories,
                        fill='toself',
                        name=token
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[-1, 1]
                        )
                    ),
                    showlegend=True,
                    title="Sentiment Dimensions for Top 5 Trending Cryptocurrencies"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error fetching trending topics: {e}")
    else:
        st.info("Click 'Refresh Trending Topics' to load the latest cryptocurrency trends from news and social media.")

# Footer
st.markdown("---")
st.write("Data refreshed on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.write("Data sources: CoinGecko, CoinMarketCap, Binance, News APIs, and Social Media")