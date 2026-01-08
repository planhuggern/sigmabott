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
st.subheader("Avansert handelsstrategiplatform")

st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Velkommen til SigmaBot!
    
    SigmaBot er en omfattende handelsstrategiplatform som hjelper deg med å analysere, 
    backteste og overvåke handelsstrategier for kryptovaluta og aksjer.
    
    ### 🚀 Funksjoner
    
    - **📊 Live Dashboard** - Overvåk markedsdata og strategiytelse i sanntid
    - **🔬 Strategitester** - Test handelsstrategiene dine på historiske data
    - **📈 Tekniske indikatorer** - EMA, RSI, og mer
    - **📉 Ytelsesanalyse** - Detaljerte metrics, drawdown-analyse, Sharpe ratio
    - **💾 Dataeksport** - Eksporter resultater for videre analyse
    
    ### 🎯 Kom i gang
    
    Velg en seksjon fra sidebaren for å begynne:
    """)
    
    # Navigation cards
    st.markdown("### 📱 Naviger til:")
    
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        st.info("""
        **📊 Dashboard**
        
        Se live markedsdata og overvåk strategiene dine i sanntid.
        Følg flere symboler og få umiddelbar innsikt.
        """)
    
    with nav_col2:
        st.info("""
        **🔬 Backtest**
        
        Test handelsstrategiene dine på historiske data.
        Analyser ytelse, optimaliser parametere og valider ideer.
        """)

with col2:
    st.markdown("### 📊 Rask oversikt")
    
    # Placeholder stats - in a real app these would be dynamic
    st.metric("Støttede symboler", "1000+")
    st.metric("Tilgjengelige strategier", "2+")
    st.metric("Datakilder", "Yahoo Finance")
    
    st.markdown("---")
    
    st.markdown("### 🎓 Lær mer")
    st.markdown("""
    - [Candlestick-mønstre](https://www.investopedia.com/trading/candlestick-charting-what-is-it/)
    - [EMA-strategi](https://www.investopedia.com/terms/e/ema.asp)
    - [RSI-indikator](https://www.investopedia.com/terms/r/rsi.asp)
    - [Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)
    """)

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🛠️ Teknologier")
    st.markdown("""
    - Python
    - Streamlit
    - Pandas
    - Plotly
    - yFinance
    """)

with col2:
    st.markdown("### 📈 Indikatorer")
    st.markdown("""
    - EMA (Eksponensielt glidende gjennomsnitt)
    - RSI (Relative Strength Index)
    - Flere kommer snart...
    """)

with col3:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Start med backtesting
    - Test flere tidsrammer
    - Sammenlign strategier
    - Eksporter dataene dine
    """)

st.markdown("---")
st.caption("SigmaBot v0.1.0 | Bygget med Streamlit")
