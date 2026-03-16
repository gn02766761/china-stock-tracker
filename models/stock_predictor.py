import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import warnings
warnings.filterwarnings('ignore')

class StockPredictor:
    """
    A class to predict stock prices using various ML algorithms
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.feature_columns = []
    
    def prepare_features(self, df):
        """
        Prepare features for training/prediction
        """
        # Select feature columns
        feature_cols = ['open', 'high', 'low', 'close', 'vol']
        
        # Add technical indicators if available
        ta_cols = ['MA5', 'MA10', 'MA20', 'MA30', 'EMA12', 'EMA26', 
                   'MACD', 'MACD_signal', 'MACD_histogram', 'RSI', 
                   'BB_upper', 'BB_middle', 'BB_lower', 'volatility', 'ROC']
        
        for col in ta_cols:
            if col in df.columns:
                feature_cols.append(col)
        
        self.feature_columns = feature_cols
        
        # Prepare features
        X = df[feature_cols].fillna(method='ffill').fillna(method='bfill').values
        y = df['close'].values  # Target variable
        
        return X, y
    
    def create_lstm_dataset(self, data, time_step=60):
        """
        Create dataset for LSTM model
        """
        X, y = [], []
        for i in range(len(data) - time_step - 1):
            X.append(data[i:(i + time_step)])
            y.append(data[i + time_step])
        return np.array(X), np.array(y)
    
    def train_lstm_model(self, df, time_step=60, epochs=50, batch_size=32):
        """
        Train an LSTM model for stock price prediction
        """
        # Prepare data
        X, y = self.prepare_features(df)
        
        # Scale the features
        scaled_X = self.scaler.fit_transform(X)
        scaled_y = self.scaler.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Create sequences for LSTM
        X_seq, y_seq = self.create_lstm_dataset(scaled_y, time_step)
        
        # Reshape X for LSTM [samples, time steps, features]
        X_seq = X_seq.reshape(X_seq.shape[0], X_seq.shape[1], 1)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_seq, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Build LSTM model
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(time_step, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            verbose=1,
            shuffle=False
        )
        
        return history
    
    def train_random_forest(self, df, n_estimators=100, max_depth=10):
        """
        Train a Random Forest model for stock price prediction
        """
        # Prepare data
        X, y = self.prepare_features(df)
        
        # Handle NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X_clean = X[mask]
        y_clean = y[mask]
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X_clean)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_clean, test_size=0.2, random_state=42
        )
        
        # Train the model
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        print(f"Random Forest - Training MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
        
        return self.model
    
    def train_linear_regression(self, df):
        """
        Train a Linear Regression model for stock price prediction
        """
        # Prepare data
        X, y = self.prepare_features(df)
        
        # Handle NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X_clean = X[mask]
        y_clean = y[mask]
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X_clean)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_clean, test_size=0.2, random_state=42
        )
        
        # Train the model
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"Linear Regression - Training MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
        print(f"Linear Regression - Training R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        
        return self.model
    
    def predict(self, df, model_type='lstm'):
        """
        Make predictions using the trained model
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call a training method first.")
        
        if model_type.lower() == 'lstm':
            # Prepare data for LSTM
            X, y = self.prepare_features(df)
            scaled_X = self.scaler.transform(X)
            scaled_y = self.scaler.transform(y.reshape(-1, 1)).flatten()
            
            # Use last sequence to predict next value
            time_step = 60
            last_sequence = scaled_y[-time_step:]
            last_sequence = last_sequence.reshape((1, time_step, 1))
            
            predicted_scaled = self.model.predict(last_sequence)
            predicted_price = self.scaler.inverse_transform(predicted_scaled)[0][0]
            
            return predicted_price
        else:
            # Prepare data for traditional models
            X, y = self.prepare_features(df)
            mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X_clean = X[mask]
            
            if len(X_clean) == 0:
                raise ValueError("No valid data points after cleaning")
            
            # Scale the features
            X_scaled = self.scaler.transform(X_clean)
            
            # Predict using the last row of data
            last_row = X_scaled[-1].reshape(1, -1)
            predicted_price = self.model.predict(last_row)[0]
            
            return predicted_price
    
    def evaluate_model(self, df):
        """
        Evaluate the trained model
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call a training method first.")
        
        X, y = self.prepare_features(df)
        
        # Handle NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X_clean = X[mask]
        y_clean = y[mask]
        
        if len(X_clean) == 0:
            raise ValueError("No valid data points after cleaning")
        
        # Scale the features
        X_scaled = self.scaler.transform(X_clean)
        
        # Make predictions
        y_pred = self.model.predict(X_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_clean, y_pred)
        mae = mean_absolute_error(y_clean, y_pred)
        r2 = r2_score(y_clean, y_pred)
        
        print(f"Model Evaluation:")
        print(f"MSE: {mse:.4f}")
        print(f"MAE: {mae:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        return {'MSE': mse, 'MAE': mae, 'R2': r2}


def backtest_strategy(df, model, prediction_days=30):
    """
    Perform a simple backtesting of the prediction model
    """
    results = []
    
    for i in range(prediction_days, len(df)):
        # Train on data up to day i-prediction_days
        train_df = df.iloc[:i-prediction_days].copy()
        
        # Reinitialize and train model
        predictor = StockPredictor()
        predictor.train_linear_regression(train_df)
        
        # Predict the next day
        test_df = df.iloc[i-prediction_days:i+1].copy()
        predicted_price = predictor.predict(test_df, model_type='linear')
        
        actual_price = df.iloc[i]['close']
        
        results.append({
            'date': df.index[i],
            'predicted': predicted_price,
            'actual': actual_price,
            'error': abs(predicted_price - actual_price)
        })
    
    results_df = pd.DataFrame(results)
    avg_error = results_df['error'].mean()
    accuracy = 1 - (avg_error / results_df['actual'].mean())
    
    print(f"Backtest Results (over {prediction_days} days):")
    print(f"Average Error: {avg_error:.4f}")
    print(f"Accuracy: {accuracy:.4f}")
    
    return results_df


if __name__ == "__main__":
    print("Stock Prediction Module - Contains classes and functions for predicting stock prices using ML techniques")