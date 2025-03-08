import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from prophet import Prophet

def predict_prices(historical_data, model_type, prediction_days=30):
    """
    Predicts future cryptocurrency prices using selected model
    
    Args:
        historical_data (pd.DataFrame): Historical price data
        model_type (str): Type of prediction model to use (ARIMA, LSTM, Prophet)
        prediction_days (int): Number of days to predict
    
    Returns:
        dict: Prediction results with dates and predicted prices
    """
    if model_type == "ARIMA":
        return predict_with_arima(historical_data, prediction_days)
    elif model_type == "LSTM":
        return predict_with_lstm(historical_data, prediction_days)
    elif model_type == "Prophet":
        return predict_with_prophet(historical_data, prediction_days)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def predict_with_arima(historical_data, prediction_days=30):
    """
    Predicts future prices using ARIMA model
    
    Args:
        historical_data (pd.DataFrame): Historical price data
        prediction_days (int): Number of days to predict
    
    Returns:
        dict: Prediction results with dates and predicted prices
    """
    # Convert to pandas DataFrame if it's a dict
    if isinstance(historical_data, dict):
        df = pd.DataFrame(historical_data)
    else:
        df = historical_data.copy()
    
    # Ensure data is sorted by date
    df = df.sort_values('date')
    
    # Prepare data for ARIMA
    prices = df['price'].values
    
    # Fit ARIMA model
    # Use auto_arima or try different parameters
    model = ARIMA(prices, order=(5, 1, 0))
    model_fit = model.fit()
    
    # Make prediction
    forecast = model_fit.forecast(steps=prediction_days)
    
    # Create forecast dates
    last_date = df['date'].iloc[-1]
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(prediction_days)]
    
    # Prepare confidence intervals
    forecast_std = np.sqrt(model_fit.forecast_variance(prediction_days))
    lower_bound = forecast - 1.96 * forecast_std
    upper_bound = forecast + 1.96 * forecast_std
    
    # Ensure no negative prices
    lower_bound = np.maximum(lower_bound, 0)
    
    # Calculate model accuracy (MAPE on historical data)
    predictions = model_fit.predict(start=1, end=len(prices))
    mape = np.mean(np.abs((prices[1:] - predictions) / prices[1:])) * 100
    accuracy = 100 - mape
    
    # Prepare result
    result = {
        'date': forecast_dates,
        'predicted_price': forecast,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'accuracy': accuracy
    }
    
    return result

def predict_with_lstm(historical_data, prediction_days=30):
    """
    Predicts future prices using LSTM model
    
    Args:
        historical_data (pd.DataFrame): Historical price data
        prediction_days (int): Number of days to predict
    
    Returns:
        dict: Prediction results with dates and predicted prices
    """
    # Convert to pandas DataFrame if it's a dict
    if isinstance(historical_data, dict):
        df = pd.DataFrame(historical_data)
    else:
        df = historical_data.copy()
    
    # Ensure data is sorted by date
    df = df.sort_values('date')
    
    # Prepare data for LSTM
    prices = df['price'].values
    
    # Normalize the data
    min_price = min(prices)
    max_price = max(prices)
    prices_normalized = (prices - min_price) / (max_price - min_price)
    
    # Create sequences for LSTM
    n_input = 14  # Input sequence length
    n_features = 1  # Number of features (only price)
    
    # Prepare sequences
    generator = TimeseriesGenerator(
        prices_normalized,
        prices_normalized,
        length=n_input,
        batch_size=1
    )
    
    # Build LSTM model
    model = Sequential([
        LSTM(units=50, activation='relu', return_sequences=True, input_shape=(n_input, n_features)),
        Dropout(0.2),
        LSTM(units=50, activation='relu'),
        Dropout(0.2),
        Dense(units=1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    
    # Train model
    model.fit(generator, epochs=50, verbose=0)
    
    # Make prediction
    last_sequence = prices_normalized[-n_input:].reshape((1, n_input, n_features))
    
    # Predict one day at a time and use that prediction for subsequent days
    predicted_normalized = []
    current_sequence = last_sequence[0].tolist()
    
    for _ in range(prediction_days):
        # Reshape for prediction
        current_sequence_array = np.array(current_sequence).reshape((1, n_input, n_features))
        
        # Predict next value
        next_value = model.predict(current_sequence_array, verbose=0)[0][0]
        
        # Add to predictions
        predicted_normalized.append(next_value)
        
        # Update sequence for next prediction
        current_sequence.pop(0)
        current_sequence.append([next_value])
    
    # Denormalize predictions
    predicted_prices = [(p * (max_price - min_price)) + min_price for p in predicted_normalized]
    
    # Create forecast dates
    last_date = df['date'].iloc[-1]
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(prediction_days)]
    
    # Add uncertainty bounds (simple approach)
    uncertainty = 0.1  # 10% uncertainty
    upper_bound = [p * (1 + uncertainty) for p in predicted_prices]
    lower_bound = [p * (1 - uncertainty) for p in predicted_prices]
    
    # Prepare result
    result = {
        'date': forecast_dates,
        'predicted_price': predicted_prices,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound
    }
    
    return result

def predict_with_prophet(historical_data, prediction_days=30):
    """
    Predicts future prices using Prophet model
    
    Args:
        historical_data (pd.DataFrame): Historical price data
        prediction_days (int): Number of days to predict
    
    Returns:
        dict: Prediction results with dates and predicted prices
    """
    # Convert to pandas DataFrame if it's a dict
    if isinstance(historical_data, dict):
        df = pd.DataFrame(historical_data)
    else:
        df = historical_data.copy()
    
    # Ensure data is sorted by date
    df = df.sort_values('date')
    
    # Prepare data for Prophet
    prophet_df = df[['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})
    
    # Create and fit model
    model = Prophet(
        changepoint_prior_scale=0.05,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    
    model.fit(prophet_df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=prediction_days)
    
    # Make prediction
    forecast = model.predict(future)
    
    # Extract relevant prediction period
    forecast = forecast.iloc[-prediction_days:].reset_index(drop=True)
    
    # Prepare result
    result = {
        'date': forecast['ds'].values,
        'predicted_price': forecast['yhat'].values,
        'upper_bound': forecast['yhat_upper'].values,
        'lower_bound': forecast['yhat_lower'].values
    }
    
    return result