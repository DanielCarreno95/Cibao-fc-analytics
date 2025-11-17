# ===========================================
# 1_Rendimiento_Colectivo_-_Liga.py — Cibao FC Data Hub
# ===========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing.load_cibao_team_data import load_cibao_team_data
from src.utils.metrics_dictionary import METRICS_DICT
from graficos_de_navaja_suiza import (
    load_data as load_liga_mayor_data,
    make_team_scatter,
    METRIC_OPTIONS,
    DATA_FILE as LIGA_MAYOR_DATA_FILE,
)

# ---------- CONFIG ----------
st.set_page_config(page_title="Rendimiento Colectivo - Liga", layout="wide")

# ---------- AÑADIR FONDO NEGRO FIJO ----------
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #000000 !important;
    color: white !important;
}

/* Evita que Chrome / Edge activen tema claro */
:root {
    color-scheme: dark !important;
}

/* Evita ajustes automáticos */
html {
    forced-color-adjust: none !important;
}

/* Limpia fondos blancos de contenedores */
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}

</style>
""", unsafe_allow_html=True)

PALETTE = ["#FF8C00", "#FFA94D", "#FFD6A5", "#F1F5F9"]
THEME_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# ---------- ENCABEZADO VISUAL DEL SIDEBAR ----------
with st.sidebar:
    st.markdown("""
    <h3 style='margin-top:0; color:#ff7b00;'>📊 Análisis Liga</h3>
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
st.markdown("""
<h1 style='text-align:center; color:#FF8C00; text-shadow: 0 0 15px rgba(255,140,0,0.65); font-weight:900;'>
Rendimiento Colectivo — Cibao FC (Liga)
</h1>
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
        """,
        unsafe_allow_html=True,
    )

    # ✅ Multiselect nativo, compacto y limpio
    selection = st.multiselect(
        "",
        options,
        default=default,
        key=key,
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)
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
# Bloque 0 ANÁLISIS RÁPIDO CIBAO VS RIVAL
# ==============================

if not df_liga_mayor.empty:
    st.markdown(
        f"""
        <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
        Comparativa liga (Cibao vs próximo rival)
        </h2>
        <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
        Evalúa el rendimiento del Cibao FC frente a su próximo rival, considerando métricas ofensivas y defensivas clave.
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
            st.plotly_chart(
                fig_radar, use_container_width=True, config={"displayModeBar": True}
            )
            if resumen_radar:
                st.caption(f"Resumen: {resumen_radar}")
else:
    st.warning("No se pudo cargar el dataset per 90 de Liga Mayor.")


# ==============================
# BLOQUE 1 — EFICIENCIA Y ATAQUE (Horizontal)
# ==============================
def bloque_eficiencia_ataque(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Eficiencia y Ataque</h3>", unsafe_allow_html=True)
    st.caption(
        "Evalúa la productividad ofensiva del Cibao FC analizando goles, xG y disparos por partido en comparación con otros equipos."
    )

    offensive_metrics = {
        "Goles por partido": "goals",
        "xG (Goles esperados)": "xg",
        "Disparos por partido": "shots",
        "Disparos a puerta por partido": "shots_on_target",
        "Contraataques por 90": "counter_attacks",
        "Entradas al área por 90": "penalty_area_entries",
    }

    metrics_sel = st.multiselect(
        "Selecciona métricas ofensivas (máx 5)",
        list(offensive_metrics.keys()),
        default=["Goles por partido", "xG (Goles esperados)", "Disparos por partido"],
        max_selections=5,
        key="of_metrics",
    )

    df_off = df_filtrado[
        (df_filtrado["Match"].isin(partidos_sel))
        & (df_filtrado["Jornada"].isin(jornadas_sel))
    ].copy()

    if df_off.empty:
        st.warning("No hay datos disponibles.")
        return

    df_long = df_off.melt(
        id_vars=["Match"],
        value_vars=[
            offensive_metrics[m]
            for m in metrics_sel
            if offensive_metrics[m] in df_off.columns
        ],
        var_name="metric",
        value_name="value",
    )
    df_long["metric_label"] = df_long["metric"].map(
        {v: k for k, v in offensive_metrics.items()}
    )

    fig = px.bar(
        df_long,
        x="value",
        y="Match",
        color="metric_label",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE_CIBAO,
        template="plotly_dark",
        text_auto=".1f",
    )
    fig.update_traces(textfont=dict(size=11), textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=260,
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        xaxis_title="Valor",
        yaxis_title=None,
        legend_title="Métrica ofensiva",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ==============================
# BLOQUE 2 — CONSTRUCCIÓN Y PASES (Horizontal)
# ==============================
def bloque_construccion_pases(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Construcción y Pases</h3>", unsafe_allow_html=True)
    st.caption(
        "Analiza la precisión y calidad de los pases en distintas zonas del campo, mostrando la consistencia técnica del equipo."
    )

    passing_metrics = {
        "Precisión de pase (%)": "passes_accurate_percent",
        "Precisión hacia adelante (%)": "forward_passes_accurate_percent",
        "Precisión pases largos (%)": "long_passes_accurate_percent",
        "Precisión al último tercio (%)": "passes_to_final_third_accurate_percent",
        "Precisión de centros (%)": "crosses_accurate_percent",
    }

    metrics_sel = st.multiselect(
        "Selecciona métricas de pase (máx 5)",
        list(passing_metrics.keys()),
        default=[
            "Precisión de pase (%)",
            "Precisión hacia adelante (%)",
            "Precisión pases largos (%)",
        ],
        max_selections=5,
        key="pa_metrics",
    )

    df_pass = df_filtrado[
        (df_filtrado["Match"].isin(partidos_sel))
        & (df_filtrado["Jornada"].isin(jornadas_sel))
    ].copy()

    if df_pass.empty:
        st.warning("No hay datos disponibles.")
        return

    df_long_pass = df_pass.melt(
        id_vars=["Match"],
        value_vars=[
            passing_metrics[m]
            for m in metrics_sel
            if passing_metrics[m] in df_pass.columns
        ],
        var_name="metric",
        value_name="value",
    )
    df_long_pass["metric_label"] = df_long_pass["metric"].map(
        {v: k for k, v in passing_metrics.items()}
    )

    fig = px.bar(
        df_long_pass,
        x="value",
        y="Match",
        color="metric_label",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE_CIBAO,
        template="plotly_dark",
        text_auto=".1f",
    )
    fig.update_traces(textfont=dict(size=11), textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=260,
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        xaxis_title="Precisión (%)",
        yaxis_title=None,
        legend_title="Tipo de pase",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# LAYOUT 1x2
# ==============================
col1, col2 = st.columns(2)
with col1:
    bloque_eficiencia_ataque(df_filtrado)
with col2:
    bloque_construccion_pases(df_filtrado)

# ==============================
# BLOQUE 1 — DEFENSA Y EFICIENCIA (Barras horizontales, 3 por defecto, máx 5)
# ==============================
def bloque_defensa_eficiencia(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Defensa y Eficiencia</h3>", unsafe_allow_html=True)
    st.caption(
        "Evalúa el rendimiento defensivo del Cibao FC mediante métricas como duelos ganados, intercepciones, recuperaciones, despejes y pérdidas por partido."
    )

    defense_metrics = {
        "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
        "Intercepciones por 90": "interceptions",
        "Recuperaciones por 90": "recoveries",
        "Despejes por 90": "clearances",
        "Pérdidas de balón por 90": "losses",
    }

    # 🔹 Solo 3 por defecto, máximo 5
    metrics_sel = st.multiselect(
        "Selecciona métricas defensivas (máx 5)",
        list(defense_metrics.keys()),
        default=[
            "Duelos defensivos ganados (%)",
            "Intercepciones por 90",
            "Recuperaciones por 90",
        ],
        max_selections=5,
        key="def_eff_metrics",
    )

    df_def = df_filtrado[
        (df_filtrado["Match"].isin(partidos_sel))
        & (df_filtrado["Jornada"].isin(jornadas_sel))
    ].copy()

    if df_def.empty:
        st.warning("No hay datos disponibles.")
        return

    df_long = df_def.melt(
        id_vars=["Match"],
        value_vars=[
            defense_metrics[m]
            for m in metrics_sel
            if defense_metrics[m] in df_def.columns
        ],
        var_name="metric",
        value_name="value",
    )
    df_long["metric_label"] = df_long["metric"].map(
        {v: k for k, v in defense_metrics.items()}
    )

    fig = px.bar(
        df_long,
        x="value",
        y="Match",
        color="metric_label",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE_CIBAO,
        template="plotly_dark",
        text_auto=".1f",
    )

    fig.update_traces(textfont=dict(size=11), textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=260,
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        xaxis_title="Valor",
        yaxis_title=None,
        legend_title="Métrica defensiva",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=30, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


# ==============================
# BLOQUE 2 — DISTRIBUCIÓN TÁCTICA (Barras agrupadas, estilo corporativo)
# ==============================
def bloque_distribucion_tactica(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Distribución Táctica — Presión y Recuperaciones</h3>", unsafe_allow_html=True)
    st.caption(
        "Analiza la distribución estimada de las pérdidas y recuperaciones del equipo según la altura del campo. "
        "Compara la presión ejercida y la efectividad de las recuperaciones entre zonas altas, medias y bajas."
    )

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

    df_view = df_filtrado[
        (df_filtrado["Jornada"].isin(jornadas_sel))
        & (df_filtrado["Match"].isin(partidos_sel))
    ].copy()

    if df_view.empty:
        st.warning("No hay datos disponibles para la selección actual.")
        return

    # === 📊 PRESIÓN POR ZONA ===
    df_pressure = df_view.melt(
        id_vars=["Match"],
        value_vars=list(pressure_metrics.values()),
        var_name="metric",
        value_name="value",
    )
    df_pressure["Zona"] = df_pressure["metric"].map({v: k for k, v in pressure_metrics.items()})

    fig_pressure = px.bar(
        df_pressure,
        x="value",
        y="Match",
        color="Zona",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE_CIBAO,
        template="plotly_dark",
        text_auto=".1f",
    )
    fig_pressure.update_traces(textfont=dict(size=11), textposition="outside", cliponaxis=False)
    fig_pressure.update_layout(
        height=230,
        title=dict(text="Presión — Por zonas del campo", font=dict(size=14, color=CIBAO_ORANGE)),
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        xaxis_title="Valor",
        yaxis_title=None,
        legend_title="Zona del campo",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=40, b=20),
    )

    st.plotly_chart(fig_pressure, use_container_width=True)

    # === 📊 RECUPERACIONES POR ZONA ===
    df_recovery = df_view.melt(
        id_vars=["Match"],
        value_vars=list(recovery_metrics.values()),
        var_name="metric",
        value_name="value",
    )
    df_recovery["Zona"] = df_recovery["metric"].map({v: k for k, v in recovery_metrics.items()})

    fig_recovery = px.bar(
        df_recovery,
        x="value",
        y="Match",
        color="Zona",
        orientation="h",
        barmode="group",
        color_discrete_sequence=PALETTE_CIBAO,
        template="plotly_dark",
        text_auto=".1f",
    )
    fig_recovery.update_traces(textfont=dict(size=11), textposition="outside", cliponaxis=False)
    fig_recovery.update_layout(
        height=230,
        title=dict(text="Recuperaciones — Por zonas del campo", font=dict(size=14, color=CIBAO_ORANGE)),
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        xaxis_title="Valor",
        yaxis_title=None,
        legend_title="Zona del campo",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=40, b=20),
    )

    st.plotly_chart(fig_recovery, use_container_width=True)


# ==============================
# LAYOUT 1×2 (Horizontal)
# ==============================
col1, col2 = st.columns(2)
with col1:
    bloque_defensa_eficiencia(df_filtrado)
with col2:
    bloque_distribucion_tactica(df_filtrado)

# ==============================
# ANÁLISIS COMPARATIVO — TABLAS CON ALTURA DINÁMICA Y PALETA CIBAO
# ==============================

import pandas as pd
import io
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

st.subheader("Análisis Comparativo por Bloques")
st.caption(
    "Visualiza y compara los indicadores clave del rendimiento colectivo en tres fases del juego: "
    "**ofensiva**, **construcción/pase** y **defensiva**. "
    "Cada bloque usa una escala cromática en tonos **naranja Cibao FC**, "
    "resaltando los valores más altos dentro de cada métrica."
)

# ==============================
# 📋 DICCIONARIO DE MÉTRICAS POR BLOQUE
# ==============================
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

# ==============================
# 🎨 PALETA NARANJA CIBAO — REGISTRADA GLOBALMENTE
# ==============================
CIBAO_ORANGE = LinearSegmentedColormap.from_list(
    "cibao_orange",
    ["#ff6600", "#ff7b00", "#ff9933", "#ffb84d", "#ffd699"]
)
matplotlib.colormaps.register(CIBAO_ORANGE, name="cibao_orange", force=True)

# ==============================
# 🔍 DATOS FILTRADOS Y LÍMITE DE FILAS
# ==============================
df_base = df_filtrado.copy()

if df_base.empty:
    st.info("No hay datos disponibles para los filtros seleccionados.")
else:
    df_base = df_base.sort_values("Date", ascending=False)
    partidos_sel = df_base["Match"].nunique()

    # Mostrar 3 filas por defecto, hasta 5 máximo
    if partidos_sel <= 3:
        df_base = df_base.head(3)
    else:
        df_base = df_base.head(min(partidos_sel, 5))

    st.caption(
        f"Mostrando los últimos {len(df_base)} partidos seleccionados "
        "(máximo 5 por visualización)."
    )

# ==============================
# ⚙️ FUNCIÓN DE TABLA CON FORMATO POR COLUMNA Y ALTURA AJUSTABLE
# ==============================
def build_table(df, metrics_dict, title):
    df_local = df[["Match"] + list(metrics_dict.values())].copy()
    df_local = df_local.rename(columns={v: k for k, v in metrics_dict.items()})
    df_local = df_local.round(2)

    st.markdown(f"### 🟧 {title}")
    styled_df = df_local.style
    for col in metrics_dict.keys():
        styled_df = styled_df.background_gradient(cmap="cibao_orange", subset=[col])

    styled_df = styled_df.set_properties(
        **{
            "text-align": "center",
            "font-size": "12px",
            "border-color": "#2b2b2b",
            "border-width": "1px",
            "border-style": "solid",
        }
    ).format(precision=2)

    # Altura dinámica: 45px por fila + margen superior
    height = max(180, len(df_local) * 45 + 80)
    st.dataframe(styled_df, use_container_width=True, height=height)
    return df_local

# ==============================
# 📊 BLOQUES (UNO DEBAJO DEL OTRO)
# ==============================
if not df_base.empty:
    st.divider()
    df_off = build_table(df_base, metrics_blocks["Ofensivas"], "Bloque Ofensivo")

    st.divider()
    df_pass = build_table(df_base, metrics_blocks["Construcción y Pase"], "Bloque Construcción y Pase")

    st.divider()
    df_def = build_table(df_base, metrics_blocks["Defensivas"], "Bloque Defensivo")

    # ==============================
    # 📥 DESCARGA EN EXCEL
    # ==============================
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_off.to_excel(writer, sheet_name="Ofensivo", index=False)
        df_pass.to_excel(writer, sheet_name="Construccion_Pase", index=False)
        df_def.to_excel(writer, sheet_name="Defensivo", index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Descargar análisis completo en Excel",
        data=buffer,
        file_name="analisis_completo_cibao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown(
        f"**Insight general:** Se muestran los últimos {len(df_base)} partidos disponibles según los filtros globales. "
        "Cada bloque utiliza una escala de tonos naranjas institucionales, resaltando los valores más altos "
        "de rendimiento dentro de cada columna."
    )



# =========================================================  COPA

# =========================================================
# 📊 ANÁLISIS DE MÉTRICAS EN COPA CONCACAF
# =========================================================

from src.data_processing.load_concacaf_matchstats_data import load_concacaf_matchstats_data
from src.utils.metrics_dictionary_concacaf import METRICS_CONCACAF, METRIC_GROUPS_CONCACAF

st.markdown(
    f"""
    <h1 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
    Análisis de Métricas — Copa Concacaf
    </h1>
    <p style='text-align:center; color:{CIBAO_GRAY}; font-size:17px;'>
    Exploración de métricas clave del Cibao FC durante la Copa Concacaf, incluyendo desempeño ofensivo, defensivo y de construcción.
    </p>
    """,
    unsafe_allow_html=True,
)

# ==============================
# 📂 Carga de datos de Copa
# ==============================

try:
    df_copa_merged, df_copa_cibao, df_copa_rivales = load_concacaf_matchstats_data()
except Exception as e:
    st.error(f"⚠️ Error al cargar los datos de Copa Concacaf: {e}")
    st.stop()

if df_copa_cibao.empty:
    st.warning("No hay registros de partidos de Copa Concacaf disponibles.")
else:
    # ==============================
    # 🧩 BLOQUE 0 — ANÁLISIS RÁPIDO CIBAO VS RIVAL (Copa)
    # ==============================
    st.markdown(
        f"""
        <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
        Comparativa Copa (Cibao vs Rival)
        </h2>
        <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
        Evalúa el rendimiento del Cibao FC frente a sus rivales en Copa Concacaf, considerando métricas ofensivas y defensivas clave.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1])

    team_options_copa = sorted(
        {
            str(t)
            for t in df_copa_cibao["rival"].dropna().unique()
            if str(t).strip().lower() != "cibao"
        }
    )

    if not team_options_copa:
        st.info("No hay rivales disponibles en el dataset de Copa Concacaf.")
    else:
        opponent_copa = col_sel1.selectbox("Selecciona rival de Copa", team_options_copa)

        metric_labels_copa = list(METRICS_CONCACAF.keys())

        # Valores por defecto
        x_default_copa = (
            metric_labels_copa.index("Goles") if "Goles" in metric_labels_copa else 0
        )
        y_default_copa = (
            metric_labels_copa.index("Goles Recibidos")
            if "Goles Recibidos" in metric_labels_copa
            else min(1, len(metric_labels_copa) - 1)
        )

        x_choice_copa = col_sel2.selectbox(
            "Métrica ofensiva (eje X)",
            metric_labels_copa,
            index=x_default_copa if metric_labels_copa else 0,
        )

        y_choice_copa = col_sel3.selectbox(
            "Métrica defensiva (eje Y)",
            metric_labels_copa,
            index=y_default_copa if metric_labels_copa else 0,
        )

        # Mapeo de nombres en español → columnas reales
        x_column_copa = METRICS_CONCACAF.get(x_choice_copa)
        y_column_copa = METRICS_CONCACAF.get(y_choice_copa)

        if x_column_copa is None or y_column_copa is None:
            st.error("No se encontró la métrica seleccionada en el dataset de Copa.")
        else:
            # --- ✨ Preparar dataset completo de Copa
            df_copa_adapter = df_copa_cibao.copy()

            df_copa_adapter["Team"] = df_copa_adapter["team"]
            df_copa_adapter["Opponent"] = df_copa_adapter.apply(
                lambda r: r["away_team"]
                if r["team"] == r["home_team"]
                else r["home_team"],
                axis=1,
            )
            df_copa_adapter["Competition"] = "Copa Concacaf"
            df_copa_adapter["Date"] = pd.to_datetime(df_copa_adapter["match_date"])
            df_copa_adapter["Match"] = df_copa_adapter.apply(
                lambda r: f"{r['home_team']} vs {r['away_team']}", axis=1
            )
            if "Jornada" not in df_copa_adapter.columns:
                df_copa_adapter["Jornada"] = df_copa_adapter.get("stage", "Copa")

            for col_num in [x_column_copa, y_column_copa]:
                if col_num in df_copa_adapter.columns:
                    df_copa_adapter[col_num] = (
                        pd.to_numeric(df_copa_adapter[col_num], errors="coerce")
                        .fillna(0)
                    )

            df_copa_adapter = df_copa_adapter.fillna(0)
            df_copa_view = df_copa_adapter.copy()

            if df_copa_view.empty:
                st.info("No hay registros disponibles para el análisis de Copa.")
            else:
                try:
                    fig_copa, resumen_copa, _ = make_team_scatter(
                        df_copa_view,
                        primary_team="Cibao",
                        opponent=opponent_copa,
                        x_metric=x_column_copa,
                        y_metric=y_column_copa,
                        x_label=x_choice_copa,
                        y_label=y_choice_copa,
                        title=f"Copa Concacaf — {x_choice_copa} vs {y_choice_copa}",
                        filters=None,
                    )

                    # 🚫 Eliminar anotaciones superiores automáticas (texto que se superpone)
                    fig_copa.layout.annotations = [
                        ann for ann in fig_copa.layout.annotations if ann.yref != "paper" or ann.y < 1
                    ]

                    # Ajuste de márgenes para mantener buen espaciado
                    fig_copa.update_layout(
                        margin=dict(t=100, b=80, l=60, r=40),
                        title_pad=dict(t=60),
                        title_font=dict(size=20),
                    )

                    st.plotly_chart(
                        fig_copa,
                        use_container_width=True,
                        config={"displayModeBar": True},
                    )

                    # ✅ Mostrar solo resumen inferior
                    if resumen_copa:
                        st.markdown("---")
                        st.caption(f"**Resumen:** {resumen_copa}")

                except Exception as e:
                    st.warning(
                        f"No se pudo usar make_team_scatter ({e}). Se muestra un scatter básico."
                    )
                    import plotly.express as px
                    fig_basic = px.scatter(
                        df_copa_view,
                        x=x_column_copa,
                        y=y_column_copa,
                        color="Team",
                        hover_data=["Match", "Date"],
                        title=f"Copa Concacaf — {x_choice_copa} vs {y_choice_copa}",
                        template="plotly_dark",
                    )
                    fig_basic.update_layout(
                        margin=dict(t=100, b=80, l=60, r=40),
                        title_pad=dict(t=60),
                        title_font=dict(size=20),
                    )
                    st.plotly_chart(fig_basic, use_container_width=True)


import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def _ensure_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def _map_metrics(names):
    """Devuelve lista de columnas reales a partir de nombres del diccionario."""
    cols = []
    for n in names:
        col = METRICS_CONCACAF.get(n)
        if col:
            cols.append(col)
    return cols


# =========================================================
# 🔧 Utilidades para bloques de Copa (usar una sola vez)
# =========================================================
import numpy as np
import plotly.graph_objects as go

def _ensure_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)
    return df

def _dedup_names_by_column(metric_names, mapping):
    seen = set()
    result = []
    for n in metric_names:
        col = mapping.get(n)
        if col and col not in seen:
            seen.add(col)
            result.append((n, col))
    return result

# =========================================================
# 🧩 BLOQUES 1–4 · COMPARATIVA CIBAO VS RIVAL — COPA CONCACAF
# =========================================================
st.markdown(
    f"""
    <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
    Comparativa de Métricas — Copa Concacaf (Cibao vs Rival)
    </h2>
    <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
    Compara el rendimiento promedio del Cibao FC frente a un rival seleccionado
    en cada grupo de métricas: ataque, pases, defensa y balón parado.
    </p>
    """,
    unsafe_allow_html=True,
)

# --- Selección de rival única ---
team_options_copa = sorted(
    {
        str(t)
        for t in df_copa_cibao["rival"].dropna().unique()
        if str(t).strip().lower() != "cibao"
    }
)
if not team_options_copa:
    st.warning("No hay rivales disponibles en el dataset de Copa Concacaf.")
    st.stop()

col_sel = st.columns([1])
opponent_choice = col_sel[0].selectbox(
    "Selecciona rival de Copa",
    team_options_copa,
    key="copa_metrics_select",
)

# =========================================================
# 🧮 Función principal comparativa Cibao vs Rival
# =========================================================
def make_comparison_bar(group_name, df, mapping_dict, group_dict, rival_name):
    group_metrics = group_dict.get(group_name, [])
    pairs = _dedup_names_by_column(group_metrics, mapping_dict)
    cols = [c for _, c in pairs]
    df = _ensure_numeric(df.copy(), cols)

    cibao_df = df[df["team"].str.contains("Cibao", case=False, na=False)]
    rival_df = df[df["team"].str.contains(rival_name, case=False, na=False)]

    cibao_means, rival_means, labels = [], [], []
    for disp, col in pairs:
        labels.append(disp)
        cibao_means.append(float(cibao_df[col].mean()) if col in cibao_df.columns else 0)
        rival_means.append(float(rival_df[col].mean()) if col in rival_df.columns else 0)

    color_cibao = "#FF8C00"  # naranja sólido (seguro)
    color_rival = "#FFA500"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=cibao_means, name="Cibao", marker_color=color_cibao
    ))
    fig.add_trace(go.Bar(
        x=labels, y=rival_means, name=rival_name, marker_color=color_rival
    ))

    fig.update_layout(
        title=f"{group_name} — Promedio por partido (Cibao vs {rival_name})",
        barmode="group",
        template="plotly_dark",
        height=450,
        margin=dict(t=70, b=60, l=60, r=40),
        xaxis_title="Métrica",
        yaxis_title="Promedio por partido",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )
    return fig

# =========================================================
# 📊 FILA 1: ATAQUE + PASES
# =========================================================
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        make_comparison_bar("Ataque", df_copa_cibao, METRICS_CONCACAF, METRIC_GROUPS_CONCACAF, opponent_choice),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        make_comparison_bar("Pases", df_copa_cibao, METRICS_CONCACAF, METRIC_GROUPS_CONCACAF, opponent_choice),
        use_container_width=True,
    )

# =========================================================
# 📊 FILA 2: DEFENSIVO + SET PIECES
# =========================================================
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(
        make_comparison_bar("Defensivo", df_copa_cibao, METRICS_CONCACAF, METRIC_GROUPS_CONCACAF, opponent_choice),
        use_container_width=True,
    )
with col4:
    st.plotly_chart(
        make_comparison_bar("Set Pieces", df_copa_cibao, METRICS_CONCACAF, METRIC_GROUPS_CONCACAF, opponent_choice),
        use_container_width=True,
    )




















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

