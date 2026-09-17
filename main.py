import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib

def generate_synthetic_data():
    """Generates synthetic daily sales data for demonstration."""
    date_range = pd.date_range(start="2023-01-01", end="2025-12-31", freq="D")
    np.random.seed(42)
    
    # Base trend, seasonality, and noise
    trend = np.linspace(100, 500, len(date_range))
    seasonality = 50 * np.sin(2 * np.pi * date_range.dayofyear / 365)
    noise = np.random.normal(0, 25, len(date_range))
    
    sales = trend + seasonality + noise
    sales = np.maximum(sales, 0)  # Ensure non-negative sales values
    
    df = pd.DataFrame({"Date": date_range, "Sales": sales})
    return df

def create_features(df):
    """Engineers time-based lag and rolling statistical features."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Calendar Features
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["IsWeekend"] = df["DayOfWeek"].isin([5, 6]).astype(int)
    
    # Lag Features
    df["Sales_Lag_1"] = df["Sales"].shift(1)
    df["Sales_Lag_7"] = df["Sales"].shift(7)
    df["Sales_Lag_30"] = df["Sales"].shift(30)
    
    # Rolling Window Features
    df["Rolling_Mean_7"] = df["Sales"].shift(1).rolling(window=7).mean()
    df["Rolling_Mean_30"] = df["Sales"].shift(1).rolling(window=30).mean()
    
    df = df.dropna().reset_index(drop=True)
    return df

def train_and_evaluate():
    # Load and preprocess data
    df_raw = generate_synthetic_data()
    df = create_features(df_raw)
    
    features = [
        "Year", "Month", "Day", "DayOfWeek", "IsWeekend",
        "Sales_Lag_1", "Sales_Lag_7", "Sales_Lag_30",
        "Rolling_Mean_7", "Rolling_Mean_30"
    ]
    target = "Sales"
    
    # Time-based Train-Test Split (80% Train, 20% Test)
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train, y_train = train_df[features], train_df[target]
    X_test, y_test = test_df[features], test_df[target]
    
    # Model Training
    model = XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("--- Model Evaluation Metrics ---")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE:  {mae:.2f}")
    print(f"R² Score: {r2:.4f}")
    
    # Save Model Artifact
    joblib.dump(model, "sales_forecasting_model.pkl")
    print("\nModel saved successfully as 'sales_forecasting_model.pkl'")
    
    # Visualization Output
    plt.figure(figsize=(12, 6))
    plt.plot(test_df["Date"], y_test.values, label="Actual Sales", color="blue", alpha=0.7)
    plt.plot(test_df["Date"], predictions, label="Forecasted Sales", color="red", linestyle="--", alpha=0.8)
    plt.title("Sales & Demand Forecast vs Actuals")
    plt.xlabel("Date")
    plt.ylabel("Sales Units")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("forecast_results.png")
    print("Forecast plot saved to 'forecast_results.png'")

if __name__ == "__main__":
    train_and_evaluate()
