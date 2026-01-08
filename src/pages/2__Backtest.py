import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.backtest_engine import BacktestEngine, BacktestConfig

st.set_page_config(page_title="SigmaBot Backtesting", page_icon="🔬", layout="wide")

st.title("🔬 SigmaBot - Strategibacktesting")

# Sidebar for configuration
st.sidebar.header("⚙️ Konfigurasjon")

# Symbol selection
symbol = st.sidebar.text_input("Symbol", value="BTC-USD")

# Period selection
period = st.sidebar.selectbox(
    "Periode",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2
)

# Interval selection
interval = st.sidebar.selectbox(
    "Intervall",
    options=["1h", "4h", "1d", "1wk"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.header("📊 Strategiparametere")

# EMA parameters
use_ema = st.sidebar.checkbox("Bruk EMA-strategi", value=True)
ema_window = st.sidebar.slider("EMA-vindu", 5, 200, 20) if use_ema else 20

# RSI parameters
use_rsi = st.sidebar.checkbox("Bruk RSI-strategi", value=True)
if use_rsi:
    rsi_window = st.sidebar.slider("RSI-vindu", 5, 30, 14)
    rsi_oversold = st.sidebar.slider("RSI Oversolgt", 10, 40, 30)
    rsi_overbought = st.sidebar.slider("RSI Overkjøpt", 60, 90, 70)
else:
    rsi_window, rsi_oversold, rsi_overbought = 14, 30, 70

st.sidebar.markdown("---")

# Run backtest button
if st.sidebar.button("🚀 Kjør Backtest", type="primary"):
    with st.spinner(f"Kjører backtest for {symbol}..."):
        try:
            # Create configuration
            config = BacktestConfig(
                symbol=symbol,
                period=period,
                interval=interval,
                use_ema=use_ema,
                ema_window=ema_window,
                use_rsi=use_rsi,
                rsi_window=rsi_window,
                rsi_oversold=rsi_oversold,
                rsi_overbought=rsi_overbought
            )
            
            # Run backtest
            engine = BacktestEngine()
            result = engine.run_backtest(config)
            
            # Store in session state
            st.session_state.result = result
            st.success(f"✅ Backtest fullført for {symbol}!")
            
        except ValueError as e:
            st.error(f"Konfigurasjonsfeil: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"Feil ved kjøring av backtest: {str(e)}")
            st.stop()

# Display results if available
if hasattr(st.session_state, 'result'):
    result = st.session_state.result
    data = result.data
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Strategiavkastning", f"{result.total_return:.2f}%")
    with col2:
        st.metric("Kjøp og hold avkastning", f"{result.buy_hold_return:.2f}%")
    with col3:
        st.metric("Maksimal drawdown", f"{result.max_drawdown:.2f}%")
    with col4:
        st.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Ytelse", "📈 Indikatorer", "📋 Data"])
    
    with tab1:
        st.subheader("Sammenligning av kumulativ avkastning")
        
        # Create plotly figure for cumulative returns
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["cum_strategy"],
            name="Strategi",
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["cum_return"],
            name="Kjøp & hold",
            line=dict(color='blue', width=2, dash='dash')
        ))
        
        fig.update_layout(
            xaxis_title="Dato",
            yaxis_title="Kumulativ avkastning",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Drawdown chart
        st.subheader("Strategi drawdown")
        cummax = data["cum_strategy"].cummax()
        drawdown = (data["cum_strategy"] - cummax) / cummax * 100
        
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=data.index,
            y=drawdown,
            fill='tozeroy',
            name="Drawdown",
            line=dict(color='red')
        ))
        
        fig_dd.update_layout(
            xaxis_title="Dato",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            height=300
        )
        
        st.plotly_chart(fig_dd, use_container_width=True)
    
    with tab2:
        st.subheader("Pris og indikatorer")
        
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Pris & Signaler', 'EMA', 'RSI'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price and signals
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            name="Sluttkurs",
            line=dict(color='black')
        ), row=1, col=1)
        
        # Buy signals
        buy_signals = data[data["signal"] == 1]
        fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals["Close"],
            mode='markers',
            name="Kjøpssignal",
            marker=dict(color='green', size=10, symbol='triangle-up')
        ), row=1, col=1)
        
        # Sell signals
        sell_signals = data[data["signal"] == -1]
        fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals["Close"],
            mode='markers',
            name="Salgssignal",
            marker=dict(color='red', size=10, symbol='triangle-down')
        ), row=1, col=1)
        
        # EMA if available
        if use_ema and f"EMA{ema_window}" in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[f"EMA{ema_window}"],
                name=f"EMA{ema_window}",
                line=dict(color='orange', dash='dash')
            ), row=2, col=1)
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["Close"],
                name="Sluttkurs",
                line=dict(color='black')
            ), row=2, col=1)
        
        # RSI if available
        if use_rsi and "RSI" in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["RSI"],
                name="RSI",
                line=dict(color='purple')
            ), row=3, col=1)
            
            # Add overbought/oversold lines
            fig.add_hline(y=rsi_overbought, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=rsi_oversold, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(height=900, showlegend=True, hovermode='x unified')
        fig.update_xaxes(title_text="Dato", row=3, col=1)
        fig.update_yaxes(title_text="Pris", row=1, col=1)
        fig.update_yaxes(title_text="Pris", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Rådata")
        
        # Show last 100 rows
        st.dataframe(
            data[["Close", "signal", "return", "strategy_return", "cum_strategy"]].tail(100),
            use_container_width=True
        )
        
        # Download button
        csv = data.to_csv()
        st.download_button(
            label="📥 Last ned fullstendig datasett",
            data=csv,
            file_name=f"{result.symbol}_backtest.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Konfigurer backtestparametrene dine i sidebaren og klikk 'Kjør Backtest' for å begynne")
    
    # Show some example info
    st.markdown("""
    ### Velkommen til SigmaBot! 
    
    Denne applikasjonen lar deg backteste handelsstrategier på kryptovaluta og aksjedata.
    
    **Funksjoner:**
    - 📊 Interaktive visualiseringer
    - 📈 Flere strategikombinasjoner (EMA, RSI)
    - 📉 Ytelsesmetrikker og drawdown-analyse
    - 💾 Eksporter resultater til CSV
    
    **Slik bruker du:**
    1. Velg et symbol (f.eks. BTC-USD, AAPL)
    2. Velg tidsperiode og intervall
    3. Konfigurer strategiparametere
    4. Klikk "Kjør Backtest" for å se resultater
    
    **For å avslutte og returnere til terminalen:** Trykk `Ctrl+C` i terminalvinduet
    """)
