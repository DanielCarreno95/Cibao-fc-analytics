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

# ============================================================
# 🔶 FUNCIÓN: Bloque — EFICIENCIA Y ATAQUE (Tab 1)
# ============================================================

def bloque_eficiencia_ataque(df_filtrado, partidos_sel, jornadas_sel):
    """
    Tab 1: Eficiencia y Ataque
    Muestra varios gráficos:
      1) Goles vs xG por partido
      2) Volumen de disparos (totales, al arco, fuera, bloqueados)
      3) Acciones de profundidad (contraataques y entradas al área por 90)
    """

    st.markdown(
        "<h3 style='text-align:center; color:#FF8C00;'>Eficiencia y Ataque</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Lectura rápida del rendimiento ofensivo del Cibao FC: conversión de goles, "
        "calidad de las ocasiones (xG), volumen y precisión de disparos y agresividad "
        "en ataques rápidos y entradas al área."
    )

    # -------- PALETA ----------
    try:
        palette = PALETTE_CIBAO
    except NameError:
        palette = ["#FF8C00", "#FFA64D", "#F97316", "#FBBF77"]

    # -------- FILTRADO BASE ----------
    df_off = df_filtrado.copy()
    df_off = df_off[
        (df_off["Match"].isin(partidos_sel)) &
        (df_off["Jornada"].isin(jornadas_sel))
    ]

    if df_off.empty:
        st.warning("No hay datos disponibles para estas métricas.")
        return

    # Ordenar partidos por fecha si existe
    if "Date" in df_off.columns:
        df_off = df_off.sort_values("Date")
    df_off["Match_label"] = df_off["Match"]

    # ======================================================
    # 1) GOLES vs xG — Comparación por partido
    # ======================================================
    col1, col2 = st.columns(2)

    with col1:
        cols_gxg = [c for c in ["goals", "xg"] if c in df_off.columns]
        if len(cols_gxg) == 2:
            df_gxg = df_off[["Match_label", "goals", "xg"]].melt(
                id_vars="Match_label",
                value_vars=["goals", "xg"],
                var_name="Métrica",
                value_name="Valor",
            )

            df_gxg["Métrica"] = df_gxg["Métrica"].map(
                {"goals": "Goles por partido", "xg": "xG (Goles esperados)"}
            )

            fig_gxg = px.bar(
                df_gxg,
                x="Match_label",
                y="Valor",
                color="Métrica",
                barmode="group",
                color_discrete_sequence=palette[:2],
                template="plotly_dark",
                text_auto=".2f",
            )
            fig_gxg.update_layout(
                title="Goles vs xG por partido",
                xaxis_title="Partido",
                yaxis_title="Goles / xG",
                plot_bgcolor="#000000",
                paper_bgcolor="#000000",
                font=dict(color="#D3D3D3", size=11),
                legend_title=None,
                margin=dict(l=20, r=10, t=40, b=40),
                height=360,
            )
            st.plotly_chart(fig_gxg, use_container_width=True)
        else:
            st.info("No se encontraron columnas de goles/xG para este bloque.")

    # ======================================================
    # 2) VOLUMEN DE DISPAROS — Totales, al arco, fuera, bloqueados
    # ======================================================
    with col2:
        shot_cols = {
            "Disparos Totales": "totalScoringAtt",
            "Disparos al Arco": "ontargetScoringAtt",
            "Disparos Fuera": "shotOffTarget",
            "Disparos Bloqueados": "blockedScoringAtt",
        }

        cols_presentes = {
            nombre: col for nombre, col in shot_cols.items() if col in df_off.columns
        }

        if cols_presentes:
            df_shots = df_off[["Match_label"] + list(cols_presentes.values())].melt(
                id_vars="Match_label",
                value_vars=list(cols_presentes.values()),
                var_name="metric",
                value_name="Valor",
            )

            inv_map = {v: k for k, v in cols_presentes.items()}
            df_shots["Métrica"] = df_shots["metric"].map(inv_map)

            fig_shots = px.bar(
                df_shots,
                x="Match_label",
                y="Valor",
                color="Métrica",
                barmode="group",
                template="plotly_dark",
                color_discrete_sequence=palette,
                text_auto=".1f",
            )
            fig_shots.update_layout(
                title="Volumen de disparos por partido",
                xaxis_title="Partido",
                yaxis_title="Número de disparos",
                plot_bgcolor="#000000",
                paper_bgcolor="#000000",
                font=dict(color="#D3D3D3", size=11),
                legend_title=None,
                margin=dict(l=20, r=10, t=40, b=40),
                height=360,
            )
            st.plotly_chart(fig_shots, use_container_width=True)
        else:
            st.info("No se encontraron columnas de disparos para este bloque.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================
    # 3) ACCIONES DE PROFUNDIDAD — Contraataques y entradas al área
    # ======================================================
    depth_cols = {
        "Contraataques por 90": "counter_attacks",
        "Entradas al área por 90": "penalty_area_entries",
    }

    cols_depth_presentes = {
        nombre: col for nombre, col in depth_cols.items() if col in df_off.columns
    }

    if cols_depth_presentes:
        df_depth = df_off[["Match_label"] + list(cols_depth_presentes.values())].melt(
            id_vars="Match_label",
            value_vars=list(cols_depth_presentes.values()),
            var_name="metric",
            value_name="Valor",
        )

        inv_depth = {v: k for k, v in cols_depth_presentes.items()}
        df_depth["Métrica"] = df_depth["metric"].map(inv_depth)

        fig_depth = px.bar(
            df_depth,
            x="Valor",
            y="Match_label",
            color="Métrica",
            orientation="h",
            barmode="group",
            template="plotly_dark",
            color_discrete_sequence=palette[:2],
            text_auto=".2f",
        )
        fig_depth.update_layout(
            title="Acciones de profundidad (por 90 minutos)",
            xaxis_title="Valor por 90",
            yaxis_title="Partido",
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            font=dict(color="#D3D3D3", size=11),
            legend_title=None,
            margin=dict(l=80, r=20, t=40, b=40),
            height=360,
        )
        st.plotly_chart(fig_depth, use_container_width=True)
    else:
        st.info("No se encontraron métricas de contraataques/entradas al área.")


# ============================================================
# 🔶 CSS PARA PESTAÑAS TIPO CHROME
# ============================================================

tabs_css = """
<style>

div[data-baseweb="tab-list"] {
    gap: 6px !important;
}

div[role="tab"] {
    background-color: #111 !important;
    padding: 10px 20px !important;
    border-radius: 8px 8px 0 0 !important;
    color: #ccc !important;
    border: 1px solid #333 !important;
    font-weight: 600 !important;
    cursor: pointer !important;
}

div[role="tab"][aria-selected="true"] {
    background-color: #ff7b00 !important;
    color: black !important;
    border-bottom: 1px solid #ff7b00 !important;
}

div[role="tabpanel"] {
    border: 1px solid #333 !important;
    padding: 20px !important;
    border-radius: 0 8px 8px 8px !important;
    background-color: #0a0a0a !important;
}

</style>
"""

st.markdown(tabs_css, unsafe_allow_html=True)


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
    bloque_eficiencia_ataque(df_filtrado, partidos_sel, jornadas_sel)


with tab2:
    st.info("🔧 Contenido de Construcción y Pases — pendiente por definir.")


with tab3:
    st.info("🔧 Contenido de Defensa y Eficiencia — pendiente por definir.")


with tab4:
    st.info("🔧 Distribución táctica — pendiente por definir.")


with tab5:
    st.info("📊 Tablas comparativas — pendiente por definir.")
