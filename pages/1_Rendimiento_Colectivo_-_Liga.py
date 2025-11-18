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
    df_filtrado = df_cibao[df_cibao["Jornada"].isin(ultimas_jornadas)]

# ===============================================
# 🧠 HELPERS AUXILIARES
# ===============================================
def col_from(metric_name: str):
    """Devuelve nombre de columna real según METRICS_DICT si existe en df."""
    if not metric_name:
        return None
    col = METRICS_DICT.get(metric_name)
    return col if (col in df_filtrado.columns) else None

def mean_safe(metric_name: str) -> float:
    """Media robusta; retorna np.nan si no existe o no es numérica."""
    col = col_from(metric_name)
    if col is None:
        return np.nan
    s = pd.to_numeric(df_filtrado[col], errors="coerce")
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

# ===============================================
# Bloque KPIs
# ===============================================

st.markdown("### Indicadores del último partido")

# Seleccionar el último partido según la fecha más reciente
if not df_filtrado.empty:
    ultimo_partido = df_filtrado.sort_values("Date", ascending=False).iloc[0]
else:
    st.warning("No hay datos disponibles para mostrar los KPIs.")
    st.stop()

# Formatear fecha (dd-mm-yyyy)
fecha_str = "-"
if pd.notna(ultimo_partido.get("Date", None)):
    try:
        fecha_str = pd.to_datetime(ultimo_partido["Date"]).strftime("%d-%m-%Y")
    except Exception:
        fecha_str = str(ultimo_partido.get("Date", ""))

# KPIs textuales
kpi_texts = [
    ("Fecha",              fecha_str),
    ("Jornada número",     ultimo_partido.get("Jornada", "")),
    ("Partido",            ultimo_partido.get("Match", "")),
    ("Resultado Final",    ultimo_partido.get("Final Result", "")),
    ("Alineación",         ultimo_partido.get("Alineacion", "")),
]

# KPIs numéricos del último partido
kpi_numericos = [
    ("Goles Esperados (xG)",  ultimo_partido.get("xg", np.nan)),
    ("Posesión (%)",          ultimo_partido.get("possession_percent", np.nan)),
    ("Tarjetas Amarillas",    ultimo_partido.get("yellow_cards", np.nan)),
    ("Tarjetas Rojas",        ultimo_partido.get("red_cards", np.nan)),
]

# Mostrar KPIs textuales
cols_text = st.columns(len(kpi_texts))
for (label, value), c in zip(kpi_texts, cols_text):
    with c:
        display = str(value) if pd.notna(value) else "-"
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

# Mostrar KPIs numéricos (xG, Posesión, Tarjetas)
cols_num = st.columns(len(kpi_numericos))
for (label, val), c in zip(kpi_numericos, cols_num):
    with c:
        if "Tarjetas" in label:
            display = "-" if pd.isna(val) else f"{int(val)}"
        else:
            display = "-" if pd.isna(val) else f"{val:.2f}"
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

# --- Separador visual antes de los KPIs ---
st.markdown("<br>", unsafe_allow_html=True)

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

    else:
        opponent_choice = col_sel1.selectbox("Próximo rival", team_options)

        metric_labels = list(METRIC_OPTIONS.keys())

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

        x_choice = col_sel2.selectbox(
            "Métrica ofensiva (eje X)",
            metric_labels,
            index=x_default if metric_labels else 0,
        )

        y_choice = col_sel3.selectbox(
            "Métrica defensiva (eje Y)",
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
        "Goles por partido": "goals",
        "Goles en contra por partido": "conceded_goals",
        "xG (Goles esperados)": "xg",
    },

    "Eficiencia en el tiro": {
        "Porcentaje de disparos a puerta (%)": "shots_on_target_percent",
        "Disparos desde fuera del área a puerta (%)": "shots_from_outside_penalty_area_on_target_percent",
    },

    "Patrones de ataque": {
        "Ataques posicionales con disparo (%)": "positional_attacks_with_shots_percent",
        "Contraataques con disparo (%)": "counter_attacks_with_shots_percent",
    },

    "Balón parado y definición": {
        "Balones parados con disparo (%)": "set_pieces_with_shots_percent",
        "Corners con disparo (%)": "corners_with_shots_percent",
        "Faltas directas con disparo (%)": "free_kicks_with_shots_percent",
        "Conversión de penaltis (%)": "penalties_converted_percent",
    },

    "Juego interior y profundidad": {
        "Entradas al área por 90": "penalty_area_entries",
        "Entradas al área con conducción": "penalty_area_entries_runs",
        "Entradas al área con centros": "penalty_area_entries_crosses",
        "Toques en el área por 90": "touches_in_penalty_area",
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

def plot_group(nombre_grupo, mapping):

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
    df_mean = df_mean.sort_values("valor", ascending=True)

    fig = px.bar(
        df_mean,
        x="valor",
        y="label",
        orientation="h",
        text_auto=".2f",
        color_discrete_sequence=PALETTE_CIBAO,
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
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------- CONCLUSIONES TÁCTICAS --------
    max_row = df_mean.iloc[-1]
    min_row = df_mean.iloc[0]

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
        plot_group("Producción ofensiva directa", grupos["Producción ofensiva directa"])
    with col2:
        plot_group("Eficiencia en el tiro", grupos["Eficiencia en el tiro"])

    col3, col4 = st.columns(2)
    with col3:
        plot_group("Patrones de ataque", grupos["Patrones de ataque"])
    with col4:
        plot_group("Balón parado y definición", grupos["Balón parado y definición"])

    # Último grupo → ancho completo
    plot_group("Juego interior y profundidad", grupos["Juego interior y profundidad"])


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
            "Disparos en contra a puerta": "shots_against_on_target",
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

        df_mean = (
            dfp[cols].mean()
            .reset_index()
            .rename(columns={"index": "metric", 0: "valor"})
        )

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
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};margin-top:-8px;margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>
        • <b>Comportamiento destacado:</b> El equipo muestra mayor solvencia en <b>{max_row['label']}</b>, 
          lo cual refleja ventaja competitiva en situaciones individuales de disputa.<br><br>

        • <b>Aspecto mejorable:</b> La métrica más baja es <b>{min_row['label']}</b>, señalando un área donde 
          la estructura defensiva puede elevar su consistencia.
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

        df_mean = (
            dfp[cols].mean()
            .reset_index()
            .rename(columns={"index": "metric", 0: "valor"})
        )
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
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};margin-top:-8px;margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>
        • <b>Mayor influencia defensiva:</b> El equipo destaca en <b>{max_row['label']}</b>, 
          comportamiento clave en la protección del área y en la interrupción de avances rivales.<br><br>

        • <b>Zona con margen de mejora:</b> La métrica con menor impacto es <b>{min_row['label']}</b>, 
          elemento donde aumentar la consistencia reforzaría el bloque defensivo.
        </div>
        """, unsafe_allow_html=True)


    # --- GAUGE LINEAL ---
    def plot_gauge(mapping):

        col = list(mapping.values())[0]
        label = list(mapping.keys())[0]

        if col not in df_filtrado.columns:
            st.warning("No hay datos disponibles.")
            return

        value = df_filtrado[col].mean()

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': f"<b>{label}</b>", 'font': {'color': CIBAO_ORANGE, 'size': 18}},
            gauge={
                'axis': {'range': [0, value*2]},
                'bar': {'color': CIBAO_ORANGE},
                'bgcolor': "#333",
            }
        ))

        fig.update_layout(
            paper_bgcolor=CIBAO_BLACK,
            height=220,
            font=dict(color=CIBAO_GRAY)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};margin-top:-5px;margin-bottom:25px;'>
        <b>Conclusión táctica</b><br><br>
        • La <b>distancia media de disparo ({value:.1f} m)</b> refleja la capacidad del equipo para empujar al rival
          a zonas menos ventajosas, reduciendo la probabilidad de ocasiones claras.
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
    # PALETA HEATMAP CIBAO
    # ===========================

    HEATMAP_COLORSCALE = [
    [0.0, "#2a2a2a"],   # gris oscuro
    [0.5, "#ff7b00"],   # naranja cibao fuerte
    [1.0, "#ffae42"]    # naranja claro
    ]

    import numpy as np
    import plotly.graph_objects as go

    CIBAO_ORANGE = "#FF8C00"
    CIBAO_GRAY = "#D3D3D3"

# ===========================
# FUNCIÓN PARA HEATMAP — COLORES FIJOS POR RANKING
# ===========================

def plot_heatmap(nombre_grupo, mapping):

    dfp = df_filtrado.copy()

    cols = [v for v in mapping.values() if v in dfp.columns]
    labels = [k for k, v in mapping.items() if v in dfp.columns]

    if len(cols) == 0:
        st.warning(f"No hay datos disponibles para: {nombre_grupo}")
        return

    # ---------------------------
    # 1. Datos reales
    # ---------------------------
    series_real = dfp[cols].mean().fillna(0)

    # ---------------------------
    # 2. RANKING → 0,1,2 (bajo–medio–alto)
    # ---------------------------
    rank = series_real.rank(method="dense") - 1
    rank = rank.astype(int)

    # Convertir ranking a matriz 1×N (valores fijos 0–1–2)
    z_vals = rank.to_numpy().reshape(1, -1)

    # ---------------------------
    # 3. PALETA FIJA CIBAO PARA RANKING
    # ---------------------------
    HEATMAP_COLORSCALE = [
        [0.0, "#2a2a2a"],   # menor → gris oscuro
        [0.5, "#ff7b00"],   # medio → naranja fuerte cibao
        [1.0, "#ffae42"]    # mayor → naranja claro
    ]

    # ---------------------------
    # 4. HEATMAP
    # ---------------------------
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

    # ---------------------------
    # 5. Mostrar valores en cada celda
    # ---------------------------
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

    # ---------------------------
    # 6. CONCLUSIONES TÁCTICAS
    # ---------------------------
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
    # LAYOUT 2×2
    # ===========================

    col1, col2 = st.columns(2)

    with col1:
        plot_heatmap(
            "Mapa de Recuperaciones por Altura",
            grupos_tacticos["Mapa de Recuperaciones por Altura"]
        )

    with col2:
        plot_heatmap(
            "Mapa de Presión por Altura",
            grupos_tacticos["Mapa de Presión por Altura"]
        )

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
    # 📋 DICCIONARIO DE MÉTRICAS POR BLOQUE
    # ============================================================

    metrics_blocks = {

        "Ofensivas": {
            "Goles por partido": "goals",
            "xG (Goles esperados)": "xg",
            "Disparos por partido": "shots",
            "Disparos a puerta por partido": "shots_on_target",
            "Contraataques por 90": "counter_attacks",
            "Penaltis por 90": "penalties",
            "Centros por 90": "crosses",
            "Precisión de centros (%)": "crosses_accurate_percent",
            "Corners por 90": "corners",
        },

        "Construcción y Pase": {
            "Precisión de pase (%)": "passes_accurate_percent",
            "Precisión hacia adelante (%)": "forward_passes_accurate_percent",
            "Precisión pases largos (%)": "long_passes_accurate_percent",
            "Precisión al último tercio (%)": "passes_to_final_third_accurate_percent",
            "Precisión pases inteligentes (%)": "smart_passes_accurate_percent",
        },

        "Defensivas": {
            "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
            "Duelos aéreos ganados (%)": "aerial_duels_won_percent",
            "Intercepciones por 90": "interceptions",
            "Despejes por 90": "clearances",
            "Recuperaciones por 90": "recoveries",
            "Pérdidas de balón por 90": "losses",
            "PPDA": "ppda",
            "Disparos en contra por 90": "shots_against",
            "Disparos en contra a puerta por 90": "shots_against_on_target",
            "Eficiencia rival (%)": "shots_against_on_target_percent",
        },
    }

    # ============================================================
    # 🎨 PALETA CIBAO — GRADIENTE
    # ============================================================

    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib
    import io
    import pandas as pd

    CIBAO_ORANGE_CMAP = LinearSegmentedColormap.from_list(
        "cibao_orange",
        ["#2a2a2a", "#ff7b00", "#ffae42"]
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

            columnas = ["Match"] + list(metrics_dict.values())
            df_local = df[columnas].copy()

            df_local = df_local.rename(columns={v: k for k, v in metrics_dict.items()})
            df_local = df_local.round(2)

            st.markdown(
                f"### <span style='color:#ff8c00;'>⬤ {title}</span>", 
                unsafe_allow_html=True
            )

            styled = df_local.style.background_gradient(
                cmap="cibao_orange"
            ).set_properties(
                **{
                    "text-align": "center",
                    "font-size": "12px",
                    "border-color": "#333",
                }
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
            Las tablas comparativas permiten identificar rápidamente qué fases del juego están mostrando mayor rendimiento
            y en cuáles existe margen de mejora. El gradiente naranja destaca de manera intuitiva los valores más influyentes
            dentro de cada bloque analizado.
        </div>
        """, unsafe_allow_html=True)


