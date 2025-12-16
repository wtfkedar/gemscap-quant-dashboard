# 📊 Gemscap – Quant Analytics Dashboard

## Overview

This is a **real-time quantitative analytics dashboard** developed as part of the **Gemscap Quant Developer Evaluation Assignment**.

The application demonstrates an **end-to-end analytical workflow**, covering:
- Live market data ingestion via WebSocket
- Persistent storage and resampling
- Quantitative analytics
- Interactive visualization
- Alerts and data export

The system is designed as a **modular prototype** that reflects how a scalable real-time analytics stack could evolve in a production trading or research environment.

---

## Project Architecture

The system follows a **layered architecture** with clear separation of concerns, enabling maintainability and extensibility.

### Architecture Diagram
   
![Architecture Diagram](architecture.svg)

### Data Flow

The application implements a **unidirectional data flow** from ingestion to visualization:

1. **External Data Source**
   - Live market data streamed from Binance Futures WebSocket API
   - Real-time tick data for multiple symbols

2. **Data Ingestion Layer** (`ingestion.py`)
   - Asynchronous WebSocket connections using `asyncio` and `websockets`
   - Captures: timestamp, symbol, price, quantity
   - Non-blocking concurrent processing for multiple streams
   - Auto-reconnect with exponential backoff

3. **Storage Layer** (`storage.py`)
   - Persistent storage using SQLite
   - Efficient tick-level data storage
   - Thread-safe operations
   - Optimized for time-series queries

4. **Analytics Engine** (`analytics.py`)
   - On-demand resampling: 1s, 1m, 5m OHLC bars
   - Statistical computations:
     - OLS hedge ratio estimation
     - Spread calculation
     - Rolling Z-score
     - Rolling correlation
     - ADF (Augmented Dickey-Fuller) stationarity test
   - Powered by `pandas`, `numpy`, and `statsmodels`

5. **Frontend UI** (`app.py`)
   - Interactive Streamlit dashboard
   - Real-time chart updates
   - Configurable parameters (symbols, timeframes, thresholds)
   - Organized tabs: Prices, Analytics, Statistical Tests, Export
   - Z-score breach alerts

### Architectural Principles

- **Modularity**: Each layer has a single, well-defined responsibility
- **Loose Coupling**: Components communicate through clean interfaces
- **Extensibility**: New data sources or analytics can be added without refactoring
- **Separation of Concerns**: Business logic, data access, and presentation are isolated

---

## Key Features

### 🔹 Real-Time Data Ingestion
- Live tick data streamed from **Binance Futures WebSocket**
- Captured fields:
  - `timestamp`
  - `symbol`
  - `price`
  - `quantity`
- Supports multiple symbols simultaneously
- Automatic reconnection on connection failures

### 🔹 Storage & Resampling
- Raw tick data stored in **SQLite**
- On-the-fly resampling into:
  - **1 second**
  - **1 minute**
  - **5 minute** bars
- Data cleanup utilities to manage storage

### 🔹 Quantitative Analytics
- Multi-symbol price visualization
- **OLS hedge ratio estimation**
- **Spread calculation**
- **Rolling Z-score**
- **Rolling correlation**
- **ADF (Augmented Dickey-Fuller) test**
- Visual alert when Z-score threshold is breached

### 🔹 Interactive Frontend
- Built using **Streamlit**
- User controls:
  - Symbol selection
  - Timeframe selection
  - Rolling window size
  - Z-score alert threshold
- Organized into tabs:
  - Prices
  - Analytics
  - Statistical Tests
  - Data Export
- Light / Dark mode toggle

### 🔹 Alerts
- Real-time **Z-score threshold alert**
- Clearly highlighted to assist quick decision-making

### 🔹 Data Export
- Download resampled OHLC data as **CSV**
- Enables offline analysis and reproducibility

---

## Technology Stack

### Backend & Analytics
- Python 3
- asyncio
- websockets
- pandas
- numpy
- statsmodels
- SQLite

### Frontend
- Streamlit

---

## Folder Structure

```
gemscap-quant-dashboard/
│
├── app.py                      # Streamlit frontend
├── ingestion.py                # WebSocket ingestion
├── analytics.py                # Quantitative analytics
├── storage.py                  # SQLite storage
├── config.py                   # Configuration
├── utils.py                    # Utility functions
├── test_app.py                 # Test suite
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── README.md                   # Documentation
└── architecture.svg            # Architecture diagram
```

---

## Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/wtfkedar/gemscap-quant-dashboard.git
cd gemscap-quant-dashboard
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the application
```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## Usage Guide

### Starting Data Collection

1. In the sidebar, enter symbols (e.g., `btcusdt,ethusdt`)
2. Click **"▶ Start"** to begin live data ingestion
3. Wait a few seconds for data to populate

### Viewing Analytics

- **Prices Tab**: See real-time price movements for all symbols
- **Analytics Tab**: View spread, Z-score, and rolling correlation
- **Tests Tab**: Run ADF test and view Z-score alerts
- **Export Tab**: Download CSV data

### Configuration

- **Symbols**: Enter comma-separated symbols (lowercase)
- **Timeframe**: Choose 1s, 1m, or 5m bars
- **Z-score Window**: Adjust rolling window size (10-200)
- **Alert Threshold**: Set Z-score threshold (typically 2.0)

### Data Management

- **Cleanup Old Data**: Keeps most recent 50,000 ticks
- **Clear All Data**: Removes all stored data

---

## Design Philosophy

- **Clarity over complexity** – readable and maintainable code
- **Modularity** – clean separation of concerns
- **Extensibility** – easy to add new analytics or data sources
- **Prototype mindset** – designed to scale conceptually without premature optimization

---


## Conclusion

This project demonstrates the ability to:
- ✅ Work with real-time financial data
- ✅ Apply statistical and quantitative techniques
- ✅ Design modular analytical systems
- ✅ Build intuitive, interactive dashboards
- ✅ Communicate design decisions clearly

The implementation focuses on business usefulness and analytical reasoning, aligning with the expectations of a quantitative trading and research environment.

---

## ChatGPT Usage Transparency

ChatGPT was used as a development assistant for:
- Structuring the system architecture
- Debugging Streamlit UI behavior
- Improving code clarity and modularity
- Writing documentation

All design decisions, implementation logic, and final code integration were reviewed and implemented manually.
