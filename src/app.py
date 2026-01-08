import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.utils.yahoo_finance import download_yf
from src.strategies import CombinedStrategy, EMAStrategy, RSIStrategy
from src.event_manager import EventManager

st.set_page_config(page_title="SigmaBot Trading", page_icon="📈", layout="wide")

st.title("📈 SigmaBot - Trading Strategy Backtester")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# Symbol selection
symbol = st.sidebar.text_input("Symbol", value="BTC-USD")

# Period selection
period = st.sidebar.selectbox(
    "Period",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2
)

# Interval selection
interval = st.sidebar.selectbox(
    "Interval",
    options=["1h", "4h", "1d", "1wk"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.header("📊 Strategy Parameters")

# EMA parameters
use_ema = st.sidebar.checkbox("Use EMA Strategy", value=True)
ema_window = st.sidebar.slider("EMA Window", 5, 200, 20) if use_ema else 20

# RSI parameters
use_rsi = st.sidebar.checkbox("Use RSI Strategy", value=True)
if use_rsi:
    rsi_window = st.sidebar.slider("RSI Window", 5, 30, 14)
    rsi_oversold = st.sidebar.slider("RSI Oversold", 10, 40, 30)
    rsi_overbought = st.sidebar.slider("RSI Overbought", 60, 90, 70)
else:
    rsi_window, rsi_oversold, rsi_overbought = 14, 30, 70

st.sidebar.markdown("---")

# Run backtest button
if st.sidebar.button("🚀 Run Backtest", type="primary"):
    with st.spinner(f"Downloading {symbol} data..."):
        try:
            # Download data
            data = download_yf(symbol, period=period, interval=interval)
            
            if data.empty:
                st.error("No data available for this symbol")
                st.stop()
            
            # Initialize event manager
            event_manager = EventManager()
            
            # Initialize strategies
            strategies = []
            if use_ema:
                strategies.append(EMAStrategy(ema_window=ema_window, event_manager=event_manager))
            if use_rsi:
                strategies.append(RSIStrategy(
                    rsi_window=rsi_window,
                    overbought=rsi_overbought,
                    oversold=rsi_oversold,
                    event_manager=event_manager
                ))
            
            if not strategies:
                st.error("Please select at least one strategy")
                st.stop()
            
            # Apply combined strategy
            combined_strategy = CombinedStrategy(strategies=strategies)
            data = combined_strategy.generate_signals(data)
            
            # Calculate returns
            data["return"] = data["Close"].pct_change()
            data["strategy_return"] = data["signal"].shift(1) * data["return"]
            
            # Cumulative returns
            data["cum_return"] = (1 + data["return"]).cumprod()
            data["cum_strategy"] = (1 + data["strategy_return"]).cumprod()
            
            # Calculate metrics
            total_return = (data["cum_strategy"].iloc[-1] - 1) * 100
            buy_hold_return = (data["cum_return"].iloc[-1] - 1) * 100
            
            # Calculate max drawdown
            cummax = data["cum_strategy"].cummax()
            drawdown = (data["cum_strategy"] - cummax) / cummax
            max_drawdown = drawdown.min() * 100
            
            # Calculate Sharpe ratio (annualized)
            sharpe_ratio = data["strategy_return"].mean() / data["strategy_return"].std() * (252 ** 0.5) if interval == "1d" else data["strategy_return"].mean() / data["strategy_return"].std()
            
            # Store in session state
            st.session_state.data = data
            st.session_state.total_return = total_return
            st.session_state.buy_hold_return = buy_hold_return
            st.session_state.max_drawdown = max_drawdown
            st.session_state.sharpe_ratio = sharpe_ratio
            st.session_state.symbol = symbol
            
        except Exception as e:
            st.error(f"Error running backtest: {str(e)}")
            st.stop()

# Display results if available
if hasattr(st.session_state, 'data'):
    data = st.session_state.data
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Strategy Return", f"{st.session_state.total_return:.2f}%")
    with col2:
        st.metric("Buy & Hold Return", f"{st.session_state.buy_hold_return:.2f}%")
    with col3:
        st.metric("Max Drawdown", f"{st.session_state.max_drawdown:.2f}%")
    with col4:
        st.metric("Sharpe Ratio", f"{st.session_state.sharpe_ratio:.2f}")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Performance", "📈 Indicators", "📋 Data"])
    
    with tab1:
        st.subheader("Cumulative Returns Comparison")
        
        # Create plotly figure for cumulative returns
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["cum_strategy"],
            name="Strategy",
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["cum_return"],
            name="Buy & Hold",
            line=dict(color='blue', width=2, dash='dash')
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Drawdown chart
        st.subheader("Strategy Drawdown")
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
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            height=300
        )
        
        st.plotly_chart(fig_dd, use_container_width=True)
    
    with tab2:
        st.subheader("Price and Indicators")
        
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & Signals', 'EMA', 'RSI'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price and signals
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            name="Close Price",
            line=dict(color='black')
        ), row=1, col=1)
        
        # Buy signals
        buy_signals = data[data["signal"] == 1]
        fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals["Close"],
            mode='markers',
            name="Buy Signal",
            marker=dict(color='green', size=10, symbol='triangle-up')
        ), row=1, col=1)
        
        # Sell signals
        sell_signals = data[data["signal"] == -1]
        fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals["Close"],
            mode='markers',
            name="Sell Signal",
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
                name="Close",
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
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Price", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Raw Data")
        
        # Show last 100 rows
        st.dataframe(
            data[["Close", "signal", "return", "strategy_return", "cum_strategy"]].tail(100),
            use_container_width=True
        )
        
        # Download button
        csv = data.to_csv()
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name=f"{st.session_state.symbol}_backtest.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Configure your backtest parameters in the sidebar and click 'Run Backtest' to begin")
    
    # Show some example info
    st.markdown("""
    ### Welcome to SigmaBot! 
    
    This application allows you to backtest trading strategies on cryptocurrency and stock data.
    
    **Features:**
    - 📊 Interactive visualizations
    - 📈 Multiple strategy combinations (EMA, RSI)
    - 📉 Performance metrics and drawdown analysis
    - 💾 Export results to CSV
    
    **How to use:**
    1. Select a symbol (e.g., BTC-USD, AAPL)
    2. Choose time period and interval
    3. Configure strategy parameters
    4. Click "Run Backtest" to see results
    
    **To exit and return to terminal:** Press `Ctrl+C` in the terminal window
    """)
