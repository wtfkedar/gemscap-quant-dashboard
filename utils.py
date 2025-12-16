"""
Utility functions for the Gemscap Quant Dashboard
"""

import pandas as pd
from datetime import datetime, timedelta


def format_number(num, decimals=2):
    """Format number with thousands separator"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def calculate_statistics(series):
    """Calculate basic statistics for a series"""
    if series.empty:
        return {}
    
    return {
        "mean": series.mean(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max(),
        "current": series.iloc[-1] if len(series) > 0 else None
    }


def validate_symbols(symbols):
    """Validate symbol format"""
    valid_symbols = []
    for symbol in symbols:
        symbol = symbol.strip().lower()
        if symbol and len(symbol) >= 6:
            valid_symbols.append(symbol)
    return valid_symbols


def get_data_quality_metrics(df):
    """Calculate data quality metrics"""
    if df.empty:
        return {
            "total_records": 0,
            "unique_symbols": 0,
            "time_range": "N/A",
            "data_gaps": 0
        }
    
    time_range = "N/A"
    if "timestamp" in df.columns and not df["timestamp"].empty:
        try:
            min_time = df["timestamp"].min()
            max_time = df["timestamp"].max()
            duration = max_time - min_time
            time_range = str(duration).split(".")[0]  # Remove microseconds
        except:
            pass
    
    return {
        "total_records": len(df),
        "unique_symbols": df["symbol"].nunique() if "symbol" in df.columns else 0,
        "time_range": time_range,
        "data_gaps": 0  # Could implement gap detection
    }


def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def truncate_dataframe(df, max_rows=100000):
    """Truncate dataframe to maximum rows"""
    if len(df) > max_rows:
        return df.tail(max_rows)
    return df


def check_system_health():
    """Check system health status"""
    import os
    import psutil
    
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # Check database file
        db_exists = os.path.exists('market_data.db')
        db_size = os.path.getsize('market_data.db') if db_exists else 0
        
        return {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "db_exists": db_exists,
            "db_size_mb": db_size / (1024 * 1024)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def format_timestamp(ts):
    """Format timestamp for display"""
    try:
        if isinstance(ts, str):
            ts = pd.to_datetime(ts)
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)


def calculate_returns(prices):
    """Calculate returns from price series"""
    if len(prices) < 2:
        return pd.Series()
    return prices.pct_change().dropna()


def calculate_volatility(returns, window=20):
    """Calculate rolling volatility"""
    if len(returns) < window:
        return pd.Series()
    return returns.rolling(window).std() * (252 ** 0.5)  # Annualized


def detect_outliers(series, threshold=3):
    """Detect outliers using z-score method"""
    if len(series) < 10:
        return pd.Series(dtype=bool)
    
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    return abs(z_scores) > threshold
