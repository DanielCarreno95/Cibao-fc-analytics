# ===========================================
# 1_Rendimiento_Colectivo_-_Liga.py — Cibao FC Data Hub
# ===========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from src.data_processing.load_cibao_team_data import load_cibao_team_data
from src.utils.metrics_dictionary import METRICS_DICT
from graficos_de_navaja_suiza import (
    load_data as load_liga_mayor_data,
    make_team_scatter,
    METRIC_OPTIONS,
    DATA_FILE as LIGA_MAYOR_DATA_FILE,
)

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

# === IMPORTA EL TEMA OSCURO GLOBAL + TÍTULOS NARANJA ===
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja

# ---------- CONFIG ----------
st.set_page_config(page_title="Rendimiento Colectivo - Liga", layout="wide")

# ---------- ACTIVAR TEMA OSCURO GLOBAL ----------
inject_dark_theme()

# =======================================================
#  🎨 🎨 FIX GLOBAL PARA MULTISELECT + SELECTBOX + BOTONES
# =======================================================
st.markdown("""
<style>

    /* MULTISELECT — quitar recuadro blanco */
    .stMultiSelect > div {
        background-color: #111 !important;
        border: 1px solid #ff7b00 !important;
        border-radius: 6px !important;
        color: white !important;
    }

    /* Dropdown del multiselect */
    div[data-baseweb="popover"] {
        background-color:#111 !important;
        border:1px solid #ff7b00 !important;
        color:white !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color:#111 !important;
        color:white !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color:#ff7b00 !important;
        color:black !important;
    }

    /* SELECTBOX */
    .stSelectbox div[data-baseweb="select"] {
        background-color:#111 !important;
        border:1px solid #ff7b00 !important;
        color:white !important;
    }

    /* Botón “Borrar filtros” */
    .stButton button {
        background-color:#111 !important;
        border:1px solid #ff7b00 !important;
        color:white !important;
        border-radius:6px !important;
    }
    .stButton button:hover {
        background-color:#ff7b00 !important;
        color:black !important;
    }

</style>
""", unsafe_allow_html=True)
# =======================================================
#  FIN DE FIX GLOBAL
# =======================================================


# ---------- ENCABEZADO VISUAL DEL SIDEBAR ----------
with st.sidebar:
    st.markdown("""
    <h3 style='margin-top:0; color:#ff7b00;'>Análisis Liga</h3>
    <hr style='margin-top:6px; margin-bottom:20px; opacity:0.3;'>
    """, unsafe_allow_html=True)


# ---------- DATA ----------
try:
    df_cibao, df_rivales = load_cibao_team_data()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# Limpieza rápida de columnas
df_cibao.columns = [c.strip().replace("\n", " ").replace("  ", " ") for c in df_cibao.columns]

@st.cache_data
def load_liga_mayor_per90():
    return load_liga_mayor_data(LIGA_MAYOR_DATA_FILE)

try:
    df_liga_mayor = load_liga_mayor_per90()
except Exception as exc:
    st.error(f"❌ Error cargando Liga Mayor per 90: {exc}")
    df_liga_mayor = pd.DataFrame()

# ---------- PAGE TITLE ----------
titulo_naranja("Rendimiento Colectivo — Cibao FC (Liga)")

st.markdown("""
<p style='text-align:center; color:#D1D5DB; font-size:17px;'>
Lectura de <b>modelo de juego</b>, <b>eficiencia por fases</b> y <b>tendencias competitivas</b>.<br>
Diseñado para soporte táctico del staff técnico — decisiones claras, con contexto.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ===============================================
# 🎯 FILTROS GLOBALES (Sidebar + Aplicación completa)
# ===============================================

# --- Detectar últimas 3 jornadas automáticamente ---
if "Jornada" in df_cibao.columns and not df_cibao.empty:
    jornadas_unicas = sorted(df_cibao["Jornada"].dropna().unique())
    ultimas_jornadas = jornadas_unicas[-3:] if len(jornadas_unicas) >= 3 else jornadas_unicas
else:
    ultimas_jornadas = []

# --- Obtener partidos correspondientes ---
if not df_cibao.empty and "Match" in df_cibao.columns:
    default_partidos = (
        df_cibao[df_cibao["Jornada"].isin(ultimas_jornadas)]
        .sort_values("Date")["Match"]
        .unique()
        .tolist()[:5]
    )
else:
    default_partidos = []

# --- Inicialización del estado global ---
if "global_jornadas" not in st.session_state:
    st.session_state["global_jornadas"] = ultimas_jornadas
if "global_partidos" not in st.session_state:
    st.session_state["global_partidos"] = default_partidos


# ===============================================
# 🧭 SIDEBAR — Filtros globales
# ===============================================
with st.sidebar:
    st.subheader("Filtros")

    jornadas_sel = st.multiselect(
        "Selecciona Jornadas (máx 5)",
        options=sorted(df_cibao["Jornada"].unique().tolist()),
        default=st.session_state["global_jornadas"],
        key="sidebar_jornadas",
        max_selections=5,
    )

    partidos_sel = st.multiselect(
        "Selecciona Partidos (máx 5)",
        options=df_cibao["Match"].unique().tolist(),
        default=st.session_state["global_partidos"],
        key="sidebar_partidos",
        max_selections=5,
    )

    # --- Botón para limpiar filtros ---
    if st.button("🔄 Borrar filtros", use_container_width=True):
        st.session_state["global_jornadas"] = ultimas_jornadas
        st.session_state["global_partidos"] = default_partidos
        st.session_state["sidebar_jornadas"] = ultimas_jornadas
        st.session_state["sidebar_partidos"] = default_partidos
        st.toast("Filtros restablecidos a las últimas 3 jornadas ✅", icon="🔁")
        st.rerun()


# ===============================================
# 🧮 SINCRONIZACIÓN
# ===============================================
st.session_state["global_jornadas"] = st.session_state.get("sidebar_jornadas", ultimas_jornadas)
st.session_state["global_partidos"] = st.session_state.get("sidebar_partidos", default_partidos)

jornadas_sel = st.session_state["global_jornadas"]
partidos_sel = st.session_state["global_partidos"]


# ===============================================
# 🔍 FILTRADO DE DATOS
# ===============================================
df_filtrado = df_cibao.copy()
if jornadas_sel and "Jornada" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Jornada"].isin(jornadas_sel)]
if partidos_sel:
    df_filtrado = df_filtrado[df_filtrado["Match"].isin(partidos_sel)]
if df_filtrado.empty and not df_cibao.empty:
    df_filtrado = df_cibao[df_cibao["Jornada"].isin(ultimas_jornadas)]

# ===============================================
# 🧠 HELPERS
# ===============================================
def col_from(metric_name: str):
    col = METRICS_DICT.get(metric_name)
    return col if (col in df_filtrado.columns) else None

def mean_safe(metric_name: str) -> float:
    col = col_from(metric_name)
    if col is None:
        return np.nan
    s = pd.to_numeric(df_filtrado[col], errors="coerce")
    return float(s.mean()) if s.notna().any() else np.nan

def available(metric_names):
    return [m for m in metric_names if col_from(m) is not None]

def warn_missing(metrics, titulo: str):
    missing = [m for m in metrics if col_from(m) is None]
    if missing:
        st.info(f"ℹ️ {titulo}: faltan columnas para {', '.join(missing)}")

# ===============================================
# 🔁 BOTÓN GLOBAL DE REINICIO
# ===============================================
cols_reset = st.columns([4, 1])
with cols_reset[1]:
    if st.button("Restablecer filtros de la página", use_container_width=True):
        for key in list(st.session_state.keys()):
            if any(x in key for x in [
                "jornadas", "matches", "partidos", "metricas", "filtros",
                "tables", "efficiency", "passes", "offensive", "defensive", "tactical"
            ]):
                del st.session_state[key]
        st.toast("Filtros restablecidos a las últimas 3 jornadas ✅", icon="🔄")
        st.rerun()

# ===============================================
# Bloque KPIs
# ===============================================
st.markdown("### Indicadores del último partido")

if not df_filtrado.empty:
    ultimo_partido = df_filtrado.sort_values("Date", ascending=False).iloc[0]
else:
    st.warning("No hay datos disponibles para mostrar los KPIs.")
    st.stop()

fecha_str = "-"
if pd.notna(ultimo_partido.get("Date", None)):
    try:
        fecha_str = pd.to_datetime(ultimo_partido["Date"]).strftime("%d-%m-%Y")
    except Exception:
        fecha_str = str(ultimo_partido.get("Date", ""))

kpi_texts = [
    ("Fecha", fecha_str),
    ("Jornada número", ultimo_partido.get("Jornada", "")),
    ("Partido", ultimo_partido.get("Match", "")),
    ("Resultado Final", ultimo_partido.get("Final Result", "")),
    ("Alineación", ultimo_partido.get("Alineacion", "")),
]

kpi_numericos = [
    ("Goles Esperados (xG)",  ultimo_partido.get("xg", np.nan)),
    ("Posesión (%)",          ultimo_partido.get("possession_percent", np.nan)),
    ("Tarjetas Amarillas",    ultimo_partido.get("yellow_cards", np.nan)),
    ("Tarjetas Rojas",        ultimo_partido.get("red_cards", np.nan)),
]

cols_text = st.columns(len(kpi_texts))
for (label, value), c in zip(kpi_texts, cols_text):
    display = str(value) if pd.notna(value) else "-"
    with c:
        st.markdown(
            f"""
            <div style='background:rgba(25,25,25,0.95);
                        border:1px solid rgba(255,140,0,0.35);
                        border-radius:14px;padding:18px;
                        text-align:center;box-shadow:0 0 18px rgba(255,140,0,0.12);'>
                <div style='font-size:1.3rem;color:#FF8C00;font-weight:700;'>{display}</div>
                <div style='color:#cfcfcf;font-size:0.9rem;'>{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

cols_num = st.columns(len(kpi_numericos))
for (label, val), c in zip(kpi_numericos, cols_num):
    display = "-" if pd.isna(val) else (str(int(val)) if "Tarjetas" in label else f"{val:.2f}")
    with c:
        st.markdown(
            f"""
            <div style='background:rgba(25,25,25,0.95);
                        border:1px solid rgba(255,140,0,0.35);
                        border-radius:14px;padding:18px;
                        text-align:center;box-shadow:0 0 18px rgba(255,140,0,0.12);'>
                <div style='font-size:2.1rem;color:#FF8C00;font-weight:900;'>{display}</div>
                <div style='color:#cfcfcf;font-size:0.95rem;'>{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# 🎨 PALETA
# ==============================
CIBAO_ORANGE = "#FF8C00"
CIBAO_ORANGE_LIGHT = "#FFA64D"
CIBAO_BLACK = "#111111"
CIBAO_GRAY = "#D3D3D3"
CIBAO_DARKGRAY = "#1B1B1B"

# ==============================
# Bloque 0 — COMPARATIVA LIGA
# ==============================
if not df_liga_mayor.empty:

    st.markdown(f"""
        <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
            Comparativa liga (Cibao vs próximo rival)
        </h2>
        <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
            Evalúa el rendimiento del Cibao FC frente a su próximo rival,
            considerando métricas ofensivas y defensivas clave.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1])

    team_options = sorted(
        {
            str(t)
            for t in df_liga_mayor["Team"].dropna().unique()
            if str(t).strip().lower() != "cibao"
        }
    )

    if team_options:
        opponent_choice = col_sel1.selectbox("Próximo rival", team_options)
        metric_labels = list(METRIC_OPTIONS.keys())

        x_default = metric_labels.index("Goles por 90") if "Goles por 90" in metric_labels else 0
        y_default = metric_labels.index("Goles en contra por 90") if "Goles en contra por 90" in metric_labels else 1

        x_choice = col_sel2.selectbox("Métrica ofensiva (eje X)", metric_labels, index=x_default)
        y_choice = col_sel3.selectbox("Métrica defensiva (eje Y)", metric_labels, index=y_default)

        filters = {"Competition": lambda s: s.str.contains("Liga", case=False, na=False)}

        x_column = METRIC_OPTIONS.get(x_choice)
        y_column = METRIC_OPTIONS.get(y_choice)

        fig_radar, resumen_radar, _ = make_team_scatter(
            df_liga_mayor,
            primary_team="Cibao",
            opponent=opponent_choice,
            x_metric=x_column,
            y_metric=y_column,
            x_label=x_choice,
            y_label=y_choice,
            title=f"Liga Mayor — {x_choice} vs {y_choice}",
            filters=filters,
        )

        # ======================
        #  FIX — FONDO OSCURO PLOTLY
        # ======================
        fig_radar.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        if resumen_radar:
            st.caption(f"Resumen: {resumen_radar}")

else:
    st.warning("No se pudo cargar el dataset per 90 de Liga Mayor.")
