"""
Dashboard - Sanntidsovervåking av marked
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from src.utils.yahoo_finance import download_yf, get_symbol_data
from src.signals.strategies import SMAStrategy
from src.main import EVENT_QUEUE
from src.event_manager import EventManager


st.set_page_config(page_title="Dashboard - SigmaBott", page_icon="📊", layout="wide")


def inject_styles():
    st.markdown("""
    <style>
      /* Litt mindre luft, mer dashboard-feel */
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

#inject_styles()


def signal(bull: bool):
    color = "#198754" if bull else "#dc3545"  # grønn eller rød
    st.markdown(
        f"""
        <div style="font-size:32px; font-weight:700; margin:20px 0; line-height:1.1; color:{color};">
            OSEBX
        </div>
        """, 
        unsafe_allow_html=True
    )


# Sidebar configuration
st.sidebar.header("⚙️ Dashboardinnstillinger")

# Initialize shared EventManager in session state
if "event_manager" not in st.session_state:
    st.session_state.event_manager = EventManager()

# Main content
st.markdown("### Markedsoversikt")

osebx = get_symbol_data("OSEBX.OL", "200d", "1d")

# Use the shared EventManager from session state
osebx_sma = SMAStrategy(200, st.session_state.event_manager).generate_signals(osebx["data"])
signal(True)  # Eksempelbruk


# Example of sending an event to the EventManager
def send_event_to_manager(event_type, data):
    st.session_state.event_manager.notify(event_type, data)


# Example usage
send_event_to_manager("dashboard_loaded", {"page": "Dashboard"})




# Symbol watchlist
st.sidebar.subheader("📋 Overvåkningsliste")
default_symbols = ["OSEBX.OL"]
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
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    index=2
)

# Refresh button
if st.sidebar.button("🔄 Oppdater data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Data oppdateres ved hver oppdatering")



# Create columns for metrics
metric_cols = st.columns(len(symbols))


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
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(f'{symbol} Pris', 'Volum', "Pris og SMA 200"),
                row_heights=[0.7, 0.3, 1]
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

            # Calculate 200 SMA
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
            data['trigger'] = data['Close'] > data['SMA_200']

            # Plot Close price
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["Close"],
                name="Sluttkurs",
                line=dict(color='yellow')
            ), row=3, col=1)

            # Plot 200 SMA
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['SMA_200'],
                name="SMA 200",
                line=dict(color='green', dash='dash')
            ), row=3, col=1)

            # Plot trigger line
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['trigger'].astype(int) * data['Close'],
                name="Trigger",
                line=dict(color='red')
            ), row=3, col=1)

            fig.update_layout(
                height=1200,
                showlegend=False,
                xaxis_rangeslider_visible=False,
                hovermode='x unified'
            )

            fig.update_yaxes(title_text="Pris", row=1, col=1)
            fig.update_yaxes(title_text="Volum", row=2, col=1)
            fig.update_yaxes(title_text="Strategi", row=3, col=1)

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
st.caption(
    "**For å avslutte og returnere til terminalen:** Trykk `Ctrl+C` i terminalvinduet"
)
