"""
Dashboard - Sanntidsovervåking av marked
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from src.utils.yahoo_finance import download_yf

st.set_page_config(page_title="Dashboard - SigmaBot", page_icon="📊", layout="wide")

st.title("📊 Live Dashboard")

# Sidebar configuration
st.sidebar.header("⚙️ Dashboardinnstillinger")

# Symbol watchlist
st.sidebar.subheader("📋 Overvåkningsliste")
default_symbols = ["BTC-USD", "ETH-USD", "AAPL", "TSLA"]
watchlist = st.sidebar.text_area(
    "Symboler (ett per linje)",
    value="\n".join(default_symbols),
    height=100
)
symbols = [s.strip() for s in watchlist.split("\n") if s.strip()]

# Time settings
interval = st.sidebar.selectbox(
    "Intervall",
    options=["1h", "4h", "1d", "1wk"],
    index=2
)

period = st.sidebar.selectbox(
    "Periode",
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y"],
    index=2
)

# Refresh button
if st.sidebar.button("🔄 Oppdater data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Data oppdateres ved hver oppdatering")

# Main content
st.markdown("### Markedsoversikt")

# Create columns for metrics
metric_cols = st.columns(len(symbols))

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_symbol_data(symbol, period, interval):
    try:
        data = download_yf(symbol, period=period, interval=interval)
        if not data.empty:
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else data.iloc[-1]
            change = ((latest["Close"] - previous["Close"]) / previous["Close"] * 100)
            return {
                "price": latest["Close"],
                "change": change,
                "high": data["High"].max(),
                "low": data["Low"].min(),
                "data": data
            }
    except:
        pass
    return None

# Display metrics for each symbol
for idx, symbol in enumerate(symbols):
    with metric_cols[idx]:
        symbol_data = get_symbol_data(symbol, period, interval)
        if symbol_data:
            st.metric(
                symbol,
                f"${symbol_data['price']:.2f}",
                f"{symbol_data['change']:+.2f}%",
                delta_color="normal"
            )
        else:
            st.metric(symbol, "N/A", "Error")

st.markdown("---")

# Detailed view
st.markdown("### Detaljerte grafer")

# Tabs for each symbol
tabs = st.tabs(symbols)

for idx, symbol in enumerate(symbols):
    with tabs[idx]:
        symbol_data = get_symbol_data(symbol, period, interval)
        
        if symbol_data and symbol_data["data"] is not None:
            data = symbol_data["data"]
            
            # Create price chart
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(f'{symbol} Pris', 'Volum'),
                row_heights=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Pris'
                ),
                row=1, col=1
            )
            
            # Volume chart
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(data['Close'], data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volum',
                    marker_color=colors
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                showlegend=False,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )
            
            fig.update_yaxes(title_text="Pris", row=1, col=1)
            fig.update_yaxes(title_text="Volum", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nåværende pris", f"${symbol_data['price']:.2f}")
            with col2:
                st.metric("Periode høy", f"${symbol_data['high']:.2f}")
            with col3:
                st.metric("Periode lav", f"${symbol_data['low']:.2f}")
            with col4:
                st.metric("Datapunkter", len(data))
        else:
            st.error(f"Kunne ikke laste data for {symbol}")

st.markdown("---")
st.caption(f"Sist oppdatert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("**For å avslutte og returnere til terminalen:** Trykk `Ctrl+C` i terminalvinduet")
