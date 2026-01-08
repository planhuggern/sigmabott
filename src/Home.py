"""
SigmaBot - Trading Strategy Platform
Main landing page
"""
import streamlit as st

st.set_page_config(
    page_title="SigmaBot",
    page_icon="📈",
    layout="wide"
)

# Header
st.title("📈 SigmaBot")
st.subheader("Advanced Trading Strategy Platform")

st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Welcome to SigmaBot!
    
    SigmaBot is a comprehensive trading strategy platform that helps you analyze, 
    backtest, and monitor trading strategies for cryptocurrencies and stocks.
    
    ### 🚀 Features
    
    - **📊 Live Dashboard** - Monitor real-time market data and strategy performance
    - **🔬 Strategy Backtester** - Test your trading strategies on historical data
    - **📈 Technical Indicators** - EMA, RSI, and more
    - **📉 Performance Analytics** - Detailed metrics, drawdown analysis, Sharpe ratio
    - **💾 Data Export** - Export results for further analysis
    
    ### 🎯 Get Started
    
    Choose a section from the sidebar to begin:
    """)
    
    # Navigation cards
    st.markdown("### 📱 Navigate to:")
    
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        st.info("""
        **📊 Dashboard**
        
        View live market data and monitor your strategies in real-time.
        Track multiple symbols and get instant insights.
        """)
    
    with nav_col2:
        st.info("""
        **🔬 Backtest**
        
        Test your trading strategies on historical data.
        Analyze performance, optimize parameters, and validate ideas.
        """)

with col2:
    st.markdown("### 📊 Quick Stats")
    
    # Placeholder stats - in a real app these would be dynamic
    st.metric("Supported Symbols", "1000+")
    st.metric("Strategies Available", "2+")
    st.metric("Data Sources", "Yahoo Finance")
    
    st.markdown("---")
    
    st.markdown("### 🎓 Learn More")
    st.markdown("""
    - [Candlestick Patterns](https://www.investopedia.com/trading/candlestick-charting-what-is-it/)
    - [EMA Strategy](https://www.investopedia.com/terms/e/ema.asp)
    - [RSI Indicator](https://www.investopedia.com/terms/r/rsi.asp)
    - [Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)
    """)

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🛠️ Technologies")
    st.markdown("""
    - Python
    - Streamlit
    - Pandas
    - Plotly
    - yFinance
    """)

with col2:
    st.markdown("### 📈 Indicators")
    st.markdown("""
    - EMA (Exponential Moving Average)
    - RSI (Relative Strength Index)
    - More coming soon...
    """)

with col3:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Start with backtesting
    - Test multiple timeframes
    - Compare strategies
    - Export your data
    """)

st.markdown("---")
st.caption("SigmaBot v0.1.0 | Built with Streamlit")
