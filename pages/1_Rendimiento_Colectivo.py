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
# BLOQUE 1 — DEFENSA Y EFICIENCIA (Horizontal)
# ==============================
def bloque_defensa_eficiencia(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Defensa y Eficiencia</h3>", unsafe_allow_html=True)
    st.caption(
        "Evalúa la efectividad defensiva del Cibao FC analizando métricas como duelos ganados, intercepciones, recuperaciones, despejes y pérdidas de balón."
    )

    defense_metrics = {
        "Duelos defensivos ganados (%)": "defensive_duels_won_percent",
        "Intercepciones por 90": "interceptions",
        "Recuperaciones por 90": "recoveries",
        "Despejes por 90": "clearances",
        "Pérdidas de balón por 90": "losses",
        "Duelos aéreos ganados (%)": "aerial_duels_won_percent",
        "Éxito en entradas (%)": "sliding_tackles_successful_percent",
    }

    metrics_sel = st.multiselect(
        "Selecciona métricas defensivas (máx 5)",
        list(defense_metrics.keys()),
        default=[
            "Duelos defensivos ganados (%)",
            "Intercepciones por 90",
            "Recuperaciones por 90",
            "Despejes por 90",
            "Pérdidas de balón por 90",
        ],
        max_selections=5,
        key="def_metrics",
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
# BLOQUE 2 — DISTRIBUCIÓN TÁCTICA (Horizontal)
# ==============================
def bloque_distribucion_tactica(df_filtrado):
    st.markdown("<h3 style='text-align:center;'>Distribución Táctica — Presión y Recuperaciones</h3>", unsafe_allow_html=True)
    st.caption(
        "Analiza la intensidad de la presión y la frecuencia de recuperaciones en distintas zonas del campo, visualizando el comportamiento táctico del equipo."
    )

    tactical_metrics = {
        "Presión alta (estimada)": "losses_high",
        "Presión media (estimada)": "losses_medium",
        "Presión baja (estimada)": "losses_low",
        "Recuperaciones altas por 90": "recoveries_high",
        "Recuperaciones medias por 90": "recoveries_medium",
        "Recuperaciones bajas por 90": "recoveries_low",
    }

    metrics_sel = st.multiselect(
        "Selecciona métricas tácticas (máx 5)",
        list(tactical_metrics.keys()),
        default=[
            "Presión alta (estimada)",
            "Presión media (estimada)",
            "Recuperaciones altas por 90",
            "Recuperaciones medias por 90",
            "Recuperaciones bajas por 90",
        ],
        max_selections=5,
        key="tact_metrics",
    )

    df_tact = df_filtrado[
        (df_filtrado["Match"].isin(partidos_sel))
        & (df_filtrado["Jornada"].isin(jornadas_sel))
    ].copy()

    if df_tact.empty:
        st.warning("No hay datos disponibles.")
        return

    df_long_tact = df_tact.melt(
        id_vars=["Match"],
        value_vars=[
            tactical_metrics[m]
            for m in metrics_sel
            if tactical_metrics[m] in df_tact.columns
        ],
        var_name="metric",
        value_name="value",
    )
    df_long_tact["metric_label"] = df_long_tact["metric"].map(
        {v: k for k, v in tactical_metrics.items()}
    )

    fig = px.bar(
        df_long_tact,
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
        legend_title="Métrica táctica",
        legend=dict(font=dict(size=11)),
        bargap=0.25,
        margin=dict(l=40, r=30, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ==============================
# LAYOUT 1x2 (Horizontal)
# ==============================
col1, col2 = st.columns(2)
with col1:
    bloque_defensa_eficiencia(df_filtrado)
with col2:
    bloque_distribucion_tactica(df_filtrado)



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

