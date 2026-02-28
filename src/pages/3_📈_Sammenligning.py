"""
Sammenligning - Korrelasjon mellom flere aksjer
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from itertools import combinations
from src.utils.yahoo_finance import get_symbol_data

st.set_page_config(page_title="Sammenligning - SigmaBott", page_icon="📈", layout="wide")

st.markdown("### Aksjesammenligning og korrelasjon")

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Sammenligningsinnstillinger")

default_symbols = "AAPL\nMSFT\nGOOGL"
watchlist = st.sidebar.text_area(
    "Symboler (ett per linje, minst 2)",
    value=default_symbols,
    height=120,
)
symbols = [s.strip().upper() for s in watchlist.splitlines() if s.strip()]

interval = st.sidebar.selectbox(
    "Intervall",
    options=["1h", "4h", "1d", "1wk"],
    index=2,
)

period = st.sidebar.selectbox(
    "Periode",
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    index=5,
)

rolling_window = st.sidebar.slider(
    "Rullerende korrelasjon (perioder)",
    min_value=5,
    max_value=120,
    value=30,
    step=1,
)

if st.sidebar.button("🔄 Oppdater data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Data oppdateres ved hver oppdatering")

# ── Validation ────────────────────────────────────────────────────────────────
if len(symbols) < 2:
    st.info("Skriv inn minst to aksjesymboler (ett per linje) i sidepanelet.")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
raw: dict = {}
errors: list = []

for sym in symbols:
    d = get_symbol_data(sym, period, interval)
    if d and d["data"] is not None:
        raw[sym] = d
    else:
        errors.append(sym)

if errors:
    st.warning(f"Kunne ikke laste data for: {', '.join(errors)}. De er utelatt.")

valid_symbols = [s for s in symbols if s in raw]

if len(valid_symbols) < 2:
    st.error("Trenger minst to gyldige symboler for sammenligning.")
    st.stop()

# Align close prices on common trading days
close_series = {sym: raw[sym]["data"]["Close"].rename(sym) for sym in valid_symbols}
combined = pd.concat(close_series.values(), axis=1).dropna()

if combined.empty:
    st.error("Ingen overlappende handelsdager mellom aksjene for valgt periode.")
    st.stop()

returns = combined.pct_change().dropna()

# ── Metrics row ───────────────────────────────────────────────────────────────
metric_cols = st.columns(len(valid_symbols))
for idx, sym in enumerate(valid_symbols):
    with metric_cols[idx]:
        st.metric(
            sym,
            f"${raw[sym]['price']:.2f}",
            f"{raw[sym]['change']:+.2f}%",
        )

st.markdown("---")

# ── Plot 1: Normaliserte priser ───────────────────────────────────────────────
st.markdown("#### Normalisert prisutvikling (base = 100)")

COLORS = [
    "#4C9BE8", "#F4A261", "#A29BFE", "#55EFC4",
    "#FD79A8", "#FDCB6E", "#E17055", "#74B9FF",
    "#00B894", "#D63031",
]

fig_price = go.Figure()
for i, sym in enumerate(valid_symbols):
    col = COLORS[i % len(COLORS)]
    norm = combined[sym] / combined[sym].iloc[0] * 100
    fig_price.add_trace(go.Scatter(
        x=combined.index, y=norm,
        name=sym,
        line=dict(color=col),
    ))
fig_price.update_layout(
    height=350,
    yaxis_title="Indeksert pris (base = 100)",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.02, x=0),
)
st.plotly_chart(fig_price, use_container_width=True)

# ── Plot 2: Korrelasjonsmatrise (heatmap) ─────────────────────────────────────
st.markdown("#### Korrelasjonsmatrise (hele perioden)")

corr_matrix = returns.corr()
z = corr_matrix.values
labels = corr_matrix.columns.tolist()

annotations = []
for i, row in enumerate(labels):
    for j, col in enumerate(labels):
        annotations.append(dict(
            x=col, y=row,
            text=f"{z[i][j]:.2f}",
            showarrow=False,
            font=dict(color="white" if abs(z[i][j]) > 0.5 else "black", size=13),
        ))

fig_heat = go.Figure(go.Heatmap(
    z=z,
    x=labels,
    y=labels,
    colorscale="RdBu",
    zmin=-1, zmax=1,
    colorbar=dict(title="Korrelasjon"),
))
fig_heat.update_layout(
    height=max(300, 80 * len(labels)),
    annotations=annotations,
    xaxis=dict(side="bottom"),
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ── Pair selector ─────────────────────────────────────────────────────────────
all_pairs = [f"{a} / {b}" for a, b in combinations(valid_symbols, 2)]

st.markdown("#### Parvise analyser")
selected_pair = st.selectbox("Velg par", options=all_pairs)

sym_x, sym_y = [s.strip() for s in selected_pair.split("/")]

# ── Plot 3: Rullerende korrelasjon ────────────────────────────────────────────
st.markdown(f"##### Rullerende {rolling_window}-perioders korrelasjon  —  {sym_x} vs {sym_y}")

rolling_corr = returns[sym_x].rolling(rolling_window).corr(returns[sym_y])
last_rolling = rolling_corr.dropna().iloc[-1] if not rolling_corr.dropna().empty else float("nan")
pearson = returns[sym_x].corr(returns[sym_y])

c1, c2 = st.columns(2)
c1.metric("Pearson-korrelasjon (hele perioden)", f"{pearson:.4f}")
c2.metric(f"Rullerende korrelasjon ({rolling_window}p, siste)", f"{last_rolling:.4f}")

fig_roll = go.Figure()
fig_roll.add_hline(y=0,  line_dash="dash", line_color="gray",  opacity=0.5)
fig_roll.add_hline(y=1,  line_dash="dot",  line_color="green", opacity=0.4)
fig_roll.add_hline(y=-1, line_dash="dot",  line_color="red",   opacity=0.4)
fig_roll.add_trace(go.Scatter(
    x=rolling_corr.index,
    y=rolling_corr,
    name=f"Korrelasjon ({rolling_window}p)",
    line=dict(color="#A29BFE"),
    fill="tozeroy",
    fillcolor="rgba(162,155,254,0.15)",
))
fig_roll.update_layout(
    height=300,
    yaxis=dict(title="Korrelasjon", range=[-1.1, 1.1]),
    hovermode="x unified",
)
st.plotly_chart(fig_roll, use_container_width=True)

# ── Plot 4: Scatter – daglige avkastninger ────────────────────────────────────
st.markdown(f"##### Korrelasjonsspredning – daglig avkastning  —  {sym_x} vs {sym_y}")

x_vals = returns[sym_x].values
y_vals = returns[sym_y].values
m, b_coef = np.polyfit(x_vals, y_vals, 1)
x_line = np.linspace(x_vals.min(), x_vals.max(), 200)
y_line = m * x_line + b_coef

fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=returns[sym_x],
    y=returns[sym_y],
    mode="markers",
    marker=dict(size=5, color="#4C9BE8", opacity=0.6),
    name="Daglig avkastning",
    text=returns.index.strftime("%Y-%m-%d"),
    hovertemplate=(
        "%{text}<br>"
        + sym_x + ": %{x:.2%}<br>"
        + sym_y + ": %{y:.2%}<extra></extra>"
    ),
))
fig_scatter.add_trace(go.Scatter(
    x=x_line,
    y=y_line,
    mode="lines",
    line=dict(color="#F4A261", width=2, dash="dash"),
    name=f"Trendlinje (β={m:.2f})",
))
fig_scatter.update_layout(
    height=450,
    xaxis_title=f"{sym_x} daglig avkastning",
    yaxis_title=f"{sym_y} daglig avkastning",
    xaxis=dict(tickformat=".1%"),
    yaxis=dict(tickformat=".1%"),
    hovermode="closest",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.caption(f"Sist oppdatert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("**For å avslutte og returnere til terminalen:** Trykk `Ctrl+C` i terminalvinduet")
