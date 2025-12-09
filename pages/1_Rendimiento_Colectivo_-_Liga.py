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
from src.data_processing.loaders import load_per90_data
from src.utils.metrics_dictionary import METRICS_DICT
from graficos_de_navaja_suiza import (
    make_team_scatter,
    METRIC_OPTIONS,
)
# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

# === IMPORTA EL TEMA OSCURO GLOBAL + TÍTULOS NARANJA ===
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja
from src.utils.navigation import render_top_navigation

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Rendimiento Colectivo - Liga",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ACTIVAR TEMA OSCURO GLOBAL ----------
inject_dark_theme()

# ---------- TOP NAVIGATION BAR ----------
render_top_navigation()

# ---------- CUSTOM FONT SIZES ----------
st.markdown("""
<style>
    /* Texto general del cuerpo - mantener grande para legibilidad */
    .stApp {
        font-size: 1.3rem !important;
    }
    
    /* Párrafos y texto general */
    p, div, span, label {
        font-size: 1.3rem !important;
    }
    
    /* Tablas */
    .stDataFrame {
        font-size: 1.4rem !important;
    }
    
    .stDataFrame table {
        font-size: 1.4rem !important;
    }
    
    .stDataFrame th {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        padding: 12px !important;
    }
    
    /* Table headers - black text, bold, orange background */
    div[data-testid="stDataFrame"] table thead th,
    div[data-testid="stDataFrame"] table th,
    .stDataFrame table thead th,
    .stDataFrame table th,
    .dataframe thead th,
    .dataframe th {
        color: #000000 !important;
        font-weight: 900 !important;
        background-color: #ff8c00 !important;
    }
    
    .stDataFrame td {
        font-size: 1.4rem !important;
        padding: 10px !important;
    }
    
    /* Métricas de Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.4rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.3rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        font-size: 1.3rem !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 1.6rem !important;
    }
    
    /* Selectores y controles */
    .stSelectbox label,
    .stRadio label,
    .stMultiselect label {
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox [class*="selectbox"],
    .stRadio [class*="radio"],
    .stMultiselect [class*="multiselect"] {
        font-size: 1.3rem !important;
    }
    
    /* Info boxes y warnings */
    .stInfo, .stWarning, .stError, .stSuccess {
        font-size: 1.3rem !important;
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 12px 24px;
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Botones - exclude navigation buttons to keep them consistent */
    .stButton button:not([key^="home_btn"]):not([key^="nav_"]) {
        font-size: 1.3rem !important;
        padding: 0.5rem 1.5rem !important;
    }
    
    /* Home button - override to match global theme - highest specificity */
    button[key="home_btn_1"],
    .stButton button[key="home_btn_1"],
    div[data-testid="column"] button[key="home_btn_1"],
    div[data-testid="column"] .stButton button[key="home_btn_1"],
    div[data-testid="stButton"] button[key="home_btn_1"],
    div[data-testid="column"] div[data-testid="stButton"] button[key="home_btn_1"] {
        font-size: 24px !important;
        height: 50px !important;
        min-height: 50px !important;
        max-height: 50px !important;
        line-height: 50px !important;
        padding: 0 !important;
        width: 100% !important;
    }
    
</style>
""", unsafe_allow_html=True)

# ---------- FINAL OVERRIDE: Ensure navigation buttons match regular buttons exactly ----------
# This must be AFTER render_top_navigation() to override any conflicting styles
# Use both CSS and JavaScript to ensure styles persist after Streamlit re-renders
st.markdown("""
<style>
    /* FINAL OVERRIDE: Navigation buttons must match regular buttons - maximum specificity */
    /* This ensures they stay consistent even if other CSS loads after */
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"],
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"] *,
    div.top-nav-container div[data-testid="column"] .stButton button[key^="nav_"],
    div.top-nav-container div[data-testid="column"] .stButton button[key^="nav_"] *,
    div.top-nav-container div[data-testid="column"] button[key^="nav_"],
    div.top-nav-container div[data-testid="column"] button[key^="nav_"] *,
    .top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"],
    .top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"] *,
    .top-nav-container div[data-testid="column"] .stButton button[key^="nav_"],
    .top-nav-container div[data-testid="column"] .stButton button[key^="nav_"] *,
    .top-nav-container .stButton button[key^="nav_"],
    .top-nav-container .stButton button[key^="nav_"] *,
    .top-nav-container button[key^="nav_"],
    .top-nav-container button[key^="nav_"] * {
        background-color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        color: black !important;
        font-size: 1.3rem !important;
        padding: 0.5rem 1.5rem !important;
        height: auto !important;
        min-height: auto !important;
        max-height: none !important;
        line-height: normal !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        font-weight: normal !important;
    }
</style>
<script>
    // Force navigation button styles to persist after Streamlit re-renders
    function enforceNavButtonStyles() {
        const navButtons = document.querySelectorAll('button[key^="nav_"]');
        navButtons.forEach(btn => {
            btn.style.backgroundColor = '#ff7b00';
            btn.style.border = '1px solid #ff7b00';
            btn.style.color = 'black';
            btn.style.fontSize = '1.3rem';
            btn.style.padding = '0.5rem 1.5rem';
            btn.style.height = 'auto';
            btn.style.minHeight = 'auto';
            btn.style.maxHeight = 'none';
            btn.style.lineHeight = 'normal';
            btn.style.width = '100%';
            btn.style.minWidth = '0';
            btn.style.maxWidth = '100%';
            btn.style.boxSizing = 'border-box';
            btn.style.fontWeight = 'normal';
        });
    }
    
    // Run immediately and after DOM changes
    enforceNavButtonStyles();
    const observer = new MutationObserver(enforceNavButtonStyles);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also run on page load and after a short delay
    window.addEventListener('load', enforceNavButtonStyles);
    setTimeout(enforceNavButtonStyles, 100);
    setTimeout(enforceNavButtonStyles, 500);
</script>
""", unsafe_allow_html=True)

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
    """Load Liga Mayor data from Wyscout JSON files (same as page 2)."""
    return load_per90_data()

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
    if "Jornada" in df_cibao.columns and ultimas_jornadas:
        default_partidos = (
            df_cibao[df_cibao["Jornada"].isin(ultimas_jornadas)]
            .sort_values("Date")["Match"]
            .unique()
            .tolist()[:5]
        )
    else:
        # If no Jornada column, just get the last 5 matches by date
        default_partidos = (
            df_cibao.sort_values("Date", na_position='last')["Match"]
            .unique()
            .tolist()[-5:]
        )
else:
    default_partidos = []

# --- Inicialización del estado global (solo primera carga) ---
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
        options=sorted(df_cibao["Jornada"].unique().tolist()) if "Jornada" in df_cibao.columns else [],
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
# 🧮 SINCRONIZACIÓN entre sidebar y app
# ===============================================
# Siempre sincroniza el estado global (para que todos los bloques usen lo mismo)
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

# Si no hay selección válida, usa últimas 3 por defecto
if df_filtrado.empty and not df_cibao.empty:
    if "Jornada" in df_cibao.columns and ultimas_jornadas:
        df_filtrado = df_cibao[df_cibao["Jornada"].isin(ultimas_jornadas)]
    else:
        # If no Jornada column, use all data or last 5 matches by date
        df_filtrado = df_cibao.copy()

# ===============================================
# 🧠 HELPERS AUXILIARES
# ===============================================
def col_from(metric_name: str):
    """Devuelve nombre de columna real según METRICS_DICT si existe en df."""
    if not metric_name:
        return None
    col = METRICS_DICT.get(metric_name)
    # Check in df_liga_mayor (Wyscout data) first, then df_filtrado (Excel) as fallback
    if col and not df_liga_mayor.empty and col in df_liga_mayor.columns:
        return col
    if col and col in df_filtrado.columns:
        return col
    return None

def mean_safe(metric_name: str) -> float:
    """Media robusta; retorna np.nan si no existe o no es numérica."""
    col = col_from(metric_name)
    if col is None:
        return np.nan
    # Use df_liga_mayor if column exists there, otherwise use df_filtrado
    if not df_liga_mayor.empty and col in df_liga_mayor.columns:
        df_to_use = df_liga_mayor
    else:
        df_to_use = df_filtrado
    s = pd.to_numeric(df_to_use[col], errors="coerce")
    return float(s.mean()) if s.notna().any() else np.nan

def available(metric_names):
    """Lista de métricas disponibles (existen en df y mapean en el diccionario)."""
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


# ==============================
# 🎨 PALETA INSTITUCIONAL CIBAO FC
# ==============================
CIBAO_ORANGE = "#FF8C00"         # Naranja principal
CIBAO_ORANGE_LIGHT = "#FFA64D"   # Naranja claro
CIBAO_BLACK = "#111111"          # Fondo general
CIBAO_GRAY = "#D3D3D3"           # Texto neutro
CIBAO_DARKGRAY = "#1B1B1B"       # Contenedor gris oscuro
PALETTE_CIBAO = [CIBAO_ORANGE, "#F78E1E", "#2F2F2F", "#777777"]

# ==============================
# 🧩 FUNCIÓN — Multiselect estilizado (idéntico al bloque 0)
# ==============================
def styled_multiselect(label, options, default, key):
    """
    Crea un multiselect visualmente igual al estilo del Bloque 0:
    fondo gris oscuro, borde naranja, texto pequeño y limpio.
    """

    # Contenedor estilo Cibao
    st.markdown(
        f"""
        <div style="
            background-color:{CIBAO_DARKGRAY};
            border:1px solid {CIBAO_ORANGE};
            border-radius:8px;
            padding:6px 8px 4px 8px;
            margin-bottom:10px;
        ">
            <p style="
                color:{CIBAO_GRAY};
                font-size:13px;
                margin-bottom:4px;
            ">{label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Multiselect nativo, compacto y limpio
    selection = st.multiselect(
        "",
        options,
        default=default,
        key=key,
        label_visibility="collapsed",
    )

    return selection

# ==============================
# 🎨 ESTILO GLOBAL — Tipografía y títulos
# ==============================
st.markdown(
    f"""
    <style>
    h2 {{
        color: {CIBAO_ORANGE} !important;
        font-weight: 900 !important;
        font-size: 26px !important;
        text-align: center !important;
        margin-bottom: 4px !important;
    }}
    h3 {{
        color: {CIBAO_ORANGE} !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        text-align: center !important;
        margin-top: 5px !important;
        margin-bottom: 2px !important;
    }}
    p, label {{
        font-size: 13px !important;
        color: {CIBAO_GRAY} !important;
        line-height: 1.4em !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================
# Bloque 0 — ANÁLISIS RÁPIDO CIBAO VS RIVAL
# ==============================

if not df_liga_mayor.empty:

    st.markdown(
        f"""
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

    # ✅ LISTA DE RIVALES LIMPIA Y CORRECTA
    team_options = sorted(
        {
            str(t)
            for t in df_liga_mayor["Team"].dropna().unique()
            if str(t).strip().lower() != "cibao"
        }
    )

    if not team_options:
        st.info("No hay rivales disponibles en el dataset de Liga Mayor.")
        opponent_choice = None
    else:
        opponent_choice = col_sel1.selectbox("Próximo rival", team_options)

        metric_labels = list(METRIC_OPTIONS.keys())

        # Default indices
        x_default = (
            metric_labels.index("Goles por 90")
            if "Goles por 90" in metric_labels
            else 0
        )
        y_default = (
            metric_labels.index("Goles en contra por 90")
            if "Goles en contra por 90" in metric_labels
            else min(1, len(metric_labels) - 1)
        )

        # X-axis metric - Streamlit selectbox has built-in search when you click and type
        x_choice = col_sel2.selectbox(
            "Métrica ofensiva (eje X) - Haz clic y escribe para buscar",
            metric_labels,
            index=x_default if metric_labels else 0,
        )

        # Y-axis metric - Streamlit selectbox has built-in search when you click and type
        y_choice = col_sel3.selectbox(
            "Métrica defensiva (eje Y) - Haz clic y escribe para buscar",
            metric_labels,
            index=y_default if metric_labels else 0,
        )

        filters = {
            "Competition": lambda s: s.str.contains("Liga", case=False, na=False)
        }

        x_column = METRIC_OPTIONS.get(x_choice)
        y_column = METRIC_OPTIONS.get(y_choice)

        if x_column is None or y_column is None:
            st.error("No se encontró la métrica seleccionada en el dataset.")

        else:
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

            # Add spacing to prevent overlap with summary text
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            st.plotly_chart(
                fig_radar,
                use_container_width=True,
                config={"displayModeBar": True},
            )

            if resumen_radar:
                st.caption(f"Resumen: {resumen_radar}")

else:
    st.warning("No se pudo cargar el dataset per 90 de Liga Mayor.")

# ===========================
# EFICIENCIA Y ATAQUE – BLOQUE COMPLETO
# ===========================

st.markdown("""
<h2 style='color:#ff8c00; text-align:center; margin-top:20px;'>Eficiencia y Ataque</h2>
<p style='text-align:center; color:#ccc;'>
Evaluación del comportamiento ofensivo del Cibao FC: producción, eficacia en tiro, tipologías de ataque, balón parado y profundidad en último tercio.
</p>
""", unsafe_allow_html=True)

# ===========================
# DEFINICIÓN DE GRUPOS
# ===========================

grupos = {
    "Producción ofensiva directa": {
        "Goles por partido": "Goals",
        "Goles en contra por partido": "Conceded goals",
        "xG (Goles esperados)": "xG",
    },

    "Eficiencia en el tiro": {
        "Porcentaje de disparos a puerta (%)": "Shot Accuracy %",
        "Disparos por 90": "Shots",
        "Disparos a puerta por 90": "Shots On Target",
    },

    "Patrones de ataque": {
        "Ataques posicionales con disparo (%)": "Positional Attacks With Shot %",
        "Contraataques con disparo (%)": "Counterattacks With Shot %",
        "Ataques posicionales": "Positional Attacks",
        "Contraataques": "Counterattacks",
    },

    "Balón parado y definición": {
        "Corners con disparo": "Corners With Shot",
        "Faltas directas con disparo": "Free Kicks With Shot",
        "Corners": "Corners",
        "Free Kicks": "Free Kicks",
    },

    "Juego interior y profundidad": {
        "Entradas al área por 90": "Penalty Area Entries",
        "Entradas al área con conducción": "Penalty Area Runs",
        "Entradas al área con centros": "Penalty Area Crosses",
        "Toques en el área por 90": "Touches in Penalty Area",
    },
}

# ===========================
# PALETA CIBAO
# ===========================

CIBAO_ORANGE = "#FF8C00"
CIBAO_BLACK = "#111111"
CIBAO_GRAY = "#D3D3D3"
PALETTE_CIBAO = ["#FF8C00"]

# ===========================
# FUNCIÓN DE GRÁFICO + CONCLUSIONES
# ===========================

def plot_group(nombre_grupo, mapping, opponent=None):
    # Use Wyscout data - include both Cibao and opponent if specified
    if df_liga_mayor.empty:
        st.warning(f"No hay datos disponibles para: {nombre_grupo}")
        return
    
    # Filter for Cibao and opponent (if provided)
    teams_to_include = ["Cibao"]
    if opponent and opponent != "Cibao":
        teams_to_include.append(opponent)
    
    df_plot = df_liga_mayor[df_liga_mayor["Team"].isin(teams_to_include)].copy()
    
    if df_plot.empty:
        st.warning(f"No hay datos disponibles para: {nombre_grupo}")
        return

    # Helper function to find column with flexible matching
    def find_column(col_name):
        """Find column in DataFrame with case-insensitive and normalized matching."""
        if col_name in df_plot.columns:
            return col_name
        # Try case-insensitive
        col_lower = col_name.lower()
        for df_col in df_plot.columns:
            if str(df_col).lower() == col_lower:
                return df_col
        # Try normalized (spaces to underscores, etc.)
        col_normalized = col_name.replace(" ", "_").replace("%", "percent").lower()
        for df_col in df_plot.columns:
            df_col_normalized = str(df_col).replace(" ", "_").replace("%", "percent").lower()
            if df_col_normalized == col_normalized:
                return df_col
        return None
    
    # Find available columns using flexible matching
    columnas = []
    etiquetas = {}
    for k, v in mapping.items():
        found_col = find_column(v)
        if found_col:
            columnas.append(found_col)
            etiquetas[found_col] = k
    
    # Special handling for "Shot Accuracy %" - calculate if not found but we have Shots and Shots On Target
    if "Shot Accuracy %" in mapping.values() and not any("Shot Accuracy" in str(col) or "shot.*accuracy" in str(col).lower() for col in columnas):
        shots_col = find_column("Shots") or find_column("totalScoringAtt")
        shots_on_target_col = find_column("Shots On Target") or find_column("ontargetScoringAtt")
        if shots_col and shots_on_target_col:
            # Calculate shot accuracy percentage
            df_plot["Shot Accuracy %"] = (df_plot[shots_on_target_col] / df_plot[shots_col] * 100).fillna(0)
            columnas.append("Shot Accuracy %")
            etiquetas["Shot Accuracy %"] = "Porcentaje de disparos a puerta (%)"
    
    # Special handling for percentage metrics - try to calculate from counts if percentages don't exist
    # For "Positional Attacks With Shot %" and "Counterattacks With Shot %"
    if "Positional Attacks With Shot %" in mapping.values() and not any("Positional Attacks" in str(col) for col in columnas):
        positional_attacks_col = find_column("Positional Attacks") or find_column("Positional Attacks With Shot")
        if positional_attacks_col:
            # If we have the count, we can't calculate percentage without total attacks, so just use the count
            columnas.append(positional_attacks_col)
            etiquetas[positional_attacks_col] = "Ataques posicionales"
    
    if "Counterattacks With Shot %" in mapping.values() and not any("Counterattacks" in str(col) for col in columnas):
        counterattacks_col = find_column("Counterattacks") or find_column("Counterattacks With Shot")
        if counterattacks_col:
            columnas.append(counterattacks_col)
            etiquetas[counterattacks_col] = "Contraataques"
    
    # For set pieces - try both singular and plural, and with/without "With Shot"
    if "Corners With Shot" in mapping.values() or "Corners With Shot %" in mapping.values():
        corners_col = find_column("Corners With Shot") or find_column("Corners With Shots") or find_column("Corners")
        if corners_col and corners_col not in columnas:
            columnas.append(corners_col)
            etiquetas[corners_col] = "Corners con disparo" if "With Shot" in str(corners_col) else "Corners"
    
    if "Free Kicks With Shot" in mapping.values() or "Free Kicks With Shot %" in mapping.values():
        free_kicks_col = find_column("Free Kicks With Shot") or find_column("Free Kicks With Shots") or find_column("Free Kicks")
        if free_kicks_col and free_kicks_col not in columnas:
            columnas.append(free_kicks_col)
            etiquetas[free_kicks_col] = "Faltas directas con disparo" if "With Shot" in str(free_kicks_col) else "Free Kicks"

    if len(columnas) == 0:
        st.warning(f"No hay métricas disponibles para: {nombre_grupo}")
        return

    # Ensure all numeric columns are properly converted to float (handle comma decimals)
    for col in columnas:
        if col in df_plot.columns:
            # Convert to string first, replace commas with periods, then to float
            df_plot[col] = pd.to_numeric(
                df_plot[col].astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            )
    
    # Calculate means per team
    df_means = df_plot.groupby("Team")[columnas].mean().reset_index()
    
    # Melt to long format for plotting
    df_melted = df_means.melt(
        id_vars=["Team"],
        value_vars=columnas,
        var_name="metric",
        value_name="valor"
    )
    df_melted["label"] = df_melted["metric"].map(etiquetas)
    
    # Ensure valor is numeric and format consistently
    df_melted["valor"] = pd.to_numeric(df_melted["valor"], errors='coerce').fillna(0)
    
    # Sort by metric and team for consistent display
    df_melted = df_melted.sort_values(["metric", "Team"])

    # Create grouped bar chart
    fig = px.bar(
        df_melted,
        x="valor",
        y="label",
        color="Team",
        orientation="h",
        text_auto=".2f",
        color_discrete_map={
            "Cibao": CIBAO_ORANGE,
            opponent: CIBAO_GRAY if opponent else CIBAO_ORANGE
        } if opponent else {team: CIBAO_ORANGE for team in df_melted["Team"].unique()},
        barmode="group",
    )

    fig.update_layout(
        height=300,
        template="plotly_dark",
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        title_x=0.5,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=bool(opponent),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ) if opponent else None,
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # -------- CONCLUSIONES TÁCTICAS --------
    # Get Cibao's data for conclusions
    df_cibao_only = df_melted[df_melted["Team"] == "Cibao"].copy()
    if not df_cibao_only.empty:
        max_row = df_cibao_only.loc[df_cibao_only["valor"].idxmax()]
        min_row = df_cibao_only.loc[df_cibao_only["valor"].idxmin()]

        conclusion = f"""
        <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE}; margin-top:-8px; margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>

        • <b>Punto fuerte:</b> El equipo muestra mayor impacto en <b>{max_row['label']}</b>,
          acción que está contribuyendo directamente al modelo ofensivo.<br><br>

        • <b>Área con menor incidencia:</b> El valor más bajo corresponde a <b>{min_row['label']}</b>,
          indicador de un comportamiento aún mejorable dentro de la estructura ofensiva.<br><br>
        </div>
        """

        st.markdown(conclusion, unsafe_allow_html=True)

# ============================================================
# 🔶 CREACIÓN DE LAS 5 PESTAÑAS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Eficiencia y Ataque",
    "Construcción y Pases",
    "Defensa y Eficiencia",
    "Distribución Táctica",
    "Análisis Comparativo (Tablas)"
])


# ============================================================
# 🔶 CONTENIDO DE CADA PESTAÑA
# ============================================================

with tab1:

    st.markdown("### Eficiencia y Ataque")
    st.caption("Evaluación del comportamiento ofensivo del Cibao FC...")

    # ===========================
    # LAYOUT 2 × 2 + 1 FINAL
    # ===========================

    col1, col2 = st.columns(2)
    with col1:
        plot_group("Producción ofensiva directa", grupos["Producción ofensiva directa"], opponent=opponent_choice)
    with col2:
        plot_group("Eficiencia en el tiro", grupos["Eficiencia en el tiro"], opponent=opponent_choice)

    col3, col4 = st.columns(2)
    with col3:
        plot_group("Patrones de ataque", grupos["Patrones de ataque"], opponent=opponent_choice)
    with col4:
        plot_group("Balón parado y definición", grupos["Balón parado y definición"], opponent=opponent_choice)

    # Último grupo → ancho completo
    plot_group("Juego interior y profundidad", grupos["Juego interior y profundidad"], opponent=opponent_choice)


# ================= TABS VACÍAS POR AHORA =====================

with tab2:

    # ============================================================
    # 🔶 CONSTRUCCIÓN Y PASES — BLOQUE COMPLETO
    # ============================================================

    st.markdown("""
    <h2 style='color:#ff8c00; text-align:center; margin-top:20px;'>Construcción y Pases</h2>
    <p style='text-align:center; color:#ccc;'>
    Evaluación de la estructura asociativa del Cibao FC: precisión, progresión, control de ritmo, distribución y mecanismos de reinicio del juego.
    </p>
    """, unsafe_allow_html=True)

    # ===========================
    # DEFINICIÓN DE GRUPOS
    # ===========================

    grupos_pases = {

        "Control y estabilidad en la circulación": {
            "Posesión (%)": "possession_percent",
            "Precisión de pase (%)": "passes_accurate_percent",
            "Precisión pases largos (%)": "long_pass_percent",
        },

        "Seguridad en la progresión": {
            "Precisión pases progresivos (%)": "progressive_passes_accurate_percent",
            "Precisión pases hacia atrás (%)": "back_passes_accurate_percent",
            "Precisión pases laterales (%)": "lateral_passes_accurate_percent",
        },

        "Conexiones de alto valor táctico": {
            "Precisión pases al último tercio (%)": "passes_to_final_third_accurate_percent",
            "Precisión pases inteligentes (%)": "smart_passes_accurate_percent",
        },

        "Reinicios del juego": {
            "Saques de banda por 90": "throw_ins",
            "Saques de meta por 90": "goal_kicks",
        },

        "Longitud media de pase": {
            "Longitud media de pase": "average_pass_length",
        }
    }


    # ===========================
    # FUNCIÓN: BARRAS VERTICALES
    # ===========================

    def plot_group_vertical(nombre_grupo, mapping):

        df_plot = df_filtrado.copy()

        columnas = [v for v in mapping.values() if v in df_plot.columns]
        etiquetas = {v: k for k, v in mapping.items() if v in df_plot.columns}

        if len(columnas) == 0:
            st.warning(f"No hay métricas disponibles para: {nombre_grupo}")
            return

        df_mean = (
            df_plot[columnas]
            .mean()
            .reset_index()
            .rename(columns={"index": "metric", 0: "valor"})
        )

        df_mean["label"] = df_mean["metric"].map(etiquetas)
        df_mean = df_mean.sort_values("valor", ascending=False)

        fig = px.bar(
            df_mean,
            x="label",
            y="valor",
            orientation="v",
            text_auto=".2f",
            color_discrete_sequence=["#FF8C00"],
        )

        fig.update_layout(
            height=360,
            template="plotly_dark",
            plot_bgcolor="#111",
            paper_bgcolor="#111",
            font=dict(color="#D3D3D3", size=12),
            title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color="#FF8C00")),
            title_x=0.5,
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False,
            xaxis=dict(tickangle=-35),
        )

        st.plotly_chart(fig, use_container_width=True)

        # -------- CONCLUSIONES TÁCTICAS --------
        max_row = df_mean.iloc[0]
        min_row = df_mean.iloc[-1]

        conclusion = f"""
        <div style='background:#111; padding:12px; border-left:3px solid #FF8C00; margin-top:-8px; margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>

        • <b>Fortaleza estructural:</b> El equipo muestra mayor fiabilidad en <b>{max_row['label']}</b>, indicador de estabilidad en la fase de construcción.<br><br>

        • <b>Área por optimizar:</b> La métrica con menor incidencia es <b>{min_row['label']}</b>, aspecto donde aumentar la claridad puede mejorar la fluidez asociativa.<br><br>
        </div>
        """

        st.markdown(conclusion, unsafe_allow_html=True)


    # ===========================
    # FUNCIÓN: GAUGE LINEAL (GRUPO 5)
    # ===========================

    def plot_longitud_pase(mapping):

        col = list(mapping.values())[0]
        label = list(mapping.keys())[0]

        if col not in df_filtrado.columns:
            st.warning("No hay datos para Longitud media de pase.")
            return

        value = df_filtrado[col].mean()

        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': f"<b>{label}</b>", 'font': {'color': '#FF8C00', 'size': 18}},
            gauge={
                'axis': {'range': [0, max(40, value * 1.5)]},
                'bar': {'color': "#FF8C00"},
                'bgcolor': "#333",
                'borderwidth': 1,
                'bordercolor': "#555",
            },
        ))

        fig.update_layout(
            height=220,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor="#111",
            font=dict(color="#D3D3D3")
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div style='background:#111; padding:12px; border-left:3px solid #FF8C00; margin-top:-5px; margin-bottom:25px;'>
        <b>Conclusión táctica</b><br><br>
        • La <b>longitud media de pase ({value:.2f} m)</b> describe el perfil del equipo en cuanto a riesgo y distancia de circulación. 
          Este valor sirve como referencia para calibrar la intención de progresar por combinación o por envío largo.
        </div>
        """, unsafe_allow_html=True)



    # ===========================
    # LAYOUT 2×2 + 1 FINAL
    # ===========================

    col1, col2 = st.columns(2)
    with col1:
        plot_group_vertical("Control y estabilidad en la circulación", grupos_pases["Control y estabilidad en la circulación"])
    with col2:
        plot_group_vertical("Seguridad en la progresión", grupos_pases["Seguridad en la progresión"])

    col3, col4 = st.columns(2)
    with col3:
        plot_group_vertical("Conexiones de alto valor táctico", grupos_pases["Conexiones de alto valor táctico"])
    with col4:
        plot_group_vertical("Reinicios del juego", grupos_pases["Reinicios del juego"])

    # Gráfico final → gauge lineal
    plot_longitud_pase(grupos_pases["Longitud media de pase"])

with tab3:

    # ============================================================
    # 🔶 DEFENSA Y EFICIENCIA — BLOQUE COMPLETO
    # ============================================================

    st.markdown("""
    <h2 style='color:#ff8c00; text-align:center; margin-top:20px;'>Defensa y Eficiencia</h2>
    <p style='text-align:center; color:#ccc;'>
    Análisis del comportamiento defensivo del Cibao FC: disputas, duelos, acciones de contención, volumen de llegadas rivales y
    eficacia defensiva global.
    </p>
    """, unsafe_allow_html=True)

    # ===========================
    # DEFINICIÓN DE GRUPOS
    # ===========================

    grupos_def = {

        "Dominio en los duelos (ofensivos y generales)": {
            "Duelos ofensivos ganados (%)": "offensive_duels_won_percent",
            "Duelos ganados (%)": "duels_won_percent",
        },

        "Solidez defensiva en disputas": {
            "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
            "Duelos aéreos ganados (%)": "aerial_duels_won_percent",
            "Éxito en entradas (%)": "sliding_tackles_successful_percent",
        },

        "Acciones defensivas por 90'": {
            "Intercepciones por 90": "interceptions",
            "Despejes por 90": "clearances",
            "Pérdidas de balón por 90": "losses",
        },

        "Volumen y calidad de llegadas rivales": {
            "Disparos en contra por 90": "shots_against",
            "Disparos en contra a puerta": "shots_again_target",
            "Eficiencia rival (tiros a puerta %)": "shots_against_on_target_percent",
        },

        "Distancia media de disparo": {
            "Distancia media de disparo": "average_shot_distance",
        }
    }

    # ===========================
    # PALETA
    # ===========================

    CIBAO_ORANGE = "#FF8C00"
    CIBAO_BLACK = "#111"
    CIBAO_GRAY = "#D3D3D3"

    # ============================================================
    # 🔶 FUNCIONES DE GRÁFICO
    # ============================================================

    # --- BARRAS HORIZONTALES ---
    def plot_horizontal(nombre, mapping):

        dfp = df_filtrado.copy()
        cols = [v for v in mapping.values() if v in dfp.columns]
        labels = {v: k for k, v in mapping.items() if v in dfp.columns}

        if not cols:
            st.warning(f"No hay datos para {nombre}")
            return

        df_mean = dfp[cols].mean().reset_index()
        df_mean.columns = ["metric", "valor"]
        df_mean["label"] = df_mean["metric"].map(labels)
        df_mean = df_mean.sort_values("valor", ascending=True)

        fig = px.bar(
            df_mean,
            x="valor",
            y="label",
            orientation="h",
            text_auto=".2f",
            color_discrete_sequence=[CIBAO_ORANGE],
        )

        fig.update_layout(
            height=320,
            template="plotly_dark",
            plot_bgcolor=CIBAO_BLACK,
            paper_bgcolor=CIBAO_BLACK,
            title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            margin=dict(l=30, r=20, t=50, b=20),
            font=dict(color=CIBAO_GRAY),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        max_row = df_mean.iloc[-1]
        min_row = df_mean.iloc[0]

        st.markdown(f"""
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};
                    margin-top:-8px;margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>
        • <b>Comportamiento destacado:</b> Mayor solvencia en <b>{max_row['label']}</b>.<br><br>
        • <b>Aspecto mejorable:</b> Valor más bajo en <b>{min_row['label']}</b>.
        </div>
        """, unsafe_allow_html=True)

    # --- BARRAS VERTICALES ---
    def plot_vertical(nombre, mapping):

        dfp = df_filtrado.copy()
        cols = [v for v in mapping.values() if v in dfp.columns]
        labels = {v: k for k, v in mapping.items() if v in dfp.columns}

        if not cols:
            st.warning(f"No hay datos para {nombre}")
            return

        df_mean = dfp[cols].mean().reset_index()
        df_mean.columns = ["metric", "valor"]
        df_mean["label"] = df_mean["metric"].map(labels)
        df_mean = df_mean.sort_values("valor", ascending=False)

        fig = px.bar(
            df_mean,
            x="label",
            y="valor",
            text_auto=".2f",
            color_discrete_sequence=[CIBAO_ORANGE],
        )

        fig.update_layout(
            height=360,
            template="plotly_dark",
            plot_bgcolor=CIBAO_BLACK,
            paper_bgcolor=CIBAO_BLACK,
            title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(color=CIBAO_GRAY),
            xaxis=dict(tickangle=-30),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        max_row = df_mean.iloc[0]
        min_row = df_mean.iloc[-1]

        st.markdown(f"""
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};
                    margin-top:-8px;margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>
        • <b>Mayor influencia:</b> <b>{max_row['label']}</b>.<br><br>
        • <b>Zona con margen de mejora:</b> <b>{min_row['label']}</b>.
        </div>
        """, unsafe_allow_html=True)

    # --- GAUGE LINEAL (UNIFICADO) ---
    def plot_gauge(mapping):

        col = list(mapping.values())[0]
        label = list(mapping.keys())[0]

        if col not in df_filtrado.columns:
            st.warning("No hay datos disponibles.")
            return

        value = df_filtrado[col].mean()

        max_rango = max(40, value * 1.8)  # rango uniforme

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': f"<b>{label}</b>", 'font': {'color': CIBAO_ORANGE, 'size': 18}},
            gauge={
                'axis': {'range': [0, max_rango]},
                'bar': {'color': CIBAO_ORANGE},
                'bgcolor': "#333",
                'borderwidth': 1,
                'bordercolor': "#555",
            }
        ))

        fig.update_layout(
            paper_bgcolor=CIBAO_BLACK,
            plot_bgcolor=CIBAO_BLACK,
            height=260,  # unificado
            margin=dict(l=20, r=20, t=60, b=20),
            font=dict(color=CIBAO_GRAY)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};
                    margin-top:-5px;margin-bottom:25px;'>
        <b>Conclusión táctica</b><br><br>
        • La <b>distancia media de disparo ({value:.1f} m)</b> indica la capacidad del equipo para limitar
          la calidad de las ocasiones rivales.
        </div>
        """, unsafe_allow_html=True)

    # ===========================
    # LAYOUT 2 × 2 + 1
    # ===========================

    col1, col2 = st.columns(2)
    with col1:
        plot_horizontal("Dominio en los duelos (ofensivos y generales)", grupos_def["Dominio en los duelos (ofensivos y generales)"])
    with col2:
        plot_horizontal("Solidez defensiva en disputas", grupos_def["Solidez defensiva en disputas"])

    col3, col4 = st.columns(2)
    with col3:
        plot_vertical("Acciones defensivas por 90'", grupos_def["Acciones defensivas por 90'"])
    with col4:
        plot_vertical("Volumen y calidad de llegadas rivales", grupos_def["Volumen y calidad de llegadas rivales"])

    # Gauge final
    plot_gauge(grupos_def["Distancia media de disparo"])

with tab4:

    # ============================================================
    # 🔶 DISTRIBUCIÓN TÁCTICA — BLOQUE COMPLETO
    # ============================================================

    st.markdown("""
    <h2 style='color:#ff8c00; text-align:center; margin-top:20px;'>Distribución Táctica</h2>
    <p style='text-align:center; color:#ccc;'>
    Análisis del comportamiento defensivo del Cibao FC según alturas de recuperación y zonas de presión.
    </p>
    """, unsafe_allow_html=True)

    # ===========================
    # DEFINICIÓN DE GRUPOS
    # ===========================

    grupos_tacticos = {
        "Mapa de Recuperaciones por Altura": {
            "Recuperaciones altas por 90": "recoveries_high",
            "Recuperaciones medias por 90": "recoveries_medium",
            "Recuperaciones bajas por 90": "recoveries_low",
        },

        "Mapa de Presión por Altura": {
            "Presión alta (estimada)": "losses_high",
            "Presión media (estimada)": "losses_medium",
            "Presión baja (estimada)": "losses_low",
        }
    }

    # ===========================
    # PALETA (COLORES FIJOS)
    # ===========================

    CIBAO_ORANGE = "#FF8C00"
    CIBAO_GRAY = "#D3D3D3"

    HEATMAP_COLORSCALE = [
        [0.0, "#2a2a2a"],   # bajo — gris oscuro
        [0.5, "#ff7b00"],   # medio — naranja fuerte
        [1.0, "#ffae42"]    # alto — naranja claro
    ]

    import numpy as np
    import plotly.graph_objects as go

    # ===========================
    # FUNCIÓN DEL HEATMAP (COLORES FIJOS POR RANKING)
    # ===========================

    def plot_heatmap(nombre_grupo, mapping):

        dfp = df_filtrado.copy()

        cols = [v for v in mapping.values() if v in dfp.columns]
        labels = [k for k, v in mapping.items() if v in dfp.columns]

        if len(cols) == 0:
            st.warning(f"No hay datos disponibles para: {nombre_grupo}")
            return

        # --- Datos reales
        series_real = dfp[cols].mean().fillna(0)

        # --- Ranking → convierte valores a 0,1,2 (bajo–medio–alto)
        rank = series_real.rank(method="dense") - 1
        rank = rank.astype(int)

        # Convertimos ranking a matriz 1×N
        z_vals = rank.to_numpy().reshape(1, -1)

        # --- HEATMAP
        fig = go.Figure(
            data=go.Heatmap(
                z=z_vals,
                x=labels,
                y=[""],
                colorscale=HEATMAP_COLORSCALE,
                showscale=True,
                colorbar=dict(
                    thickness=10,
                    tickvals=[0, 1, 2],
                    ticktext=["Bajo", "Medio", "Alto"],
                    bgcolor="#111",
                    tickfont=dict(color=CIBAO_GRAY)
                )
            )
        )

        # --- Texto dentro de las celdas (valores reales)
        annotations = []
        for j, label in enumerate(labels):
            annotations.append(
                dict(
                    x=label,
                    y="",
                    text=f"{series_real.iloc[j]:.2f}",
                    font=dict(color="white", size=13),
                    showarrow=False
                )
            )

        fig.update_layout(
            annotations=annotations,
            height=280,
            template="plotly_dark",
            title=dict(
                text=f"<b>{nombre_grupo}</b>",
                font=dict(size=18, color=CIBAO_ORANGE)
            ),
            title_x=0.5,
            paper_bgcolor="#111",
            plot_bgcolor="#111",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- CONCLUSIONES TÁCTICAS ---
        max_m = series_real.idxmax()
        min_m = series_real.idxmin()

        c1 = [k for k, v in mapping.items() if v == max_m][0]
        c2 = [k for k, v in mapping.items() if v == min_m][0]

        st.markdown(f"""
        <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                    margin-top:-8px; margin-bottom:25px; border-radius:6px;'>

        <b>Conclusiones tácticas</b><br><br>

        • <b>Zona de mayor incidencia:</b> mayor actividad en <b>{c1}</b>.<br><br>

        • <b>Zona con menor actividad:</b> menor intervención en <b>{c2}</b>.<br><br>

        </div>
        """, unsafe_allow_html=True)


    # ===========================
    # LAYOUT — 2 HEATMAPS
    # ===========================

    col1, col2 = st.columns(2)

    with col1:
        plot_heatmap("Mapa de Recuperaciones por Altura", grupos_tacticos["Mapa de Recuperaciones por Altura"])

    with col2:
        plot_heatmap("Mapa de Presión por Altura", grupos_tacticos["Mapa de Presión por Altura"])

with tab5:

    # ============================================================
    # 🔶 ANÁLISIS COMPARATIVO — BLOQUE COMPLETO
    # ============================================================

    st.markdown("""
    <h2 style='color:#ff8c00; text-align:center; margin-top:20px;'>Análisis Comparativo (Tablas)</h2>
    <p style='text-align:center; color:#ccc;'>
        Comparación de métricas clave del Cibao FC por fase del juego: ofensiva, construcción/pase y defensa.
        Los valores más altos se resaltan mediante un gradiente en tonos naranja institucional.
    </p>
    """, unsafe_allow_html=True)

    # ============================================================
    # 📋 DICCIONARIO DE MÉTRICAS (AMPLIADO)
    # ============================================================

    metrics_blocks = {

        "Ofensivas": {
            "Goles por partido": "goals",
            "xG (Goles esperados)": "xg",
            "Disparos por 90": "shots",
            "Disparos a puerta por 90": "shots_on_target",
            "xG por disparo": "xg_per_shot",
            "Conversión de disparos (%)": "shot_conversion_percent",
            "Acciones de ataque por 90": "attacking_actions",
            "Acciones exitosas (%)": "successful_attacking_actions_percent",
            "Contraataques por 90": "counter_attacks",
            "Centros por 90": "crosses",
            "Precisión de centros (%)": "crosses_accurate_percent",
            "Pases clave por 90": "key_passes",
            "Asistencias esperadas (xA)": "xa",
            "Corners por 90": "corners",
        },

        "Construcción y Pase": {
            "Posesión (%)": "possession_percent",
            "Pases por 90": "passes",
            "Precisión de pase (%)": "passes_accurate_percent",
            "Precisión hacia adelante (%)": "forward_passes_accurate_percent",
            "Precisión hacia atrás (%)": "back_passes_accurate_percent",
            "Precisión lateral (%)": "lateral_passes_accurate_percent",
            "Pases progresivos por 90": "progressive_passes",
            "Precisión pases progresivos (%)": "progressive_passes_accurate_percent",
            "Precisión último tercio (%)": "passes_to_final_third_accurate_percent",
            "Precisión pases largos (%)": "long_passes_accurate_percent",
            "Precisión pases inteligentes (%)": "smart_passes_accurate_percent",
            "Pases al área por 90": "passes_to_penalty_area",
            "Longitud media de pase": "average_pass_length",
        },

        "Defensivas": {
            "Intercepciones por 90": "interceptions",
            "Despejes por 90": "clearances",
            "Entradas por 90": "sliding_tackles",
            "Éxito en entradas (%)": "sliding_tackles_successful_percent",
            "Duelos ganados (%)": "duels_won_percent",
            "Duelos ofensivos ganados (%)": "offensive_duels_won_percent",
            "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
            "Duelos aéreos ganados (%)": "aerial_duels_won_percent",
            "Pérdidas por 90": "losses",
            "Disparos en contra por 90": "shots_against",
            "Disparos en contra a puerta": "shots_against_on_target",
            "Eficiencia rival (%)": "shots_against_on_target_percent",
            "PPDA": "ppda",
        },
    }

    # ============================================================
    # 🎨 PALETA CIBAO — GRADIENTE VIVO
    # ============================================================

    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib
    import pandas as pd
    import io

    CIBAO_ORANGE_CMAP = LinearSegmentedColormap.from_list(
        "cibao_orange",
        ["#ff6600", "#ff7b00", "#ff9933", "#ffb84d", "#ffd699"]
    )

    matplotlib.colormaps.register(
        CIBAO_ORANGE_CMAP,
        name="cibao_orange",
        force=True
    )

    # ============================================================
    # 🔍 PREPARAR DATOS BASE
    # ============================================================

    df_base = df_filtrado.copy()

    if df_base.empty:
        st.info("No hay datos disponibles para los filtros seleccionados.")
    else:
        df_base = df_base.sort_values("Date", ascending=False)

        partidos_disponibles = df_base["Match"].nunique()
        df_base = df_base.head(min(partidos_disponibles, 5))

        st.caption(
            f"Mostrando los últimos {len(df_base)} partidos disponibles (máximo 5)."
        )

        # ============================================================
        # ⚙️ FUNCIÓN PARA GENERAR TABLA FORMATEADA
        # ============================================================

        def build_table(df, metrics_dict, title):

            # solo columnas que EXISTEN en df
            columnas_existentes = [c for c in metrics_dict.values() if c in df.columns]

            if len(columnas_existentes) == 0:
                st.warning(f"No hay datos disponibles para {title}.")
                return df.iloc[:0]

            df_local = df[["Match"] + columnas_existentes].copy()

            # renombrar
            label_map = {v: k for k, v in metrics_dict.items() if v in columnas_existentes}
            df_local = df_local.rename(columns=label_map)

            # redondeo REAL a 2 decimales solo en numéricas
            numeric_cols = df_local.select_dtypes(include=["number"]).columns
            df_local[numeric_cols] = df_local[numeric_cols].round(2)

            st.markdown(
                f"### <span style='color:#ff8c00;'>⬤ {title}</span>",
                unsafe_allow_html=True
            )

            styled = (
                df_local.style
                .background_gradient(cmap="cibao_orange", subset=numeric_cols)
                .set_properties(
                    **{
                        "text-align": "center",
                        "font-size": "12px",
                        "border-color": "#333",
                    }
                )
                .format("{:.2f}", subset=numeric_cols)
            )

            height = max(220, len(df_local) * 45 + 80)

            st.dataframe(styled, use_container_width=True, height=height)

            return df_local

        # ============================================================
        # 📊 BLOQUES
        # ============================================================

        st.divider()
        df_off = build_table(df_base, metrics_blocks["Ofensivas"], "Bloque Ofensivo")

        st.divider()
        df_pass = build_table(df_base, metrics_blocks["Construcción y Pase"], "Bloque Construcción y Pase")

        st.divider()
        df_def = build_table(df_base, metrics_blocks["Defensivas"], "Bloque Defensivo")

        # ============================================================
        # 📥 DESCARGA EN EXCEL
        # ============================================================

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_off.to_excel(writer, sheet_name="Ofensivo", index=False)
            df_pass.to_excel(writer, sheet_name="Construccion_Pase", index=False)
            df_def.to_excel(writer, sheet_name="Defensivo", index=False)

        buffer.seek(0)

        st.download_button(
            label="📥 Descargar análisis completo en Excel",
            data=buffer,
            file_name="analisis_comparativo_cibao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # ============================================================
        # 📌 INSIGHT FINAL
        # ============================================================

        st.markdown("""
        <div style='background:#111; padding:12px; border-left:3px solid #ff8c00; margin-top:20px;'>
            <b>Resumen general:</b><br><br>
            Las tablas comparativas permiten identificar de forma rápida qué bloques del modelo
            (ofensivo, construcción y defensivo) están sosteniendo el rendimiento del equipo
            y en cuáles existe margen para ajustar comportamientos.
        </div>
        """, unsafe_allow_html=True)
        
        # ===========================================
# EXPORTACIÓN A PDF (fpdf2 + kaleido, sin HTML)
# ===========================================
import tempfile
import requests
from fpdf import FPDF
from datetime import datetime

# Valor del checkbox (fallback a True)
mostrar_promedio_liga = st.session_state.get("mostrar_promedio_liga", True)

# ---------- Logo helper ----------
def descargar_logo():
    url = "https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(r.content)
            tmp.close()
            return tmp.name
    except Exception:
        pass
    return None

# ---------- Captura plotly -> PNG bytes ----------
def plotly_to_png(fig, width=1600, height=900, scale=2):
    try:
        return pio.to_image(fig, format="png", width=width, height=height, scale=scale)
    except Exception as e:
        st.warning(f"No se pudo capturar un gráfico: {e}")
        return None

# ---------- Conclusiones automáticas ----------
def generar_conclusiones(df_cibao, df_liga):
    metricas = {
        "xg": "Goles Esperados (xG)",
        "possession_percent": "Posesión (%)",
        "passes_accurate_percent": "Precisión de Pase (%)",
        "shots_on_target_percent": "Disparos a Puerta (%)",
        "duels_won_percent": "Duelos Ganados (%)",
        "interceptions": "Intercepciones p90",
    }
    fort, deb = [], []
    if df_liga.empty:
        return {"fortalezas": fort, "debilidades": deb}
    liga_sin = df_liga[df_liga["Team"].str.lower() != "cibao"].copy()
    for col, nombre in metricas.items():
        if col not in df_cibao.columns or col not in liga_sin.columns:
            continue
        v_c = pd.to_numeric(df_cibao[col], errors="coerce").mean()
        v_l = pd.to_numeric(liga_sin[col], errors="coerce").mean()
        if pd.isna(v_c) or pd.isna(v_l) or v_l == 0:
            continue
        dif = (v_c - v_l) / v_l * 100
        item = {"metrica": nombre, "cibao": v_c, "liga": v_l, "dif": dif}
        if dif >= 10:
            fort.append(item)
        elif dif <= -10:
            deb.append(item)
    fort = sorted(fort, key=lambda x: x["dif"], reverse=True)[:3]
    deb = sorted(deb, key=lambda x: x["dif"])[:3]
    return {"fortalezas": fort, "debilidades": deb}

# ---------- Funciones para recrear gráficos ----------
def grafico_barras_pdf(nombre, mapping, df_filtrado, df_liga, mostrar_promedio, orient="h"):
    cols = [v for v in mapping.values() if v in df_filtrado.columns]
    if not cols:
        return None
    etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    data = []
    means_c = df_filtrado[cols].mean()
    for c in cols:
        data.append({"label": etiquetas[c], "Equipo": "Cibao FC", "valor": means_c[c]})
    if mostrar_promedio and not df_liga.empty:
        liga_sin = df_liga[df_liga["Team"].str.lower() != "cibao"].copy()
        for c in cols:
            if c in liga_sin.columns:
                v = pd.to_numeric(liga_sin[c], errors="coerce").mean()
                data.append({"label": etiquetas[c], "Equipo": "Promedio Liga", "valor": v if not pd.isna(v) else 0})
    dfp = pd.DataFrame(data)
    color_map = {"Cibao FC": "#FF8C00", "Promedio Liga": "#FFC966"}
    if orient == "h":
        fig = px.bar(dfp, x="valor", y="label", color="Equipo", orientation="h",
                     text_auto=".2f", color_discrete_map=color_map, barmode="group",
                     title=nombre)
    else:
        fig = px.bar(dfp, x="label", y="valor", color="Equipo",
                     text_auto=".2f", color_discrete_map=color_map, barmode="group",
                     title=nombre)
    fig.update_layout(template="plotly_dark", plot_bgcolor="#111", paper_bgcolor="#111",
                      font=dict(color="#D3D3D3", size=14),
                      title=dict(font=dict(size=20, color="#FF8C00")))
    return fig

def gauge_pdf(mapping, df_filtrado, df_liga, mostrar_promedio):
    col = list(mapping.values())[0]
    label = list(mapping.keys())[0]
    if col not in df_filtrado.columns:
        return None
    v_c = df_filtrado[col].mean()
    v_l = None
    if mostrar_promedio and not df_liga.empty and col in df_liga.columns:
        liga_sin = df_liga[df_liga["Team"].str.lower() != "cibao"].copy()
        v_l = pd.to_numeric(liga_sin[col], errors="coerce").mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=v_c,
        title={'text': f"<b>{label}</b>", 'font': {'color': '#FF8C00', 'size': 20}},
        number={'font': {'color': '#FF8C00', 'size': 42}},
        gauge={
            'axis': {'range': [0, max(1, v_c * 1.5, 40)]},
            'bar': {'color': "#FF8C00"},
            'bgcolor': "#333",
            'threshold': {
                'line': {'color': "#FFC966", 'width': 3},
                'thickness': 0.8,
                'value': v_l if v_l and not pd.isna(v_l) else 0
            } if v_l and not pd.isna(v_l) else None
        },
    ))
    fig.update_layout(paper_bgcolor="#111", font=dict(color="#D3D3D3"))
    return fig

def heatmap_pdf(nombre, mapping, df_filtrado):
    cols = [v for v in mapping.values() if v in df_filtrado.columns]
    labels = [k for k, v in mapping.items() if v in df_filtrado.columns]
    if not cols:
        return None
    serie = df_filtrado[cols].mean().fillna(0)
    rank = serie.rank(method="dense") - 1
    z = rank.astype(int).to_numpy().reshape(1, -1)
    colorscale = [
        [0.0, "#2a2a2a"],
        [0.5, "#ff7b00"],
        [1.0, "#ffae42"]
    ]
    fig = go.Figure(go.Heatmap(z=z, x=labels, y=[""], colorscale=colorscale, showscale=True,
                               colorbar=dict(tickvals=[0,1,2], ticktext=["Bajo","Medio","Alto"])))
    ann = []
    for j, lbl in enumerate(labels):
        ann.append(dict(x=lbl, y="", text=f"{serie.iloc[j]:.2f}", font=dict(color="white", size=14), showarrow=False))
    fig.update_layout(annotations=ann, template="plotly_dark",
                      title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color="#FF8C00")),
                      paper_bgcolor="#111", plot_bgcolor="#111")
    return fig

# ---------- PDF principal ----------
def generar_pdf(df_filtrado, df_liga_mayor, partidos_sel, fig_comp, figs_tabs):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    # Portada
    pdf.add_page()
    pdf.set_fill_color(17,17,17); pdf.rect(0,0,297,210,"F")
    logo = descargar_logo()
    if logo:
        try: pdf.image(logo, x=115, y=25, w=60)
        except: pass
    pdf.set_y(95); pdf.set_font("Helvetica","B",28); pdf.set_text_color(255,140,0)
    pdf.cell(0,12,"REPORTE DE RENDIMIENTO COLECTIVO",0,1,"C")
    pdf.set_font("Helvetica","B",16); pdf.set_text_color(220,220,220)
    pdf.cell(0,9,"Liga Dominicana - Temporada 2024/2025",0,1,"C"); pdf.ln(6)
    pdf.set_font("Helvetica","",12); pdf.set_text_color(190,190,190)
    fecha = datetime.now().strftime("%d/%m/%Y - %H:%M")
    pdf.cell(0,7,f"Fecha de generacion: {fecha}",0,1,"C")
    if partidos_sel:
        txt = ", ".join(partidos_sel[:3]) + ("..." if len(partidos_sel)>3 else "")
        pdf.cell(0,7,f"Partidos analizados: {txt}",0,1,"C")
    pdf.set_y(165); pdf.set_draw_color(255,140,0); pdf.set_line_width(1); pdf.line(50,165,247,165)
    pdf.set_y(178); pdf.set_font("Helvetica","I",10); pdf.set_text_color(160,160,160)
    pdf.cell(0,6,"Analisis tactico y estadistico avanzado",0,1,"C")
    pdf.cell(0,6,"Departamento de Analisis - Cibao FC",0,1,"C")

    # Resumen ejecutivo
    pdf.add_page()
    pdf.set_font("Helvetica","B",18); pdf.set_text_color(255,140,0)
    pdf.cell(0,10,"RESUMEN EJECUTIVO",0,1,"C"); pdf.ln(4)
    concl = generar_conclusiones(df_filtrado, df_liga_mayor)
    pdf.set_font("Helvetica","B",14); pdf.set_text_color(100,220,100)
    pdf.cell(0,9,"FORTALEZAS PRINCIPALES",0,1,"L"); pdf.ln(2)
    pdf.set_font("Helvetica","",11); pdf.set_text_color(220,220,220)
    if concl["fortalezas"]:
        for it in concl["fortalezas"]:
            pdf.set_x(12); pdf.set_text_color(255,140,0); pdf.cell(5,7,chr(149),0,0,"L")
            pdf.set_text_color(220,220,220)
            pdf.cell(0,7,f"{it['metrica']}: Cibao {it['cibao']:.2f} vs Liga {it['liga']:.2f} (+{it['dif']:.1f}%)",0,1,"L")
    else:
        pdf.set_x(12); pdf.cell(0,7,"Rendimiento equilibrado respecto al promedio de liga",0,1,"L")
    pdf.ln(6)
    pdf.set_font("Helvetica","B",14); pdf.set_text_color(255,120,120)
    pdf.cell(0,9,"AREAS DE MEJORA",0,1,"L"); pdf.ln(2)
    pdf.set_font("Helvetica","",11); pdf.set_text_color(220,220,220)
    if concl["debilidades"]:
        for it in concl["debilidades"]:
            pdf.set_x(12); pdf.set_text_color(255,140,0); pdf.cell(5,7,chr(149),0,0,"L")
            pdf.set_text_color(220,220,220)
            pdf.cell(0,7,f"{it['metrica']}: Cibao {it['cibao']:.2f} vs Liga {it['liga']:.2f} ({it['dif']:.1f}%)",0,1,"L")
    else:
        pdf.set_x(12); pdf.cell(0,7,"No se identificaron areas significativas de mejora",0,1,"L")
    pdf.set_draw_color(255,140,0); pdf.set_line_width(0.4); pdf.rect(10,28,277,150)

    # Comparativa
    if fig_comp:
        pdf.add_page()
        pdf.set_font("Helvetica","B",16); pdf.set_text_color(255,140,0)
        pdf.cell(0,10,"COMPARATIVA: CIBAO FC VS RIVAL",0,1,"C"); pdf.ln(3)
        img = plotly_to_png(fig_comp, width=2000, height=1200)
        if img:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); tmp.write(img); tmp.close()
            try: pdf.image(tmp.name, x=15, y=38, w=265)
            except: pass

    # Secciones
    secciones = [
        ("EFICIENCIA Y ATAQUE", "eficiencia_ataque"),
        ("CONSTRUCCION Y PASES", "construccion_pases"),
        ("DEFENSA Y EFICIENCIA", "defensa"),
        ("DISTRIBUCION TACTICA", "tactica"),
    ]
    for titulo, key in secciones:
        figs = figs_tabs.get(key, [])
        if not figs:
            continue
        pdf.add_page()
        pdf.set_font("Helvetica","B",18); pdf.set_text_color(255,140,0)
        pdf.cell(0,10,titulo,0,1,"C"); pdf.ln(2)
        y = 35; per_page = 2; count = 0
        for fig in figs:
            if count > 0 and count % per_page == 0:
                pdf.add_page()
                pdf.set_font("Helvetica","B",14); pdf.set_text_color(255,140,0)
                pdf.cell(0,8,f"{titulo} (continuacion)",0,1,"C"); pdf.ln(2)
                y = 35
            img = plotly_to_png(fig, width=2000, height=1100)
            if img:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); tmp.write(img); tmp.close()
                try: pdf.image(tmp.name, x=15, y=y, w=265, h=80); y += 90
                except: pass
            else:
                pdf.set_y(y); pdf.set_font("Helvetica","I",10); pdf.set_text_color(180,180,180)
                pdf.cell(0,8,"[Grafico no disponible]",0,1,"C"); y += 20
            count += 1

    # Final
    pdf.add_page()
    pdf.set_y(90); pdf.set_font("Helvetica","B",22); pdf.set_text_color(255,140,0)
    pdf.cell(0,12,"CIBAO FC",0,1,"C")
    pdf.set_font("Helvetica","I",11); pdf.set_text_color(180,180,180)
    pdf.cell(0,7,"Departamento de Analisis y Rendimiento",0,1,"C")
    pdf.cell(0,7,"www.cibaofc.com",0,1,"C")

    return pdf.output(dest="S").encode("latin-1")

# ---------- UI ----------
st.markdown("<hr style='margin:40px 0; border-color:#ff8c00;'>", unsafe_allow_html=True)
st.markdown("""
<h2 style='color:#ff8c00; text-align:center; margin-top:12px;'>
    📄 Exportar Reporte Completo en PDF
</h2>
<p style='text-align:center; color:#ccc; font-size:15px;'>
    Reporte profesional con todas las métricas, gráficos y conclusiones.
</p>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Valores seguros para el PDF
mostrar_promedio_liga = st.session_state.get("mostrar_promedio_liga", True)
partidos_seleccionados = st.session_state.get(
    "sidebar_partidos_combinados",
    st.session_state.get("global_partidos", [])
)

c1, c2, c3 = st.columns([1,1,1])
with c2:
    if st.button("🚀 GENERAR REPORTE PDF", use_container_width=True, type="primary"):
        with st.spinner("Generando reporte... puede tardar 30-60 segundos ⏳"):
            try:
                # Comparativa (si hay rival)
                fig_comp_pdf = None
                if not df_liga_mayor.empty and 'opponent_choice' in locals():
                    try:
                        fig_comp_pdf, _, _ = make_team_scatter(
                            df_liga_mayor,
                            primary_team="Cibao",
                            opponent=opponent_choice,
                            x_metric=METRIC_OPTIONS.get(x_choice),
                            y_metric=METRIC_OPTIONS.get(y_choice),
                            x_label=x_choice,
                            y_label=y_choice,
                            title=f"Liga Mayor — {x_choice} vs {y_choice}",
                            filters={"Competition": lambda s: s.str.contains("Liga", case=False, na=False)},
                        )
                    except Exception as e:
                        st.warning(f"No se pudo recrear la comparativa: {e}")

                figs_dict = {
                    "eficiencia_ataque": [],
                    "construccion_pases": [],
                    "defensa": [],
                    "tactica": [],
                }

                # Tab 1
                for nombre_grupo, mapping in grupos.items():
                    fig = grafico_barras_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga, orient="h")
                    if fig: figs_dict["eficiencia_ataque"].append(fig)

                # Tab 2
                for nombre_grupo, mapping in grupos_pases.items():
                    if nombre_grupo == "Longitud media de pase":
                        fig = gauge_pdf(mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga)
                    else:
                        fig = grafico_barras_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                                                 orient="v")
                    if fig: figs_dict["construccion_pases"].append(fig)

                # Tab 3
                for nombre_grupo, mapping in grupos_def.items():
                    if nombre_grupo == "Distancia media de disparo":
                        fig = gauge_pdf(mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga)
                    else:
                        fig = grafico_barras_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                                                 orient="h")
                    if fig: figs_dict["defensa"].append(fig)

                # Tab 4
                for nombre_grupo, mapping in grupos_tacticos.items():
                    fig = heatmap_pdf(nombre_grupo, mapping, df_filtrado)
                    if fig: figs_dict["tactica"].append(fig)

                pdf_bytes = generar_pdf(df_filtrado, df_liga_mayor, partidos_seleccionados, fig_comp_pdf, figs_dict)
                nombre = f"Cibao_FC_Rendimiento_Colectivo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

                st.success("✅ ¡Reporte generado!")
                st.download_button(
                    label="📥 DESCARGAR PDF",
                    data=pdf_bytes,
                    file_name=nombre,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"❌ Error generando el reporte: {e}")
                st.exception(e)
