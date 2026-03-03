import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Lemon Clinic — SEO Report",
    page_icon="https://lemonclinic.es/favicon.ico",
    layout="wide",
)

COLORS = {
    "primary": "#C8E64A",
    "dark": "#1A1A1A",
    "gray": "#2D2D2D",
    "light_gray": "#F5F5F5",
    "white": "#FFFFFF",
    "green": "#22C55E",
    "red": "#EF4444",
    "blue": "#3B82F6",
    "muted": "#9CA3AF",
    "accent": "#A3D139",
}

# ---------------------------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {{
        background-color: {COLORS["dark"]};
        color: {COLORS["white"]};
        font-family: 'Inter', sans-serif;
    }}
    .stApp header {{visibility: hidden;}}
    .block-container {{padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px;}}

    h1, h2, h3, h4 {{color: {COLORS["white"]} !important; font-weight: 600 !important;}}

    .metric-card {{
        background: {COLORS["gray"]};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }}
    .metric-value {{
        font-size: 2.4rem;
        font-weight: 700;
        color: {COLORS["primary"]};
        line-height: 1.1;
    }}
    .metric-label {{
        font-size: 0.85rem;
        color: {COLORS["muted"]};
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-delta {{
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }}
    .delta-positive {{color: {COLORS["green"]};}}
    .delta-negative {{color: {COLORS["red"]};}}

    .section-divider {{
        border: none;
        border-top: 1px solid #333;
        margin: 2.5rem 0 1.5rem 0;
    }}
    .section-tag {{
        display: inline-block;
        background: {COLORS["gray"]};
        color: {COLORS["primary"]};
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }}

    /* dataframe styling */
    .stDataFrame div[data-testid="stDataFrameResizable"] {{
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }}

    /* tabs */
    .stTabs [data-baseweb="tab-list"] {{gap: 0.5rem;}}
    .stTabs [data-baseweb="tab"] {{
        background: {COLORS["gray"]};
        border-radius: 8px;
        color: {COLORS["muted"]};
        padding: 0.5rem 1.2rem;
        font-size: 0.85rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS["primary"]} !important;
        color: {COLORS["dark"]} !important;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# HELPER: plotly layout defaults
# ---------------------------------------------------------------------------
def base_layout(fig, height=400):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=COLORS["white"], size=12),
        margin=dict(l=40, r=20, t=30, b=40),
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11),
        ),
        xaxis=dict(gridcolor="#333", showline=False),
        yaxis=dict(gridcolor="#333", showline=False),
    )
    return fig


def metric_card(label, value, delta=None, prefix="", suffix=""):
    delta_html = ""
    if delta is not None:
        cls = "delta-positive" if delta >= 0 else "delta-negative"
        sign = "+" if delta >= 0 else ""
        delta_html = f'<div class="metric-delta {cls}">{sign}{delta}%</div>'
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """


# ===================================================================
# DATA
# ===================================================================

# -- Monthly organic (GSC) --
months_labels = ["Ago 25", "Sep 25", "Oct 25", "Nov 25", "Dic 25", "Ene 26", "Feb 26"]
months_iso = ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02"]

gsc_clicks =       [861, 1223, 1620, 1799, 1299, 1464, 1387]
gsc_impressions =   [42906, 72040, 110320, 157203, 161199, 173380, 153041]
gsc_ctr =           [2.01, 1.70, 1.47, 1.14, 0.81, 0.84, 0.91]
gsc_position =      [23.5, 17.7, 13.2, 11.8, 15.9, 14.7, 12.5]
gsc_queries =       [2268, 4439, 5971, 7828, 8968, 8322, 8279]
gsc_queries_click = [104, 140, 195, 252, 197, 195, 195]

# -- SEM keywords in organic (GSC) --
sem_kw_found =  [25, 24, 26, 38, 52, 43, 45]
sem_org_clicks = [8, 8, 10, 9, 5, 8, 12]
sem_org_impr =   [1093, 1401, 1410, 1824, 1985, 2283, 2020]

# -- Category impressions (organic) --
categories_data = {
    "HIFU":          [356, 832, 888, 1061, 809, 887, 1038],
    "IPL":           [2, 35, 95, 69, 72, 149, 139],
    "Armonizacion":  [0, 0, 1, 15, 116, 211, 181],
    "Carboxiterapia":[225, 274, 118, 113, 259, 452, 228],
    "Mesoterapia":   [255, 0, 30, 238, 244, 213, 102],
    "Estetica":      [11, 30, 50, 50, 31, 55, 71],
    "Endolaser":     [57, 41, 8, 10, 4, 42, 48],
    "Morpheus8":     [142, 164, 163, 150, 144, 123, 90],
}

# -- Top SEM keywords that grew in organic --
top_growth = pd.DataFrame([
    {"Keyword": "hifu facial", "Ago Impr": 0, "Feb Impr": 441, "Feb Pos": 8.5, "Feb Clics": 0},
    {"Keyword": "armonizacion facial", "Ago Impr": 0, "Feb Impr": 158, "Feb Pos": 42.0, "Feb Clics": 1},
    {"Keyword": "hifu precio", "Ago Impr": 1, "Feb Impr": 100, "Feb Pos": 63.6, "Feb Clics": 0},
    {"Keyword": "ipl barcelona", "Ago Impr": 0, "Feb Impr": 84, "Feb Pos": 65.3, "Feb Clics": 2},
    {"Keyword": "hifu facial barcelona", "Ago Impr": 105, "Feb Impr": 175, "Feb Pos": 22.8, "Feb Clics": 2},
    {"Keyword": "clinica estetica castelldefels", "Ago Impr": 3, "Feb Impr": 57, "Feb Pos": 7.8, "Feb Clics": 0},
    {"Keyword": "fotorejuvenecimiento facial ipl", "Ago Impr": 2, "Feb Impr": 55, "Feb Pos": 68.2, "Feb Clics": 0},
    {"Keyword": "endolaser barcelona", "Ago Impr": 0, "Feb Impr": 44, "Feb Pos": 10.4, "Feb Clics": 1},
    {"Keyword": "carboxiterapia ojeras", "Ago Impr": 38, "Feb Impr": 74, "Feb Pos": 60.9, "Feb Clics": 0},
    {"Keyword": "tratamiento hifu", "Ago Impr": 0, "Feb Impr": 30, "Feb Pos": 42.8, "Feb Clics": 0},
    {"Keyword": "morpheus8 barcelona", "Ago Impr": 38, "Feb Impr": 66, "Feb Pos": 43.2, "Feb Clics": 0},
    {"Keyword": "laser co2 barcelona", "Ago Impr": 0, "Feb Impr": 27, "Feb Pos": 44.9, "Feb Clics": 0},
    {"Keyword": "hifu corporal", "Ago Impr": 0, "Feb Impr": 20, "Feb Pos": 2.9, "Feb Clics": 0},
    {"Keyword": "hifu treatment", "Ago Impr": 5, "Feb Impr": 23, "Feb Pos": 12.1, "Feb Clics": 0},
    {"Keyword": "ultraformer barcelona", "Ago Impr": 43, "Feb Impr": 51, "Feb Pos": 6.9, "Feb Clics": 1},
])
top_growth["Cambio"] = top_growth["Feb Impr"] - top_growth["Ago Impr"]

# -- New SEM keywords that appeared in organic --
new_kws = pd.DataFrame([
    {"Keyword": "hifu facial", "Impresiones": 441, "Clics": 0, "Posicion": 8.5},
    {"Keyword": "armonizacion facial", "Impresiones": 158, "Clics": 1, "Posicion": 42.0},
    {"Keyword": "ipl barcelona", "Impresiones": 84, "Clics": 2, "Posicion": 65.3},
    {"Keyword": "endolaser barcelona", "Impresiones": 44, "Clics": 1, "Posicion": 10.4},
    {"Keyword": "tratamiento hifu", "Impresiones": 30, "Clics": 0, "Posicion": 42.8},
    {"Keyword": "laser co2 barcelona", "Impresiones": 27, "Clics": 0, "Posicion": 44.9},
    {"Keyword": "hifu corporal", "Impresiones": 20, "Clics": 0, "Posicion": 2.9},
    {"Keyword": "armonizacion facial precio", "Impresiones": 13, "Clics": 0, "Posicion": 70.5},
    {"Keyword": "tratamiento armonizacion facial", "Impresiones": 8, "Clics": 0, "Posicion": 58.6},
    {"Keyword": "endolaser cerca de mi", "Impresiones": 6, "Clics": 1, "Posicion": 9.8},
    {"Keyword": "medicina estetica", "Impresiones": 5, "Clics": 0, "Posicion": 4.2},
    {"Keyword": "carboxiterapia cerca de mi", "Impresiones": 4, "Clics": 0, "Posicion": 31.8},
    {"Keyword": "endolaser precio", "Impresiones": 4, "Clics": 0, "Posicion": 44.8},
    {"Keyword": "mesoterapia capilar precio", "Impresiones": 2, "Clics": 0, "Posicion": 37.5},
    {"Keyword": "aumento de labios cerca de mi", "Impresiones": 2, "Clics": 2, "Posicion": 2.0},
])

# -- GA4 engagement (Feb 2026) --
ga4_engagement = pd.DataFrame([
    {"Canal": "Organic Search", "Sesiones": 59, "Engagement": 64.4, "Duracion": 410, "Pag/Sesion": 3.05, "Bounce": 35.6},
    {"Canal": "Direct", "Sesiones": 165, "Engagement": 52.1, "Duracion": 72, "Pag/Sesion": 1.75, "Bounce": 47.9},
    {"Canal": "Organic Social", "Sesiones": 37, "Engagement": 59.5, "Duracion": 51, "Pag/Sesion": 1.38, "Bounce": 40.5},
    {"Canal": "Organic Shopping", "Sesiones": 10, "Engagement": 80.0, "Duracion": 201, "Pag/Sesion": 2.40, "Bounce": 20.0},
    {"Canal": "Referral", "Sesiones": 5, "Engagement": 60.0, "Duracion": 32, "Pag/Sesion": 1.20, "Bounce": 40.0},
])


# ===================================================================
# LAYOUT
# ===================================================================

# -- Header --
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;">
        <div style="background:{COLORS['primary']}; width:8px; height:48px; border-radius:4px;"></div>
        <div>
            <h1 style="margin:0; font-size:1.8rem;">Lemon Clinic</h1>
            <p style="margin:0; color:{COLORS['muted']}; font-size:0.9rem;">
                Reporte SEO &mdash; Agosto 2025 a Febrero 2026
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -- Snapshot KPIs --
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Foto inicial vs actual</span>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("Clics organicos / mes", f"{gsc_clicks[-1]:,}", delta=round((gsc_clicks[-1]/gsc_clicks[0]-1)*100)), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Impresiones / mes", f"{gsc_impressions[-1]//1000}K", delta=round((gsc_impressions[-1]/gsc_impressions[0]-1)*100)), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Queries indexadas", f"{gsc_queries[-1]:,}", delta=round((gsc_queries[-1]/gsc_queries[0]-1)*100)), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Posicion media", f"{gsc_position[-1]}", delta=round((1-gsc_position[-1]/gsc_position[0])*100)), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("KWs SEM en organico", f"{sem_kw_found[-1]}", delta=round((sem_kw_found[-1]/sem_kw_found[0]-1)*100)), unsafe_allow_html=True)


# -- Before / After snapshot --
st.markdown("")
col_before, col_after = st.columns(2)
with col_before:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 3px solid {COLORS['muted']};">
            <div class="metric-label">Agosto 2025 &mdash; Inicio campana</div>
            <div style="display:flex; justify-content:space-around; margin-top:1rem;">
                <div><div class="metric-label">Clics</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['muted']};">861</div></div>
                <div><div class="metric-label">Impresiones</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['muted']};">42.9K</div></div>
                <div><div class="metric-label">Posicion</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['muted']};">23.5</div></div>
                <div><div class="metric-label">Queries</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['muted']};">2,268</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_after:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 3px solid {COLORS['primary']};">
            <div class="metric-label">Febrero 2026 &mdash; Actual</div>
            <div style="display:flex; justify-content:space-around; margin-top:1rem;">
                <div><div class="metric-label">Clics</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']};">1,387</div></div>
                <div><div class="metric-label">Impresiones</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']};">153K</div></div>
                <div><div class="metric-label">Posicion</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']};">12.5</div></div>
                <div><div class="metric-label">Queries</div><div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']};">8,279</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===================================================================
# SECTION: Organic evolution
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Evolucion organica</span>', unsafe_allow_html=True)
st.markdown("### Clics e impresiones mensuales")

fig_main = go.Figure()
fig_main.add_trace(go.Bar(
    x=months_labels, y=gsc_clicks, name="Clics",
    marker_color=COLORS["primary"], marker_cornerradius=6,
    text=gsc_clicks, textposition="outside", textfont=dict(size=11, color=COLORS["white"]),
))
fig_main.add_trace(go.Scatter(
    x=months_labels, y=[i / 1000 for i in gsc_impressions], name="Impresiones (K)",
    yaxis="y2", line=dict(color=COLORS["muted"], width=2.5), mode="lines+markers",
    marker=dict(size=7),
))
fig_main.update_layout(
    yaxis=dict(title="Clics", gridcolor="#333", showline=False),
    yaxis2=dict(title="Impresiones (K)", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", showline=False),
    barmode="group",
)
base_layout(fig_main, height=380)
st.plotly_chart(fig_main, use_container_width=True)

# Position + queries
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Posicion media")
    fig_pos = go.Figure()
    fig_pos.add_trace(go.Scatter(
        x=months_labels, y=gsc_position, mode="lines+markers+text",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=9, color=COLORS["primary"]),
        text=[f"{p}" for p in gsc_position], textposition="top center",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    fig_pos.update_yaxes(autorange="reversed", gridcolor="#333")
    base_layout(fig_pos, height=300)
    st.plotly_chart(fig_pos, use_container_width=True)

with col_b:
    st.markdown("### Universo de queries")
    fig_q = go.Figure()
    fig_q.add_trace(go.Bar(
        x=months_labels, y=gsc_queries, marker_color=COLORS["accent"],
        marker_cornerradius=6,
        text=[f"{q:,}" for q in gsc_queries], textposition="outside",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    base_layout(fig_q, height=300)
    st.plotly_chart(fig_q, use_container_width=True)


# ===================================================================
# SECTION: SEM Halo effect
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Efecto halo SEM &rarr; SEO</span>', unsafe_allow_html=True)
st.markdown("### Keywords de la campana SEM que aparecen en organico")

col_h1, col_h2 = st.columns(2)

with col_h1:
    fig_sem = go.Figure()
    fig_sem.add_trace(go.Bar(
        x=months_labels, y=sem_kw_found, name="Keywords encontradas",
        marker_color=COLORS["primary"], marker_cornerradius=6,
        text=sem_kw_found, textposition="outside",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    base_layout(fig_sem, height=320)
    fig_sem.update_layout(showlegend=False)
    st.plotly_chart(fig_sem, use_container_width=True)

with col_h2:
    fig_sem_impr = go.Figure()
    fig_sem_impr.add_trace(go.Scatter(
        x=months_labels, y=sem_org_impr, mode="lines+markers+text",
        fill="tozeroy", fillcolor="rgba(200,230,74,0.15)",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=8),
        text=[f"{v:,}" for v in sem_org_impr], textposition="top center",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    fig_sem_impr.update_layout(yaxis_title="Impresiones organicas")
    base_layout(fig_sem_impr, height=320)
    st.plotly_chart(fig_sem_impr, use_container_width=True)


# ===================================================================
# SECTION: Growth by category
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Crecimiento por servicio</span>', unsafe_allow_html=True)
st.markdown("### Impresiones organicas de keywords SEM por categoria")

cat_colors = [
    COLORS["primary"], "#6EE7B7", "#93C5FD", "#FCD34D",
    "#F9A8D4", "#A78BFA", "#FB923C", "#67E8F9",
]

fig_cat = go.Figure()
for i, (cat, vals) in enumerate(categories_data.items()):
    fig_cat.add_trace(go.Scatter(
        x=months_labels, y=vals, name=cat,
        mode="lines+markers", line=dict(width=2.5, color=cat_colors[i % len(cat_colors)]),
        marker=dict(size=6),
    ))
base_layout(fig_cat, height=400)
fig_cat.update_layout(legend=dict(font=dict(size=10)))
st.plotly_chart(fig_cat, use_container_width=True)

# Before/after by category
st.markdown("#### Comparativa Ago 2025 vs Feb 2026")
cat_comparison = []
for cat, vals in categories_data.items():
    aug, feb = vals[0], vals[-1]
    if aug > 0:
        growth_pct = round((feb / aug - 1) * 100)
    elif feb > 0:
        growth_pct = "Nuevo"
    else:
        growth_pct = 0
    cat_comparison.append({"Servicio": cat, "Ago 2025": aug, "Feb 2026": feb, "Cambio": growth_pct})

df_cat = pd.DataFrame(cat_comparison)

fig_cat_bar = go.Figure()
fig_cat_bar.add_trace(go.Bar(
    y=df_cat["Servicio"], x=df_cat["Ago 2025"], name="Ago 2025",
    orientation="h", marker_color=COLORS["muted"], marker_cornerradius=4,
))
fig_cat_bar.add_trace(go.Bar(
    y=df_cat["Servicio"], x=df_cat["Feb 2026"], name="Feb 2026",
    orientation="h", marker_color=COLORS["primary"], marker_cornerradius=4,
))
fig_cat_bar.update_layout(barmode="group", yaxis=dict(autorange="reversed"))
base_layout(fig_cat_bar, height=350)
st.plotly_chart(fig_cat_bar, use_container_width=True)


# ===================================================================
# SECTION: Keyword detail tables
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Detalle de keywords</span>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Top crecimiento", "Nuevas en organico"])

with tab1:
    st.markdown("#### Keywords SEM con mayor crecimiento de impresiones organicas")
    display_growth = top_growth[["Keyword", "Ago Impr", "Feb Impr", "Cambio", "Feb Pos", "Feb Clics"]].copy()
    display_growth.index = range(1, len(display_growth) + 1)
    st.dataframe(
        display_growth.style
            .background_gradient(subset=["Cambio"], cmap="YlGn", vmin=0)
            .format({"Feb Pos": "{:.1f}"}),
        use_container_width=True,
        height=560,
    )

with tab2:
    st.markdown("#### Keywords SEM que no existian en organico en Ago 2025 y ahora si aparecen")
    display_new = new_kws.copy()
    display_new.index = range(1, len(display_new) + 1)
    st.dataframe(
        display_new.style
            .background_gradient(subset=["Impresiones"], cmap="YlGn", vmin=0)
            .format({"Posicion": "{:.1f}"}),
        use_container_width=True,
        height=560,
    )


# ===================================================================
# SECTION: GA4 Engagement quality
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<span class="section-tag">Calidad del trafico &mdash; GA4</span>', unsafe_allow_html=True)
st.markdown("### Engagement por canal (Feb 2026)")

col_e1, col_e2, col_e3 = st.columns(3)

with col_e1:
    fig_eng = go.Figure(go.Bar(
        x=ga4_engagement["Canal"], y=ga4_engagement["Engagement"],
        marker_color=[COLORS["primary"] if c == "Organic Search" else COLORS["gray"] for c in ga4_engagement["Canal"]],
        marker_cornerradius=6,
        text=[f"{v}%" for v in ga4_engagement["Engagement"]], textposition="outside",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    fig_eng.update_layout(yaxis_title="Engagement rate %")
    base_layout(fig_eng, height=320)
    st.plotly_chart(fig_eng, use_container_width=True)

with col_e2:
    fig_dur = go.Figure(go.Bar(
        x=ga4_engagement["Canal"], y=ga4_engagement["Duracion"],
        marker_color=[COLORS["primary"] if c == "Organic Search" else COLORS["gray"] for c in ga4_engagement["Canal"]],
        marker_cornerradius=6,
        text=[f"{v}s" for v in ga4_engagement["Duracion"]], textposition="outside",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    fig_dur.update_layout(yaxis_title="Duracion media (seg)")
    base_layout(fig_dur, height=320)
    st.plotly_chart(fig_dur, use_container_width=True)

with col_e3:
    fig_pag = go.Figure(go.Bar(
        x=ga4_engagement["Canal"], y=ga4_engagement["Pag/Sesion"],
        marker_color=[COLORS["primary"] if c == "Organic Search" else COLORS["gray"] for c in ga4_engagement["Canal"]],
        marker_cornerradius=6,
        text=[f"{v}" for v in ga4_engagement["Pag/Sesion"]], textposition="outside",
        textfont=dict(size=11, color=COLORS["white"]),
    ))
    fig_pag.update_layout(yaxis_title="Paginas / sesion")
    base_layout(fig_pag, height=320)
    st.plotly_chart(fig_pag, use_container_width=True)


# ===================================================================
# FOOTER
# ===================================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center; color:{COLORS['muted']}; font-size:0.75rem; padding:1rem 0;">
        Datos extraidos de Google Search Console y Google Analytics 4 &mdash; lemonclinic.es
        <br>Periodo: Agosto 2025 &ndash; Febrero 2026
    </div>
    """,
    unsafe_allow_html=True,
)
