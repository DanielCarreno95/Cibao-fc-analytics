# ===========================================
# 1_Rendimiento_Colectivo.py — Cibao FC Data Hub (fix types + dict keys)
# ===========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing.load_cibao_team_data import load_cibao_team_data
from src.utils.metrics_dictionary import METRICS_DICT  # español -> nombre real
from graficos_de_navaja_suiza import (
    load_data as load_liga_mayor_data,
    make_team_scatter,
    METRIC_OPTIONS,
    DATA_FILE as LIGA_MAYOR_DATA_FILE,
)

# ---------- CONFIG ----------
st.set_page_config(page_title="Rendimiento Colectivo - Cibao FC", layout="wide")
PALETTE = ["#FF8C00", "#FFA94D", "#FFD6A5", "#F1F5F9"]
THEME_DARK = dict(template="plotly_dark",
                   paper_bgcolor="rgba(0,0,0,0)",
                   plot_bgcolor="rgba(0,0,0,0)")

# ---------- DATA ----------
try:
    df_cibao, df_rivales = load_cibao_team_data()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

df_cibao.columns = [c.strip().replace("\n", " ").replace("  ", " ") for c in df_cibao.columns]

@st.cache_data
def load_liga_mayor_per90():
    return load_liga_mayor_data(LIGA_MAYOR_DATA_FILE)


try:
    df_liga_mayor = load_liga_mayor_per90()
except Exception as exc:
    st.error(f"❌ Error cargando Liga Mayor per 90: {exc}")
    df_liga_mayor = pd.DataFrame()

# ---------- TITLES ----------
st.markdown("""
<h1 style='text-align:center; color:#FF8C00; text-shadow: 0 0 15px rgba(255,140,0,0.65); font-weight:900;'>
Rendimiento Colectivo — Cibao FC
</h1>
<p style='text-align:center; color:#D1D5DB; font-size:17px;'>
Lectura de <b>modelo de juego</b>, <b>eficiencia por fases</b> y <b>tendencias competitivas</b>.<br>
Diseñado para soporte táctico del staff técnico — decisiones claras, con contexto.
</p>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ---------- SIDEBAR: Filtros (Jornada y Partido con botón de reinicio) ----------
with st.sidebar:
    st.subheader("Filtros")

    # --- Listas de opciones ---
    jornadas = sorted(df_cibao["Jornada"].dropna().unique()) if "Jornada" in df_cibao.columns else []
    partidos = sorted(df_cibao["Match"].dropna().unique()) if "Match" in df_cibao.columns else []

    # --- Estado inicial (para recordar y resetear) ---
    if "filtros_reset" not in st.session_state:
        st.session_state["jornadas_sel"] = []
        st.session_state["partidos_sel"] = []
        st.session_state["filtros_reset"] = False

    # --- Multiselects ---
    jornadas_sel = st.multiselect(
        "Selecciona Jornadas",
        options=jornadas,
        default=st.session_state["jornadas_sel"] or jornadas,
        key="sidebar_jornadas",
    )

    partidos_sel = st.multiselect(
        "Selecciona Partidos",
        options=partidos,
        default=st.session_state["partidos_sel"] or partidos,
        key="sidebar_partidos",
    )

    # --- Botón de reinicio ---
    if st.button("🔄 Borrar filtros"):
        st.session_state["jornadas_sel"] = []
        st.session_state["partidos_sel"] = []
        st.session_state["filtros_reset"] = True
        st.experimental_rerun()  # 🔁 Recargar para aplicar los valores por defecto

# ---------- FILTRADO DE DATOS ----------
df_filtrado = df_cibao.copy()

# Si hay selección de jornadas
if jornadas_sel and "Jornada" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Jornada"].isin(jornadas_sel)]

# Si hay selección de partidos
if partidos_sel:
    df_filtrado = df_filtrado[df_filtrado["Match"].isin(partidos_sel)]

# Si no se selecciona nada (estado inicial o reset), mostrar todo
if (not jornadas_sel) and (not partidos_sel):
    df_filtrado = df_cibao.copy()

# ---------- HELPERS ----------
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

# ---------- BOTÓN GLOBAL DE REINICIO DE FILTROS Y MÉTRICAS (arriba a la derecha) ----------
cols_reset = st.columns([4, 1])  # proporción: contenido principal / botón
with cols_reset[1]:  # columna derecha
    if st.button("Restablecer filtros de la página", use_container_width=True):
        # Eliminar todos los estados de filtros y selecciones
        for key in list(st.session_state.keys()):
            if any(x in key for x in [
                "jornadas", "matches", "partidos", "metricas", "filtros",
                "tables", "efficiency", "passes", "offensive", "defensive", "tactical"
            ]):
                del st.session_state[key]

        st.toast("Filtros restablecidos a los valores por defecto ✅", icon="🔄")
        st.rerun()  # ✅ Nueva función en lugar de st.experimental_rerun()

# --- Separador visual antes de los KPIs ---
st.markdown("<br>", unsafe_allow_html=True)

# ---------- ANÁLISIS RÁPIDO CIBAO VS RIVAL ----------
if not df_liga_mayor.empty:
    st.markdown("## Comparativa liga (Cibao vs próximo rival)")
    col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1])
    team_options = sorted({str(t) for t in df_liga_mayor['Team'].dropna().unique() if str(t).strip().lower() != 'cibao'})
    if not team_options:
        st.info("No hay rivales disponibles en el dataset de Liga Mayor.")
    else:
        opponent_choice = col_sel1.selectbox("Próximo rival", team_options)
        metric_labels = list(METRIC_OPTIONS.keys())
        x_default = metric_labels.index("Goles por 90") if "Goles por 90" in metric_labels else 0
        y_default = metric_labels.index("Goles en contra por 90") if "Goles en contra por 90" in metric_labels else min(1, len(metric_labels) - 1)
        x_choice = col_sel2.selectbox("Métrica ofensiva (eje X)", metric_labels, index=x_default if metric_labels else 0)
        y_choice = col_sel3.selectbox("Métrica defensiva (eje Y)", metric_labels, index=y_default if metric_labels else 0)
        filters = {"Competition": lambda s: s.str.contains("Liga", case=False, na=False)}
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
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": True})
            if resumen_radar:
                st.caption(f"Resumen: {resumen_radar}")
else:
    st.warning("No se pudo cargar el dataset per 90 de Liga Mayor.")


# ---------- KPIs ----------
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


# ==============================
# EFICIENCIA Y ATAQUE — VARIACIÓN POR PARTIDO
# ==============================

import numpy as np
import plotly.express as px

st.subheader("Eficiencia y Ataque — Comparativa por Partido")
st.caption(
    "Analiza cómo varían las métricas ofensivas entre distintos partidos o rivales. "
    "Permite detectar patrones de finalización, efectividad y generación de peligro."
)

# --- Métricas ofensivas disponibles ---
offensive_metrics = {
    "Goles por partido": "goals",
    "Goles en contra por partido": "conceded_goals",
    "xG (Goles esperados)": "xg",
    "Disparos por partido": "shots",
    "Disparos a puerta por partido": "shots_on_target",
    "Contraataques por 90": "counter_attacks",
    "Contraataques con disparo (%)": "counter_attacks_with_shots_percent",
    "Corners por 90": "corners",
    "Corners con disparo (%)": "corners_with_shots_percent",
    "Faltas directas por 90": "free_kicks",
    "Faltas directas con disparo (%)": "free_kicks_with_shots_percent",
    "Penaltis por 90": "penalties",
    "Conversión de penaltis (%)": "penalties_converted_percent",
    "Entradas al área por 90": "penalty_area_entries",
    "Distancia media de disparo": "average_shot_distance",
}

# ==============================
# 🔍 FILTROS — JORNADA Y PARTIDO
# ==============================

cols_filtros = st.columns(2)

# --- Últimas 3 jornadas automáticas ---
ultimas_jornadas = (
    sorted(df_filtrado["Jornada"].unique())[-3:]
    if len(df_filtrado["Jornada"].unique()) >= 3
    else sorted(df_filtrado["Jornada"].unique())
)

with cols_filtros[0]:
    jornadas_sel = st.multiselect(
        "Selecciona jornadas (máx 5)",
        options=sorted(df_filtrado["Jornada"].unique().tolist()),
        default=ultimas_jornadas,
        key="offensive_jornadas",
        max_selections=5,
    )

# --- Partidos por defecto según jornadas seleccionadas ---
partidos_default = (
    df_filtrado[df_filtrado["Jornada"].isin(ultimas_jornadas)]
    .sort_values("Date")["Match"]
    .unique()
    .tolist()[:3]
)

with cols_filtros[1]:
    partidos_sel = st.multiselect(
        "Selecciona partidos para comparar (máx 4)",
        options=df_filtrado["Match"].unique().tolist(),
        default=partidos_default,
        key="offensive_matches",
        max_selections=4,
    )

# ==============================
# 📊 FILTRO DE MÉTRICAS
# ==============================

metrics_sel = st.multiselect(
    "Selecciona métricas ofensivas (máx 5)",
    list(offensive_metrics.keys()),
    default=["Goles por partido", "xG (Goles esperados)", "Disparos por partido"],
    max_selections=5,
    key="offensive_metrics",
)

# ==============================
# 📈 DATOS Y VISUALIZACIÓN
# ==============================

# --- Subconjunto de datos ---
df_off = df_filtrado[
    (df_filtrado["Match"].isin(partidos_sel)) & (df_filtrado["Jornada"].isin(jornadas_sel))
].copy()

if df_off.empty:
    st.warning("No hay datos disponibles para las jornadas o partidos seleccionados.")
else:
    # --- Transformar datos al formato largo ---
    metric_cols = [
        offensive_metrics[m]
        for m in metrics_sel
        if offensive_metrics[m] in df_off.columns
    ]
    df_long = df_off.melt(
        id_vars=["Match", "Date"],
        value_vars=metric_cols,
        var_name="metric",
        value_name="value",
    )
    df_long["metric_label"] = df_long["metric"].map(
        {v: k for k, v in offensive_metrics.items()}
    )
    df_long = df_long.dropna(subset=["value"])

    # --- Gráfico de barras horizontales con etiquetas ---
    PALETTE = ["#FF8C00", "#3B82F6", "#22C55E", "#EF4444", "#F59E0B"]

    fig_off = px.bar(
        df_long,
        x="value",
        y="metric_label",
        color="Match",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE,
        template="plotly_dark",
        text=df_long["value"].map(lambda v: f"{v:.1f}"),
        hover_data={"value": ":.2f", "Match": True, "metric_label": False},
    )

    fig_off.update_traces(
        textposition="outside",
        textfont=dict(size=11, color="#F3F4F6", family="Arial"),
        cliponaxis=False,
    )

    # ✅ Altura dinámica según nº de métricas seleccionadas
    dynamic_height = 280 + 40 * len(metrics_sel)
    fig_off.update_layout(
        height=dynamic_height,
        xaxis_title="Valor",
        yaxis_title="Métrica ofensiva",
        legend_title="Partido",
        bargap=0.25,
        bargroupgap=0.15,
    )
    st.plotly_chart(fig_off, use_container_width=True)

    # --- Insight automático ---
    resumen = (
        df_long.groupby("metric_label")["value"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
    )
    mejores = ", ".join([f"{m} ({v:.2f})" for m, v in resumen.items()])
    st.markdown(
        f"**Insight:** el equipo mostró un mejor rendimiento ofensivo en métricas como {mejores}. "
        f"Analiza si esta tendencia se mantiene frente a distintos rivales o contextos tácticos."
    )


# ==============================
# CONSTRUCCIÓN Y PASES — PRECISIÓN POR PARTIDO
# ==============================

import plotly.express as px

st.subheader("Construcción y Pases — Precisión por Partido")
st.caption(
    "Compara la precisión de los distintos tipos de pase en cada partido. "
    "Permite evaluar la consistencia en la circulación, el riesgo de los pases y la calidad técnica bajo presión."
)

# --- Métricas de precisión de pase ---
passing_metrics = {
    "Precisión de pase (%)": "passes_accurate_percent",
    "Precisión pases hacia adelante (%)": "forward_passes_accurate_percent",
    "Precisión pases hacia atrás (%)": "back_passes_accurate_percent",
    "Precisión pases laterales (%)": "lateral_passes_accurate_percent",
    "Precisión pases largos (%)": "long_passes_accurate_percent",
    "Precisión pases al último tercio (%)": "passes_to_final_third_accurate_percent",
    "Precisión pases inteligentes (%)": "smart_passes_accurate_percent",
    "Precisión saques de banda (%)": "throw_ins_accurate_percent",
    "Precisión de centros (%)": "crosses_accurate_percent",
}

# ==============================
# 🔍 FILTROS — JORNADA Y PARTIDO
# ==============================

cols_filtros = st.columns(2)

# --- Últimas 3 jornadas automáticas ---
ultimas_jornadas = (
    sorted(df_filtrado["Jornada"].unique())[-3:]
    if len(df_filtrado["Jornada"].unique()) >= 3
    else sorted(df_filtrado["Jornada"].unique())
)

with cols_filtros[0]:
    jornadas_sel = st.multiselect(
        "Selecciona jornadas (máx 5)",
        options=sorted(df_filtrado["Jornada"].unique().tolist()),
        default=ultimas_jornadas,
        key="passes_jornadas",
        max_selections=5,
    )

# --- Partidos por defecto según jornadas seleccionadas ---
partidos_default = (
    df_filtrado[df_filtrado["Jornada"].isin(ultimas_jornadas)]
    .sort_values("Date")["Match"]
    .unique()
    .tolist()[:3]
)

with cols_filtros[1]:
    partidos_sel = st.multiselect(
        "Selecciona partidos para comparar (máx 4)",
        options=df_filtrado["Match"].unique().tolist(),
        default=partidos_default,
        key="passes_matches",
        max_selections=4,
    )

# ==============================
# 📊 FILTRO DE MÉTRICAS
# ==============================

metrics_sel = st.multiselect(
    "Selecciona métricas de pase (máx 5)",
    list(passing_metrics.keys()),
    default=[
        "Precisión de pase (%)",
        "Precisión pases hacia adelante (%)",
        "Precisión pases largos (%)",
    ],
    max_selections=5,
    key="passes_metrics",
)

# ==============================
# 📈 DATOS Y VISUALIZACIÓN
# ==============================

# --- Subconjunto de datos ---
df_pass = df_filtrado[
    (df_filtrado["Match"].isin(partidos_sel)) & (df_filtrado["Jornada"].isin(jornadas_sel))
].copy()

if df_pass.empty:
    st.warning("No hay datos disponibles para las jornadas o partidos seleccionados.")
else:
    # --- Transformación al formato largo ---
    metric_cols = [
        passing_metrics[m] for m in metrics_sel if passing_metrics[m] in df_pass.columns
    ]
    df_long_pass = df_pass.melt(
        id_vars=["Match", "Date"],
        value_vars=metric_cols,
        var_name="metric",
        value_name="value",
    )
    df_long_pass["metric_label"] = df_long_pass["metric"].map(
        {v: k for k, v in passing_metrics.items()}
    )
    df_long_pass = df_long_pass.dropna(subset=["value"])

    # --- Gráfico de barras verticales con etiquetas ---
    PALETTE = ["#FF8C00", "#3B82F6", "#22C55E", "#EF4444", "#F59E0B"]

    fig_pass = px.bar(
        df_long_pass,
        x="Match",
        y="value",
        color="metric_label",
        barmode="group",
        color_discrete_sequence=PALETTE,
        template="plotly_dark",
        text=df_long_pass["value"].map(lambda v: f"{v:.1f}%"),
        hover_data={"value": ":.2f", "Match": True, "metric_label": False},
    )

    fig_pass.update_traces(
        textposition="outside",
        textfont=dict(size=11, color="#F3F4F6", family="Arial"),
        cliponaxis=False,
    )

    # ✅ Altura dinámica según nº de métricas seleccionadas
    dynamic_height_pass = 280 + 40 * len(metrics_sel)
    fig_pass.update_layout(
        height=dynamic_height_pass,
        xaxis_title="Partido",
        yaxis_title="Precisión (%)",
        legend_title="Tipo de pase",
        bargap=0.25,
        bargroupgap=0.15,
    )
    fig_pass.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_pass, use_container_width=True)

    # --- Insight automático ---
    resumen = (
        df_long_pass.groupby("metric_label")["value"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
    )
    mejores = ", ".join([f"{m} ({v:.1f}%)" for m, v in resumen.items()])
    st.markdown(
        f"**Insight:** las mayores precisiones de pase se observaron en {mejores}. "
        f"Estos resultados reflejan las zonas o estilos de circulación más seguros y consistentes del equipo."
    )

# ==============================
# DEFENSA Y EFICIENCIA — RESUMEN POR PARTIDO (GRÁFICOS CIRCULARES)
# ==============================

import plotly.graph_objects as go
import math

st.subheader("Defensa y Eficiencia — Resumen por Partido")
st.caption(
    "Selecciona las métricas defensivas que deseas visualizar y compara su distribución entre partidos. "
    "Cada gráfico circular representa un partido, mostrando la efectividad y volumen de las acciones defensivas."
)

# --- Métricas defensivas disponibles ---
defense_summary_metrics = {
    "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
    "Duelos aéreos ganados (%)": "aerial_duels_won_percent",
    "Éxito en entradas (%)": "sliding_tackles_successful_percent",
    "Intercepciones por 90": "interceptions",
    "Despejes por 90": "clearances",
    "Duelos ofensivos por 90": "offensive_duels",
    "Recuperaciones por 90": "recoveries",
    "Pérdidas de balón por 90": "losses",
    "Intensidad de presión (PPDA)": "ppda",
    "Disparos en contra por 90": "shots_against",
    "Disparos en contra a puerta por 90": "shots_against_on_target",
    "Eficiencia rival (disparos a puerta %)": "shots_against_on_target_percent",
}

# ==============================
# 🔍 FILTROS INTERACTIVOS
# ==============================

cols_sel = st.columns(2)

# --- Últimas 3 jornadas automáticas ---
ultimas_jornadas = (
    sorted(df_filtrado["Jornada"].unique())[-3:]
    if len(df_filtrado["Jornada"].unique()) >= 3
    else sorted(df_filtrado["Jornada"].unique())
)

with cols_sel[0]:
    jornadas_sel = st.multiselect(
        "Selecciona jornadas (máx 5)",
        options=sorted(df_filtrado["Jornada"].unique().tolist()),
        default=ultimas_jornadas,
        key="def_efficiency_jornadas",
        max_selections=5,
    )

# --- Partidos correspondientes a las jornadas seleccionadas ---
partidos_defecto = (
    df_filtrado[df_filtrado["Jornada"].isin(ultimas_jornadas)]
    .sort_values("Date")["Match"]
    .unique()
    .tolist()[:3]
)

with cols_sel[1]:
    partidos_sel = st.multiselect(
        "Selecciona partidos para comparar (máx 5)",
        options=df_filtrado["Match"].unique().tolist(),
        default=partidos_defecto,
        key="def_efficiency_partidos",
        max_selections=5,
    )

# --- Selección de métricas ---
metrics_sel = st.multiselect(
    "Selecciona métricas defensivas (mín 5, máx 7)",
    options=list(defense_summary_metrics.keys()),
    default=[
        "Duelos defensivos ganados (%)",
        "Intercepciones por 90",
        "Recuperaciones por 90",
        "Despejes por 90",
        "Pérdidas de balón por 90",
    ],
    max_selections=7,
    key="def_efficiency_metrics",
)

# ==============================
# 🧩 GENERACIÓN DE GRÁFICOS
# ==============================

if len(metrics_sel) < 5:
    st.warning("Selecciona al menos 5 métricas defensivas para generar los gráficos.")
elif not partidos_sel:
    st.info("Selecciona al menos un partido para mostrar el resumen defensivo.")
else:
    # Filtrar el DataFrame
    df_def = df_filtrado[
        (df_filtrado["Match"].isin(partidos_sel)) & (df_filtrado["Jornada"].isin(jornadas_sel))
    ].copy()

    if df_def.empty:
        st.warning("No hay datos disponibles para las jornadas o partidos seleccionados.")
    else:
        # Layout 3x3 (hasta 9 gráficos)
        n_partidos = len(partidos_sel)
        n_cols = 3
        n_rows = math.ceil(n_partidos / n_cols)

        # Iterar por filas y columnas
        for i in range(n_rows):
            cols = st.columns(n_cols)
            for j in range(n_cols):
                idx = i * n_cols + j
                if idx < n_partidos:
                    match = partidos_sel[idx]
                    df_match = df_def[df_def["Match"] == match]
                    if df_match.empty:
                        continue

                    with cols[j]:
                        st.markdown(f"**{match}**")

                        labels = metrics_sel
                        values = [
                            df_match.iloc[0][defense_summary_metrics[m]]
                            if defense_summary_metrics[m] in df_match.columns
                            else 0
                            for m in metrics_sel
                        ]

                        # --- Gráfico circular con formato profesional ---
                        fig_pie = go.Figure(
                            data=[
                                go.Pie(
                                    labels=labels,
                                    values=values,
                                    text=[f"{v:.1f}" for v in values],
                                    textinfo="label+text",
                                    textfont=dict(size=12, color="#F5F5F5"),
                                    insidetextorientation="radial",
                                    marker=dict(
                                        colors=[
                                            "#FF8C00", "#3B82F6", "#22C55E",
                                            "#EF4444", "#F59E0B", "#8B5CF6", "#14B8A6"
                                        ][: len(metrics_sel)],
                                        line=dict(color="rgba(255,255,255,0.2)", width=1),
                                    ),
                                )
                            ]
                        )

                        fig_pie.update_layout(
                            template="plotly_dark",
                            height=420,
                            margin=dict(t=15, b=15, l=15, r=15),
                            showlegend=False,
                        )

                        st.plotly_chart(fig_pie, use_container_width=True)


# ==============================
# DISTRIBUCIÓN TÁCTICA — PRESIÓN Y RECUPERACIONES (LAYOUT 3x3)
# ==============================

import plotly.express as px
import math

st.subheader("Distribución Táctica — Presión y Recuperaciones")
st.caption(
    "Analiza la distribución de las pérdidas y recuperaciones del equipo según la altura del campo. "
    "Cada columna representa una jornada o partido, mostrando la intensidad de la presión (arriba) "
    "y la frecuencia de recuperaciones (abajo)."
)

# --- Métricas ---
pressure_metrics = {
    "Presión alta (estimada)": "losses_high",
    "Presión media (estimada)": "losses_medium",
    "Presión baja (estimada)": "losses_low",
}

recovery_metrics = {
    "Recuperaciones altas por 90": "recoveries_high",
    "Recuperaciones medias por 90": "recoveries_medium",
    "Recuperaciones bajas por 90": "recoveries_low",
}

# ==============================
# 🔍 FILTROS DE JORNADA Y PARTIDO
# ==============================

cols_filters = st.columns(2)

# Últimas 3 jornadas automáticas
ultimas_jornadas = (
    sorted(df_filtrado["Jornada"].unique())[-3:]
    if len(df_filtrado["Jornada"].unique()) >= 3
    else sorted(df_filtrado["Jornada"].unique())
)

with cols_filters[0]:
    jornadas_sel = st.multiselect(
        "Selecciona jornadas (máx 5)",
        options=sorted(df_filtrado["Jornada"].unique().tolist()),
        default=ultimas_jornadas,
        key="tactical_heatmap_jornadas",
        max_selections=5,
    )

# Partidos por defecto según jornadas
partidos_default = (
    df_filtrado[df_filtrado["Jornada"].isin(ultimas_jornadas)]
    .sort_values("Date")["Match"]
    .unique()
    .tolist()[:3]
)

with cols_filters[1]:
    partidos_sel = st.multiselect(
        "Selecciona partidos (máx 5)",
        options=df_filtrado["Match"].unique().tolist(),
        default=partidos_default,
        key="tactical_heatmap_partidos",
        max_selections=5,
    )

# --- Filtrar dataset final ---
df_view = df_filtrado[
    (df_filtrado["Jornada"].isin(jornadas_sel)) & (df_filtrado["Match"].isin(partidos_sel))
].copy()

if df_view.empty:
    st.warning("No hay datos disponibles para las jornadas o partidos seleccionados.")
else:
    # ==============================
    # 🎨 Colores personalizados
    # ==============================
    PRESSURE_COLORS = [
        [0.0, "#1E1E1E"],
        [0.3, "#403020"],
        [0.6, "#A85C00"],
        [1.0, "#FF8C00"],
    ]
    RECOVERY_COLORS = [
        [0.0, "#1E1E1E"],
        [0.3, "#1F3A2E"],
        [0.6, "#228B22"],
        [1.0, "#22C55E"],
    ]

    # ==============================
    # 📊 Layout 3x3: presión arriba, recuperación abajo
    # ==============================

    jornadas_unicas = sorted(df_view["Jornada"].unique())[:3]  # máx 3 visibles por fila
    n_cols = min(3, len(jornadas_unicas))  # ajusta columnas según cantidad
    n_rows = math.ceil(len(jornadas_unicas) / n_cols)

    st.markdown("### 🔶 Presión — Pérdidas estimadas")
    cols_top = st.columns(n_cols)

    for i, jornada in enumerate(jornadas_unicas):
        with cols_top[i]:
            df_jornada = df_view[df_view["Jornada"] == jornada]
            partido = (
                df_jornada["Match"].iloc[-1]
                if not df_jornada.empty
                else f"Jornada {jornada}"
            )

            st.markdown(f"**{partido}**")

            df_pressure = df_jornada.melt(
                value_vars=list(pressure_metrics.values()),
                var_name="Zona",
                value_name="Valor",
            )
            df_pressure["Zona"] = df_pressure["Zona"].map(
                {v: k for k, v in pressure_metrics.items()}
            )

            fig_pressure = px.imshow(
                [df_pressure["Valor"]],
                x=df_pressure["Zona"],
                color_continuous_scale=PRESSURE_COLORS,
                aspect="auto",
                text_auto=".1f",
            )
            fig_pressure.update_layout(
                template="plotly_dark",
                title=dict(
                    text=f"Presión (Jornada {jornada})",
                    font=dict(size=13, color="#E5E7EB"),
                ),
                height=300,
                margin=dict(t=35, b=20, l=15, r=15),
                coloraxis_colorbar=dict(
                    title=dict(text="Intensidad", font=dict(color="#D1D5DB", size=11)),
                    tickfont=dict(color="#D1D5DB", size=10),
                ),
            )
            fig_pressure.update_xaxes(title=None, tickfont=dict(size=10, color="#E5E7EB"))
            st.plotly_chart(fig_pressure, use_container_width=True)

    st.markdown("### 🟢 Recuperaciones — Por zonas del campo")
    cols_bottom = st.columns(n_cols)

    for i, jornada in enumerate(jornadas_unicas):
        with cols_bottom[i]:
            df_jornada = df_view[df_view["Jornada"] == jornada]
            partido = (
                df_jornada["Match"].iloc[-1]
                if not df_jornada.empty
                else f"Jornada {jornada}"
            )

            df_recovery = df_jornada.melt(
                value_vars=list(recovery_metrics.values()),
                var_name="Zona",
                value_name="Valor",
            )
            df_recovery["Zona"] = df_recovery["Zona"].map(
                {v: k for k, v in recovery_metrics.items()}
            )

            fig_recovery = px.imshow(
                [df_recovery["Valor"]],
                x=df_recovery["Zona"],
                color_continuous_scale=RECOVERY_COLORS,
                aspect="auto",
                text_auto=".1f",
            )
            fig_recovery.update_layout(
                template="plotly_dark",
                title=dict(
                    text=f"Recuperaciones (Jornada {jornada})",
                    font=dict(size=13, color="#E5E7EB"),
                ),
                height=300,
                margin=dict(t=35, b=20, l=15, r=15),
                coloraxis_colorbar=dict(
                    title=dict(text="Frecuencia", font=dict(color="#D1D5DB", size=11)),
                    tickfont=dict(color="#D1D5DB", size=10),
                ),
            )
            fig_recovery.update_xaxes(title=None, tickfont=dict(size=10, color="#E5E7EB"))
            st.plotly_chart(fig_recovery, use_container_width=True)

    # ==============================
    # 💡 Insight automático
    # ==============================
    if not df_view.empty:
        ultima_jornada = max(jornadas_sel)
        ultimo_partido = partidos_sel[-1] if partidos_sel else None
        df_last = df_view[
            (df_view["Jornada"] == ultima_jornada)
            & (df_view["Match"] == ultimo_partido)
        ]
        if not df_last.empty:
            press_high = df_last[pressure_metrics["Presión alta (estimada)"]].mean()
            rec_high = df_last[recovery_metrics["Recuperaciones altas por 90"]].mean()
            st.markdown(
                f"**Insight:** En la jornada **{ultima_jornada}**, partido **{ultimo_partido}**, "
                f"la presión alta media fue de **{press_high:.1f}** y las recuperaciones altas promedio **{rec_high:.1f}**. "
                "Esto refleja el grado de agresividad e intensidad del bloque en la recuperación tras pérdida."
            )

# ==============================
# ANÁLISIS COMPARATIVO — TABLAS OFENSIVA, CONSTRUCCIÓN Y DEFENSIVA (PALETAS PERSONALIZADAS)
# ==============================

import pandas as pd
import io
from matplotlib.colors import LinearSegmentedColormap

st.subheader("Análisis Comparativo por Bloques")
st.caption(
    "Visualiza y compara los indicadores clave del rendimiento colectivo en tres fases del juego: "
    "**ofensiva**, **construcción/pase** y **defensiva**. "
    "El formato condicional usa una paleta cromática personalizada de 5 tonos para cada bloque, "
    "de menor a mayor rendimiento."
)

# --- Diccionario de métricas ---
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
        "Precisión pases hacia adelante (%)": "forward_passes_accurate_percent",
        "Precisión pases largos (%)": "long_passes_accurate_percent",
        "Precisión pases al último tercio (%)": "passes_to_final_third_accurate_percent",
        "Precisión pases inteligentes (%)": "smart_passes_accurate_percent",
        "Precisión de centros (%)": "crosses_accurate_percent",
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

# ==============================
# 🎨 Paletas personalizadas
# ==============================

cmap_off = LinearSegmentedColormap.from_list(
    "reds_custom", ["#3d0000", "#6b0000", "#a10000", "#d02c2c", "#ff6b6b"]
)
cmap_pass = LinearSegmentedColormap.from_list(
    "yellows_custom", ["#332700", "#7a5500", "#b87c00", "#e8a600", "#ffd75a"]
)
cmap_def = LinearSegmentedColormap.from_list(
    "greens_custom", ["#002b00", "#005c00", "#008a00", "#4cb34c", "#8cff8c"]
)

# ==============================
# 🔍 FILTROS
# ==============================

cols_filtros = st.columns(2)
with cols_filtros[0]:
    partidos_ordenados = df_filtrado.sort_values("Date")["Match"].unique().tolist()
    partidos_default = partidos_ordenados[-3:]
    partidos_sel = st.multiselect(
        "Selecciona partidos (máx 5)",
        options=partidos_ordenados,
        default=partidos_default,
        key="tables_partidos",
        max_selections=5,
    )

with cols_filtros[1]:
    jornadas_ordenadas = sorted(df_filtrado["Jornada"].unique().tolist())
    jornadas_default = jornadas_ordenadas[-3:]
    jornadas_sel = st.multiselect(
        "Selecciona jornadas (máx 5)",
        options=jornadas_ordenadas,
        default=jornadas_default,
        key="tables_jornadas",
        max_selections=5,
    )

df_base = df_filtrado[
    (df_filtrado["Match"].isin(partidos_sel)) | (df_filtrado["Jornada"].isin(jornadas_sel))
].copy()

df_base = df_base.sort_values("Date", ascending=False).head(5)

# ==============================
# FUNCIONES DE TABLA
# ==============================

def build_table(df, metrics_dict, title, cmap):
    df_local = df[["Date", "Jornada", "Match"] + list(metrics_dict.values())].copy()
    df_local["Date"] = pd.to_datetime(df_local["Date"]).dt.strftime("%d-%m-%Y")
    df_local = df_local.rename(columns={v: k for k, v in metrics_dict.items()})
    df_local = df_local.sort_values(["Jornada", "Date"], ascending=[True, False])
    df_local = df_local.reset_index(drop=True)

    for col in metrics_dict.keys():
        if pd.api.types.is_numeric_dtype(df_local[col]):
            df_local[col] = df_local[col].round(2)

    st.markdown(f"### {title}")
    styled_df = (
        df_local.style
        .background_gradient(cmap=cmap, subset=list(metrics_dict.keys()), axis=0)
        .set_properties(**{"text-align": "center"})
        .format(precision=2)
    )
    st.dataframe(styled_df, use_container_width=True)
    return df_local


# ==============================
# 📊 BLOQUES
# ==============================

if not df_base.empty:
    st.divider()
    st.markdown("## 🔴 Bloque Ofensivo")
    df_off = build_table(df_base, metrics_blocks["Ofensivas"], "Tabla Ofensiva", cmap=cmap_off)

    st.divider()
    st.markdown("## 🟡 Bloque de Construcción y Pase")
    df_pass = build_table(df_base, metrics_blocks["Construcción y Pase"], "Tabla de Construcción y Pase", cmap=cmap_pass)

    st.divider()
    st.markdown("## 🟢 Bloque Defensivo")
    df_def = build_table(df_base, metrics_blocks["Defensivas"], "Tabla Defensiva", cmap=cmap_def)

    # ==============================
    # 📥 DESCARGA
    # ==============================
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_off.to_excel(writer, sheet_name="Ofensivas", index=False)
        df_pass.to_excel(writer, sheet_name="Construccion_Pase", index=False)
        df_def.to_excel(writer, sheet_name="Defensivas", index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Descargar todas las tablas en Excel",
        data=buffer,
        file_name="analisis_completo_cibao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown(
        f"**Insight general:** se muestran hasta {len(df_base)} partidos recientes. "
        "Los tonos más intensos dentro de cada columna reflejan los valores más altos de rendimiento, "
        "con una escala cromática estable y diferenciada por bloque."
    )
else:
    st.info("Selecciona al menos un partido o una jornada para generar las tablas comparativas.")

# ==============================
# FIGURA DE KPIs PARA EL PDF (a partir del último partido filtrado)
# ==============================
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def _fmt_percent(x):
    if pd.isna(x): return "-"
    try: return f"{float(x):.2f}%"
    except: return str(x)

def _fmt_num(x):
    if pd.isna(x): return "-"
    try: 
        v = float(x)
        # entero si no tiene decimales, si no 2 decimales
        return f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}"
    except:
        return str(x)

def _fmt_text(x):
    if pd.isna(x) or x == "": return "-"
    return str(x)

def build_fig_kpi(df_base: pd.DataFrame) -> go.Figure:
    if df_base is None or df_base.empty:
        # fallback a todo el dataset si el filtrado quedó vacío
        df_use = df_cibao.copy()
    else:
        df_use = df_base.copy()

    # último partido por fecha
    if "Date" in df_use.columns:
        df_use = df_use.sort_values("Date")
    last = df_use.iloc[-1]

    # extraer campos esperados (con fallback si no existen)
    date_raw   = last.get("Date", "")
    date_fmt   = pd.to_datetime(date_raw).strftime("%d-%m-%Y") if pd.notna(date_raw) and str(date_raw) != "" else "-"
    jornada    = last.get("Jornada", "-")
    match      = last.get("Match", "-")
    final_res  = last.get("Final Result", last.get("Resultado Final", "-"))
    alineacion = last.get("Alineacion", last.get("Alineación", "-"))
    xg         = last.get("xg", last.get("xG", np.nan))
    poss       = last.get("possession_percent", last.get("Posesión (%)", np.nan))
    yc         = last.get("yellow_cards", last.get("tarjetas_amarillas", np.nan))
    rc         = last.get("red_cards", last.get("tarjetas_rojas", np.nan))

    # armar los KPIs clave (mismos que enseñaste)
    labels = [
        "Fecha", "Jornada", "Partido", "Resultado Final", "Alineación",
        "Goles Esperados (xG)", "Posesión (%)", "Tarjetas amarillas", "Tarjetas rojas"
    ]
    values = [
        _fmt_text(date_fmt),
        _fmt_text(jornada),
        _fmt_text(match),
        _fmt_text(final_res),
        _fmt_text(alineacion),
        _fmt_num(xg),
        _fmt_percent(poss),
        _fmt_num(yc),
        _fmt_num(rc),
    ]

    # tabla compacta para cabecera de PDF
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=["<b>KPI</b>", "<b>Valor</b>"],
                fill_color="#1D232F",
                font=dict(color="#F3F4F6", size=16),
                align="left",
                height=34
            ),
            cells=dict(
                values=[labels, values],
                fill_color=[["#0B0F17"] * len(labels), ["#0B0F17"] * len(values)],
                font=dict(color="#E5E7EB", size=15),
                align="left",
                height=30
            )
        )
    ])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,  # el exportador ajusta el width, aquí fijamos altura razonable
    )
    return fig

# construir fig_kpi desde el df_filtrado actual (o dataset si quedó vacío)
try:
    fig_kpi = build_fig_kpi(df_filtrado if 'df_filtrado' in globals() else df_cibao)
except Exception as e:
    st.warning(f"No se pudo construir fig_kpi: {e}")
    fig_kpi = None

# ==============================
# 📄 INFORME DE RENDIMIENTO COLECTIVO — PDF PROFESIONAL (2 PÁGINAS)
# ==============================

import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
PAGE_W, PAGE_H = 2400, 1600  # horizontal
MARGIN = 60
GAP = 28

# --- FUNCIÓN AUXILIAR: exportar figura a PNG ---
def export_fig_png(fig, w, h, scale=3):
    if fig is None:
        return None
    f = go.Figure(fig)
    f.update_layout(
        width=int(w),
        height=int(h),
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    try:
        return f.to_image(format="png", scale=scale)
    except Exception:
        st.warning("⚠️ No se pudo exportar una figura (falta 'kaleido'?).")
        return None

# --- FIGURA KPI (tabla superior) ---
def _fmt_percent(x):
    if pd.isna(x): return "-"
    try: return f"{float(x):.2f}%"
    except: return str(x)

def _fmt_num(x):
    if pd.isna(x): return "-"
    try: 
        v = float(x)
        return f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}"
    except:
        return str(x)

def _fmt_text(x):
    if pd.isna(x) or x == "": return "-"
    return str(x)

def build_fig_kpi(df_base: pd.DataFrame) -> go.Figure:
    if df_base is None or df_base.empty:
        df_use = df_cibao.copy()
    else:
        df_use = df_base.copy()

    if "Date" in df_use.columns:
        df_use = df_use.sort_values("Date")
    last = df_use.iloc[-1]

    date_raw   = last.get("Date", "")
    date_fmt   = pd.to_datetime(date_raw).strftime("%d-%m-%Y") if pd.notna(date_raw) and str(date_raw) != "" else "-"
    jornada    = last.get("Jornada", "-")
    match      = last.get("Match", "-")
    final_res  = last.get("Final Result", last.get("Resultado Final", "-"))
    alineacion = last.get("Alineacion", last.get("Alineación", "-"))
    xg         = last.get("xg", last.get("xG", np.nan))
    poss       = last.get("possession_percent", last.get("Posesión (%)", np.nan))
    yc         = last.get("yellow_cards", last.get("tarjetas_amarillas", np.nan))
    rc         = last.get("red_cards", last.get("tarjetas_rojas", np.nan))

    labels = [
        "Fecha", "Jornada", "Partido", "Resultado Final", "Alineación",
        "Goles Esperados (xG)", "Posesión (%)", "Tarjetas amarillas", "Tarjetas rojas"
    ]
    values = [
        _fmt_text(date_fmt),
        _fmt_text(jornada),
        _fmt_text(match),
        _fmt_text(final_res),
        _fmt_text(alineacion),
        _fmt_num(xg),
        _fmt_percent(poss),
        _fmt_num(yc),
        _fmt_num(rc),
    ]

    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=["<b>KPI</b>", "<b>Valor</b>"],
                fill_color="#1D232F",
                font=dict(color="#F3F4F6", size=16),
                align="left",
                height=34
            ),
            cells=dict(
                values=[labels, values],
                fill_color=[["#0B0F17"] * len(labels), ["#0B0F17"] * len(values)],
                font=dict(color="#E5E7EB", size=15),
                align="left",
                height=30
            )
        )
    ])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
    )
    return fig

# --- PLACEHOLDERS DE SEGURIDAD ---
def _placeholder_fig(text, color="#FF8C00"):
    fig = go.Figure()
    fig.add_annotation(
        text=text,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=22, color=color, family="Arial"),
        xref="paper", yref="paper"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        margin=dict(l=0, r=0, t=0, b=0),
        height=300
    )
    return fig

# --- Verificar o crear figuras base ---
try:
    fig_kpi = build_fig_kpi(df_filtrado if 'df_filtrado' in globals() else df_cibao)
except Exception as e:
    st.warning(f"No se pudo construir fig_kpi: {e}")
    fig_kpi = _placeholder_fig("KPIs no disponibles")

if "fig_defense" not in globals():
    fig_defense = _placeholder_fig("⚠️ No hay gráfico defensivo disponible")

if "fig_heatmap" not in globals():
    fig_heatmap = _placeholder_fig("⚠️ No hay heatmap disponible")

if "fig_tables" not in globals():
    fig_tables = _placeholder_fig("⚠️ No hay tablas comparativas disponibles")

if "fig_off" not in globals():
    fig_off = _placeholder_fig("⚠️ No hay gráfico ofensivo disponible")

if "fig_pass" not in globals():
    fig_pass = _placeholder_fig("⚠️ No hay gráfico de construcción disponible")

# --- FUNCIÓN PRINCIPAL PDF ---
def generar_informe_pdf(figs, logo_path=None):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    BG = HexColor("#0B0F17")
    FG = HexColor("#F3F4F6")
    ORANGE = HexColor("#FF8C00")
    MUTED = HexColor("#9AA2AD")

    # ---------- PÁGINA 1 ----------
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(FG)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(MARGIN, PAGE_H - MARGIN - 10, "ANÁLISIS DE RENDIMIENTO COLECTIVO")
    c.setFont("Helvetica", 20)
    c.setFillColor(MUTED)
    c.drawString(MARGIN, PAGE_H - MARGIN - 45, "Temporada 2024/25 — Últimos partidos")
    c.setFont("Helvetica", 16)
    c.setFillColor(FG)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN - 20, datetime.now().strftime("%d/%m/%Y"))

    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, PAGE_W - 320, PAGE_H - 220, width=220, height=140, mask='auto')
        except:
            pass

    # --- KPIs ---
    if figs.get("kpis"):
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(ORANGE)
        c.drawString(MARGIN, PAGE_H - 230, "Indicadores Clave de Rendimiento (KPIs)")
        hero_img = ImageReader(io.BytesIO(figs["kpis"]))
        c.drawImage(hero_img, MARGIN, PAGE_H - 230 - 300, width=PAGE_W - 2*MARGIN, height=260, mask='auto')

    # --- OFENSIVA Y CONSTRUCCIÓN ---
    y_base = PAGE_H - 600
    sec_h = 420
    cell_w = (PAGE_W - 3*MARGIN) / 2
    if figs.get("offensive") or figs.get("passing"):
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(ORANGE)
        c.drawString(MARGIN, y_base + sec_h + 40, "Rendimiento Ofensivo y Construcción")
        if figs.get("offensive"):
            off_img = ImageReader(io.BytesIO(figs["offensive"]))
            c.drawImage(off_img, MARGIN, y_base, width=cell_w, height=sec_h, mask='auto')
        if figs.get("passing"):
            pass_img = ImageReader(io.BytesIO(figs["passing"]))
            c.drawImage(pass_img, MARGIN + cell_w + GAP, y_base, width=cell_w, height=sec_h, mask='auto')

    # ---------- PÁGINA 2 ----------
    c.showPage()
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(FG)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(MARGIN, PAGE_H - MARGIN - 10, "Bloque Defensivo y Análisis Táctico")

    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, PAGE_W - 300, PAGE_H - 200, width=200, height=120, mask='auto')
        except:
            pass

    if figs.get("defense"):
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(ORANGE)
        c.drawString(MARGIN, PAGE_H - 260, "Defensa y Eficiencia")
        def_img = ImageReader(io.BytesIO(figs["defense"]))
        c.drawImage(def_img, MARGIN, PAGE_H - 800, width=PAGE_W - 2*MARGIN, height=480, mask='auto')

    if figs.get("heatmap"):
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(ORANGE)
        c.drawString(MARGIN, PAGE_H - 840, "Distribución Táctica — Presión y Recuperaciones")
        heat_img = ImageReader(io.BytesIO(figs["heatmap"]))
        c.drawImage(heat_img, MARGIN, PAGE_H - 1400, width=PAGE_W - 2*MARGIN, height=480, mask='auto')

    if figs.get("tables"):
        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(ORANGE)
        c.drawString(MARGIN, PAGE_H - 1460, "Tablas Comparativas")
        table_img = ImageReader(io.BytesIO(figs["tables"]))
        c.drawImage(table_img, MARGIN, MARGIN + 40, width=PAGE_W - 2*MARGIN, height=340, mask='auto')

    c.showPage()
    c.save()
    return buf.getvalue()

# ==============================
# 📦 GENERACIÓN INTERACTIVA
# ==============================

st.markdown("### 📘 Exportar Informe Técnico de Rendimiento Colectivo")

include_kpis = st.checkbox("Incluir KPIs", True)
include_off  = st.checkbox("Incluir bloque Ofensivo", True)
include_pass = st.checkbox("Incluir bloque de Construcción y Pase", True)
include_def  = st.checkbox("Incluir bloque Defensivo", True)
include_heat = st.checkbox("Incluir Distribución Táctica (Heatmaps)", True)
include_tab  = st.checkbox("Incluir Tablas Comparativas", True)

if st.button("📄 Generar Informe en PDF"):
    try:
        figs = {}
        if include_kpis: figs["kpis"] = export_fig_png(fig_kpi, PAGE_W - 2*MARGIN, 260)
        if include_off:  figs["offensive"] = export_fig_png(fig_off, (PAGE_W - 3*MARGIN)/2, 420)
        if include_pass: figs["passing"] = export_fig_png(fig_pass, (PAGE_W - 3*MARGIN)/2, 420)
        if include_def:  figs["defense"] = export_fig_png(fig_defense, PAGE_W - 2*MARGIN, 480)
        if include_heat: figs["heatmap"] = export_fig_png(fig_heatmap, PAGE_W - 2*MARGIN, 480)
        if include_tab:  figs["tables"] = export_fig_png(fig_tables, PAGE_W - 2*MARGIN, 340)

        pdf_bytes = generar_informe_pdf(figs, logo_path="logo_cibao.png")
        st.download_button(
            "⬇️ Descargar Informe PDF (2 páginas)",
            data=pdf_bytes,
            file_name=f"Informe_Rendimiento_Colectivo_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"❌ Error generando PDF: {e}")

