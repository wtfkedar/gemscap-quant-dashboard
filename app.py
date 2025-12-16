import streamlit as st
import threading
import asyncio
import pandas as pd

from storage import init_db, get_all_ticks, get_tick_count, cleanup_old_data, clear_all_data
from ingestion import start_stream, stop_stream
from analytics import (
    prepare_df,
    spread_and_hedge,
    zscore,
    resample_ohlc,
    rolling_correlation,
    adf_test
)

# ================= PAGE CONFIG =================
st.set_page_config(
    layout="wide", 
    page_title="Gemscap Quant Dashboard",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ================= SESSION STATE =================
if "streaming" not in st.session_state:
    st.session_state.streaming = False
    st.session_state.thread = None

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Controls")

# ---- THEME TOGGLE ----
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark Mode")

# ================= GLOBAL CSS =================
if st.session_state.dark_mode:
    # Dark Mode Theme
    st.markdown("""
    <style>
    /* Main container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #1a1a1a;
    }
    
    /* Main background */
    .stApp {
        background-color: #0d0d0d;
    }
    
    /* Text colors */
    .stMarkdown, p, span, label {
        color: #e0e0e0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    
    /* Download button */
    div.stDownloadButton > button {
        background-color: #16a34a;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    
    div.stDownloadButton > button:hover {
        background-color: #15803d;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border-bottom: 2px solid #333;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #a0a0a0;
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stSelectbox > div > div {
        background-color: #2a2a2a;
        color: #ffffff;
    }
    
    /* Info/Success boxes */
    .stAlert {
        background-color: #2a2a2a;
        border: 1px solid #404040;
    }
    
    /* Divider */
    hr {
        border-color: #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light Mode Theme
    st.markdown("""
    <style>
    /* Main container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #f8fafc;
    }
    
    /* Main background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Text colors */
    .stMarkdown, p, span, label {
        color: #1e293b !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transform: translateY(-1px);
    }
    
    /* Download button */
    div.stDownloadButton > button {
        background-color: #16a34a;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    div.stDownloadButton > button:hover {
        background-color: #15803d;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.8rem !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8fafc;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
        background-color: transparent;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
        font-weight: 600;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
    }
    
    /* Info/Success boxes */
    .stAlert {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Divider */
    hr {
        border-color: #e2e8f0 !important;
        margin: 1.5rem 0;
    }
    
    /* Cards effect for metrics */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("## 📊 Gemscap – Quant Analytics Dashboard")
init_db()

# ================= SIDEBAR CONTROLS =================
st.sidebar.markdown("### 📡 Data Ingestion")

timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1m", "5m"], index=1)

symbols_input = st.sidebar.text_input(
    "Symbols (comma-separated)",
    "btcusdt,ethusdt"
)

symbols = [s.strip().lower() for s in symbols_input.split(",") if s.strip()]

c1, c2 = st.sidebar.columns(2)
with c1:
    start_btn = st.button("▶ Start", use_container_width=True, key="start_btn")
    if start_btn and not st.session_state.streaming:
        def run_async_stream():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_stream(symbols))
        
        st.session_state.thread = threading.Thread(target=run_async_stream, daemon=True)
        st.session_state.thread.start()
        st.session_state.streaming = True
        st.rerun()

with c2:
    stop_btn = st.button("⏹ Stop", use_container_width=True, key="stop_btn")
    if stop_btn and st.session_state.streaming:
        stop_stream()
        st.session_state.streaming = False
        st.rerun()

st.sidebar.markdown("### 📊 Analytics Settings")

window = st.sidebar.slider("Z-score Window", 10, 200, 50)

z_threshold = st.sidebar.number_input(
    "Z-score Alert Threshold",
    value=2.0,
    step=0.1,
    min_value=0.5,
    max_value=5.0
)

st.sidebar.markdown("### 📊 Status")

# Show streaming status
if st.session_state.streaming:
    st.sidebar.success("🟢 Stream is LIVE")
else:
    st.sidebar.info("🔴 Stream is STOPPED")

tick_count = get_tick_count()
st.sidebar.metric("Total Ticks Stored", f"{tick_count:,}")

st.sidebar.markdown("### 🗄️ Data Management")

if st.sidebar.button("🧹 Cleanup Old Data", use_container_width=True):
    cleanup_old_data(keep_last_n=50000)
    st.sidebar.success("Data cleaned up!")
    st.rerun()

if st.sidebar.button("🗑️ Clear All Data", use_container_width=True):
    clear_all_data()
    st.sidebar.success("All data cleared!")
    st.rerun()

# ================= AUTO-REFRESH =================
if st.session_state.streaming:
    import time
    time.sleep(2)
    st.rerun()

# ================= LOAD DATA =================
rows = get_all_ticks()
if not rows:
    st.info("⏳ Waiting for live data... Click 'Start Stream' to begin ingestion.")
    st.stop()

try:
    df = prepare_df(rows)
except Exception as e:
    st.error(f"Error preparing data: {e}")
    st.stop()

# ================= KPI ROW =================
k1, k2, k3 = st.columns(3)
k1.metric("Total Ticks", f"{len(df):,}")
k2.metric("Symbols", df["symbol"].nunique())
k3.metric("Timeframe", timeframe)

st.divider()

# ================= CORE COMPUTATION =================
resampled = []
for sym in symbols:
    sym_df = df[df["symbol"] == sym][["timestamp", "price", "qty"]]
    bars = resample_ohlc(sym_df, timeframe)
    bars["symbol"] = sym
    resampled.append(bars)

price_bars = pd.concat(resampled)

price_chart_df = (
    price_bars
    .pivot_table(
        index="timestamp",
        columns="symbol",
        values="close",
        aggfunc="last"
    )
    .sort_index()
)

spread = zs = hedge = rolling_corr = None

if len(symbols) >= 2:
    s1, s2 = symbols[:2]

    df1 = df[df["symbol"] == s1].sort_values("timestamp")
    df2 = df[df["symbol"] == s2].sort_values("timestamp")

    n = min(len(df1), len(df2))
    df1, df2 = df1.iloc[-n:], df2.iloc[-n:]

    spread, hedge = spread_and_hedge(df1, df2)
    zs = zscore(spread, window)

    corr_df = price_chart_df[[s1, s2]].dropna()
    if len(corr_df) >= window:
        rolling_corr = rolling_correlation(
            corr_df[s1], corr_df[s2], window
        )

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Prices", "📊 Analytics", "🧪 Tests", "📥 Export"]
)

# ---------- TAB 1 ----------
with tab1:
    st.line_chart(price_chart_df.tail(400), height=380)

# ---------- TAB 2 (ANALYTICS – CORRELATION INCLUDED) ----------
with tab2:
    if spread is None:
        st.info("📊 Select at least two symbols to view analytics")
    else:
        # Metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("Hedge Ratio (β)", f"{hedge:.4f}")
        if not zs.dropna().empty:
            latest_z = zs.dropna().iloc[-1]
            m2.metric("Current Z-score", f"{latest_z:.3f}")
            m3.metric("Z-score Status", 
                     "⚠️ Alert" if abs(latest_z) >= z_threshold else "✅ Normal")
        
        st.divider()
        
        # Charts
        cA, cB = st.columns(2)
        with cA:
            st.subheader("📈 Spread")
            st.line_chart(spread.tail(400), height=280)
            st.caption(f"Spread = {symbols[0]} - {hedge:.4f} × {symbols[1]}")

        with cB:
            st.subheader("📊 Z-score")
            st.line_chart(zs.tail(400), height=280)
            st.caption(f"Window: {window} | Threshold: ±{z_threshold}")

        st.subheader("🔗 Rolling Correlation")
        if rolling_corr is not None:
            st.line_chart(rolling_corr.tail(400), height=280)
            if not rolling_corr.dropna().empty:
                latest_corr = rolling_corr.dropna().iloc[-1]
                st.caption(f"Current correlation: {latest_corr:.4f} | Window: {window}")
        else:
            st.info("Collecting more data for correlation analysis...")

# ---------- TAB 3 ----------
with tab3:
    if spread is not None:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Run ADF Test", use_container_width=True):
                try:
                    p = adf_test(spread)
                    if p is not None:
                        st.metric("ADF p-value", f"{p:.6f}")
                        if p < 0.05:
                            st.success("✅ Series is stationary (p < 0.05)")
                        else:
                            st.warning("⚠️ Series is non-stationary (p ≥ 0.05)")
                    else:
                        st.error("Insufficient data for ADF test (need at least 20 points)")
                except Exception as e:
                    st.error(f"Error running ADF test: {e}")
        
        with col_b:
            st.markdown("**ADF Test Interpretation:**")
            st.markdown("- p < 0.05: Reject null hypothesis → Stationary")
            st.markdown("- p ≥ 0.05: Fail to reject → Non-stationary")
    else:
        st.info("Select at least two symbols to run statistical tests")

    if zs is not None and not zs.dropna().empty:
        latest_z = zs.dropna().iloc[-1]
        z_val = round(latest_z, 3)

        if abs(z_val) >= z_threshold:
            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    border-radius:8px;
                    background-color:#fee2e2;
                    color:#991b1b;
                    font-size:20px;
                    font-weight:600;
                ">
                🚨 Z-score: {z_val} (OUT OF RANGE)
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    border-radius:8px;
                    background-color:#dcfce7;
                    color:#166534;
                    font-size:20px;
                    font-weight:600;
                ">
                ✅ Z-score: {z_val} (NORMAL)
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------- TAB 4 ----------
with tab4:
    price_csv = price_bars.assign(
        timestamp=price_bars["timestamp"].astype(str)
    ).to_csv(index=False)

    st.download_button(
        "Download Price Bars CSV",
        price_csv,
        file_name=f"price_bars_{timeframe}.csv",
        mime="text/csv"
    )
