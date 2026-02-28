"""
Sammenligning - Korrelasjon mellom to aksjer
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from src.utils.yahoo_finance import download_yf, get_symbol_data

st.set_page_config(page_title="Sammenligning - SigmaBott", page_icon="📈", layout="wide")

st.markdown("### Aksjesammenligning og korrelasjon")

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Sammenligningsinnstillinger")

symbol_a = st.sidebar.text_input("Aksje A", value="AAPL")
symbol_b = st.sidebar.text_input("Aksje B", value="MSFT")

interval = st.sidebar.selectbox(
    "Intervall",
    options=["1h", "4h", "1d", "1wk"],
    index=2
)

period = st.sidebar.selectbox(
    "Periode",
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    index=5
)

rolling_window = st.sidebar.slider(
    "Rullerende korrelasjon (perioder)",
    min_value=5,
    max_value=120,
    value=30,
    step=1
)

if st.sidebar.button("🔄 Oppdater data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Data oppdateres ved hver oppdatering")

# ── Data ─────────────────────────────────────────────────────────────────────
if not symbol_a.strip() or not symbol_b.strip():
    st.info("Skriv inn to aksjesymboler i sidepanelet for å starte sammenligningen.")
    st.stop()

symbol_a = symbol_a.strip().upper()
symbol_b = symbol_b.strip().upper()

data_a = get_symbol_data(symbol_a, period, interval)
data_b = get_symbol_data(symbol_b, period, interval)

if not data_a or data_a["data"] is None:
    st.error(f"Kunne ikke laste data for {symbol_a}. Sjekk at symbolet er gyldig.")
    st.stop()

if not data_b or data_b["data"] is None:
    st.error(f"Kunne ikke laste data for {symbol_b}. Sjekk at symbolet er gyldig.")
    st.stop()

df_a = data_a["data"]["Close"].rename(symbol_a)
df_b = data_b["data"]["Close"].rename(symbol_b)

# Align on common dates
combined = pd.concat([df_a, df_b], axis=1).dropna()

if combined.empty:
    st.error("Ingen overlappende handelsdager mellom de to aksjene for valgt periode.")
    st.stop()

# Log returns
returns = combined.pct_change().dropna()

# Pearson correlation (full period)
corr_full = returns[symbol_a].corr(returns[symbol_b])

# Rolling correlation
rolling_corr = returns[symbol_a].rolling(rolling_window).corr(returns[symbol_b])

# ── Metrics ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"{symbol_a} siste pris", f"${data_a['price']:.2f}", f"{data_a['change']:+.2f}%")
with col2:
    st.metric(f"{symbol_b} siste pris", f"${data_b['price']:.2f}", f"{data_b['change']:+.2f}%")
with col3:
    corr_color = "normal"
    st.metric("Pearson-korrelasjon", f"{corr_full:.4f}")
with col4:
    last_rolling = rolling_corr.dropna().iloc[-1] if not rolling_corr.dropna().empty else float("nan")
    st.metric(f"Rullerende korrelasjon ({rolling_window}p)", f"{last_rolling:.4f}")

st.markdown("---")

# ── Plot 1: Normaliserte priser ───────────────────────────────────────────────
st.markdown("#### Normalisert prisutvikling")

norm_a = combined[symbol_a] / combined[symbol_a].iloc[0] * 100
norm_b = combined[symbol_b] / combined[symbol_b].iloc[0] * 100

fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=combined.index, y=norm_a,
    name=symbol_a, line=dict(color="#4C9BE8")
))
fig_price.add_trace(go.Scatter(
    x=combined.index, y=norm_b,
    name=symbol_b, line=dict(color="#F4A261")
))
fig_price.update_layout(
    height=350,
    yaxis_title="Indeksert pris (base = 100)",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.02, x=0)
)
st.plotly_chart(fig_price, use_container_width=True)

# ── Plot 2: Rullerende korrelasjon ────────────────────────────────────────────
st.markdown(f"#### Rullerende {rolling_window}-perioders korrelasjon")

fig_roll = go.Figure()
fig_roll.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig_roll.add_hline(y=1,  line_dash="dot",  line_color="green", opacity=0.4)
fig_roll.add_hline(y=-1, line_dash="dot",  line_color="red",   opacity=0.4)
fig_roll.add_trace(go.Scatter(
    x=rolling_corr.index,
    y=rolling_corr,
    name=f"Korrelasjon ({rolling_window}p)",
    line=dict(color="#A29BFE"),
    fill="tozeroy",
    fillcolor="rgba(162,155,254,0.15)"
))
fig_roll.update_layout(
    height=300,
    yaxis=dict(title="Korrelasjon", range=[-1.1, 1.1]),
    hovermode="x unified"
)
st.plotly_chart(fig_roll, use_container_width=True)

# ── Plot 3: Scatter – daglige avkastninger ────────────────────────────────────
st.markdown("#### Korrelasjonsspredning – daglig avkastning")

# OLS trendline
x_vals = returns[symbol_a].values
y_vals = returns[symbol_b].values
m, b = np.polyfit(x_vals, y_vals, 1)
x_line = np.linspace(x_vals.min(), x_vals.max(), 200)
y_line = m * x_line + b

fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=returns[symbol_a],
    y=returns[symbol_b],
    mode="markers",
    marker=dict(size=5, color="#4C9BE8", opacity=0.6),
    name="Daglig avkastning",
    text=returns.index.strftime("%Y-%m-%d"),
    hovertemplate="%{text}<br>" + symbol_a + ": %{x:.2%}<br>" + symbol_b + ": %{y:.2%}<extra></extra>"
))
fig_scatter.add_trace(go.Scatter(
    x=x_line,
    y=y_line,
    mode="lines",
    line=dict(color="#F4A261", width=2, dash="dash"),
    name=f"Trendlinje (β={m:.2f})"
))
fig_scatter.update_layout(
    height=450,
    xaxis_title=f"{symbol_a} daglig avkastning",
    yaxis_title=f"{symbol_b} daglig avkastning",
    xaxis=dict(tickformat=".1%"),
    yaxis=dict(tickformat=".1%"),
    hovermode="closest"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.caption(f"Sist oppdatert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("**For å avslutte og returnere til terminalen:** Trykk `Ctrl+C` i terminalvinduet")
