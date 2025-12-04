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
    
    # Crear opciones combinadas "Jornada - Partido"
    if not df_cibao.empty and "Jornada" in df_cibao.columns and "Match" in df_cibao.columns:
        df_cibao_sorted = df_cibao.sort_values("Date")
        opciones_partidos = []
        for _, row in df_cibao_sorted.iterrows():
            jornada = row.get("Jornada", "")
            partido = row.get("Match", "")
            if pd.notna(jornada) and pd.notna(partido):
                opciones_partidos.append(f"J{int(jornada)} - {partido}")
        
        # Eliminar duplicados manteniendo orden
        opciones_partidos = list(dict.fromkeys(opciones_partidos))
        
        # Seleccionar últimos 3 por defecto
        default_selection = opciones_partidos[-3:] if len(opciones_partidos) >= 3 else opciones_partidos
    else:
        opciones_partidos = []
        default_selection = []
    
    # Inicializar estado
    if "partidos_seleccionados" not in st.session_state:
        st.session_state["partidos_seleccionados"] = default_selection
    
    partidos_seleccionados = st.multiselect(
        "Selecciona Partidos (máx 5)",
        options=opciones_partidos,
        default=st.session_state["partidos_seleccionados"],
        key="sidebar_partidos_combinados",
        max_selections=5,
        help="Formato: Jornada - Partido"
    )
    
    # --- Botón para limpiar filtros ---
    if st.button("🔄 Borrar filtros", use_container_width=True):
        st.session_state["partidos_seleccionados"] = default_selection
        st.session_state["sidebar_partidos_combinados"] = default_selection
        st.toast("Filtros restablecidos a los últimos 3 partidos ✅", icon="🔁")
        st.rerun()
    
    # ===============================================
    # 📊 COMPARACIÓN CON PROMEDIO LIGA
    # ===============================================
    st.markdown("<hr style='margin:20px 0; opacity:0.3;'>", unsafe_allow_html=True)
    st.subheader("Comparación")
    
    # Checkbox para promedio de liga
    mostrar_promedio_liga = st.checkbox(
        "Mostrar Promedio Liga",
        value=True,
        key="mostrar_promedio_liga",
        help="Compara Cibao con el promedio de todos los equipos de la liga"
    )

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

if partidos_seleccionados:
    # Extraer nombres de partidos de las selecciones "J# - Partido"
    partidos_nombres = [p.split(" - ", 1)[1] if " - " in p else p for p in partidos_seleccionados]
    df_filtrado = df_filtrado[df_filtrado["Match"].isin(partidos_nombres)]

# Si no hay selección válida, usa últimos 3 por defecto
if df_filtrado.empty and not df_cibao.empty:
    # Usar últimos 3 partidos
    ultimos_partidos = df_cibao.sort_values("Date").tail(3)["Match"].unique().tolist()
    df_filtrado = df_cibao[df_cibao["Match"].isin(ultimos_partidos)]

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
CIBAO_ORANGE = "#FF8C00"         # Naranja principal - Cibao FC
CIBAO_ORANGE_LIGHT = "#FFC966"   # Naranja dorado claro - Promedio Liga
CIBAO_WHITE = "#E8E8E8"          # Gris claro/blanco - Equipo 1
CIBAO_GRAY_MED = "#808080"       # Gris medio - Equipo 2
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
    
    columnas = [v for v in mapping.values() if v in df_filtrado.columns]
    etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if len(columnas) == 0:
        st.warning(f"No hay métricas disponibles para: {nombre_grupo}")
        return
    
    # ===== CALCULAR PROMEDIO DE CIBAO (con filtros) =====
    df_cibao_filtered = df_filtrado.copy()
    cibao_means = df_cibao_filtered[columnas].mean()
    
    # ===== PREPARAR DATOS PARA COMPARACIÓN =====
    comparison_data = []
    
    # Agregar Cibao
    for col in columnas:
        comparison_data.append({
            "label": etiquetas[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    # ===== PROMEDIO LIGA (si está activado) =====
    if mostrar_promedio_liga and not df_liga_mayor.empty:
        # Filtrar equipos excluyendo Cibao
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        # Calcular promedio para cada métrica
        for col in columnas:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": etiquetas[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    # ===== CREAR DATAFRAME PARA PLOTLY =====
    df_plot = pd.DataFrame(comparison_data)
    
    # Ordenar por valor de Cibao (para mantener consistencia visual)
    cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=True)["label"].tolist()
    df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
    df_plot = df_plot.sort_values("label")
    
    # ===== MAPA DE COLORES =====
    color_map = {
        "Cibao FC": CIBAO_ORANGE,
        "Promedio Liga": CIBAO_ORANGE_LIGHT,
    }
    
    # ===== CREAR GRÁFICO =====
    fig = px.bar(
        df_plot,
        x="valor",
        y="label",
        color="Equipo",
        orientation="h",
        text_auto=".2f",
        color_discrete_map=color_map,
        barmode="group",
    )
    
    fig.update_layout(
        height=350,
        template="plotly_dark",
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        title_x=0.5,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(size=10)
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== CONCLUSIONES TÁCTICAS =====
    cibao_data = df_plot[df_plot["Equipo"] == "Cibao FC"].copy()
    if not cibao_data.empty:
        max_row = cibao_data.loc[cibao_data["valor"].idxmax()]
        min_row = cibao_data.loc[cibao_data["valor"].idxmin()]
        
        conclusion = f"""
        <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE}; margin-top:-8px; margin-bottom:25px;'>
        <b>Conclusiones tácticas</b><br><br>
        
        • <b>Punto fuerte:</b> El equipo muestra mayor impacto en <b>{max_row['label']}</b> ({max_row['valor']:.2f}),
          acción que está contribuyendo directamente al modelo ofensivo.<br><br>
        
        • <b>Área con menor incidencia:</b> El valor más bajo corresponde a <b>{min_row['label']}</b> ({min_row['valor']:.2f}),
          indicador de un comportamiento aún mejorable dentro de la estructura ofensiva.<br><br>
        </div>
        """
        
        st.markdown(conclusion, unsafe_allow_html=True)


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
        
        columnas = [v for v in mapping.values() if v in df_filtrado.columns]
        etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
        
        if len(columnas) == 0:
            st.warning(f"No hay métricas disponibles para: {nombre_grupo}")
            return
        
        # ===== CALCULAR PROMEDIO DE CIBAO (con filtros) =====
        df_cibao_filtered = df_filtrado.copy()
        cibao_means = df_cibao_filtered[columnas].mean()
        
        # ===== PREPARAR DATOS PARA COMPARACIÓN =====
        comparison_data = []
        
        # Agregar Cibao
        for col in columnas:
            comparison_data.append({
                "label": etiquetas[col],
                "Equipo": "Cibao FC",
                "valor": cibao_means[col]
            })
        
        # ===== PROMEDIO LIGA (si está activado) =====
        if mostrar_promedio_liga and not df_liga_mayor.empty:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
            
            for col in columnas:
                if col in df_liga_sin_cibao.columns:
                    liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                    comparison_data.append({
                        "label": etiquetas[col],
                        "Equipo": "Promedio Liga",
                        "valor": liga_val if not pd.isna(liga_val) else 0
                    })
        
        # ===== CREAR DATAFRAME PARA PLOTLY =====
        df_plot = pd.DataFrame(comparison_data)
        
        # Ordenar por valor de Cibao
        cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=False)["label"].tolist()
        df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
        df_plot = df_plot.sort_values("label")
        
        # ===== MAPA DE COLORES =====
        color_map = {
            "Cibao FC": CIBAO_ORANGE,
            "Promedio Liga": CIBAO_ORANGE_LIGHT,
        }
        
        # ===== CREAR GRÁFICO =====
        fig = px.bar(
            df_plot,
            x="label",
            y="valor",
            color="Equipo",
            orientation="v",
            text_auto=".2f",
            color_discrete_map=color_map,
            barmode="group",
        )
        
        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#111",
            paper_bgcolor="#111",
            font=dict(color="#D3D3D3", size=12),
            title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color="#FF8C00")),
            title_x=0.5,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(tickangle=-35),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)",
                font=dict(size=10)
            ),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # -------- CONCLUSIONES TÁCTICAS --------
        cibao_data = df_plot[df_plot["Equipo"] == "Cibao FC"].copy()
        if not cibao_data.empty:
            max_row = cibao_data.loc[cibao_data["valor"].idxmax()]
            min_row = cibao_data.loc[cibao_data["valor"].idxmin()]
            
            conclusion = f"""
            <div style='background:#111; padding:12px; border-left:3px solid #FF8C00; margin-top:-8px; margin-bottom:25px;'>
            <b>Conclusiones tácticas</b><br><br>
            
            • <b>Fortaleza estructural:</b> El equipo muestra mayor fiabilidad en <b>{max_row['label']}</b> ({max_row['valor']:.2f}), indicador de estabilidad en la fase de construcción.<br><br>
            
            • <b>Área por optimizar:</b> La métrica con menor incidencia es <b>{min_row['label']}</b> ({min_row['valor']:.2f}), aspecto donde aumentar la claridad puede mejorar la fluidez asociativa.<br><br>
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

        # Valor de Cibao
        value_cibao = df_filtrado[col].mean()
        
        # Valor promedio de liga (si está activado)
        value_liga = None
        if mostrar_promedio_liga and not df_liga_mayor.empty and col in df_liga_mayor.columns:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
            value_liga = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()

        fig = go.Figure()

        # Gauge principal con valor de Cibao
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=value_cibao,
            title={'text': f"<b>{label}</b><br><span style='font-size:12px; color:#FFC966'>Cibao FC</span>", 
                   'font': {'color': '#FF8C00', 'size': 18}},
            number={'font': {'color': '#FF8C00', 'size': 40}},
            gauge={
                'axis': {'range': [0, max(40, value_cibao * 1.5)]},
                'bar': {'color': "#FF8C00", 'thickness': 0.7},
                'bgcolor': "#333",
                'borderwidth': 1,
                'bordercolor': "#555",
                'steps': [
                    {'range': [0, max(40, value_cibao * 1.5)], 'color': "#1a1a1a"}
                ],
                # Agregar threshold para promedio liga si existe
                'threshold': {
                    'line': {'color': "#FFC966", 'width': 3},
                    'thickness': 0.8,
                    'value': value_liga if value_liga and not pd.isna(value_liga) else 0
                } if value_liga and not pd.isna(value_liga) else None
            },
        ))

        fig.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=80, b=20),
            paper_bgcolor="#111",
            font=dict(color="#D3D3D3")
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # Conclusión con comparación
        if value_liga and not pd.isna(value_liga):
            diferencia = value_cibao - value_liga
            comparacion_text = f"superior en {abs(diferencia):.2f}m" if diferencia > 0 else f"inferior en {abs(diferencia):.2f}m"
            
            st.markdown(f"""
            <div style='background:#111; padding:12px; border-left:3px solid #FF8C00; margin-top:-5px; margin-bottom:25px;'>
            <b>Conclusión táctica</b><br><br>
            • La <b>longitud media de pase de Cibao ({value_cibao:.2f} m)</b> es {comparacion_text} al promedio de la liga ({value_liga:.2f} m).<br><br>
            • Este valor describe el perfil del equipo en cuanto a riesgo y distancia de circulación, 
              sirviendo como referencia para calibrar la intención de progresar por combinación o por envío largo.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background:#111; padding:12px; border-left:3px solid #FF8C00; margin-top:-5px; margin-bottom:25px;'>
            <b>Conclusión táctica</b><br><br>
            • La <b>longitud media de pase ({value_cibao:.2f} m)</b> describe el perfil del equipo en cuanto a riesgo y distancia de circulación. 
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

        cols = [v for v in mapping.values() if v in df_filtrado.columns]
        labels = {v: k for k, v in mapping.items() if v in df_filtrado.columns}

        if not cols:
            st.warning(f"No hay datos para {nombre}")
            return

        # Calcular promedio de Cibao
        cibao_means = df_filtrado[cols].mean()
        
        # Preparar datos para comparación
        comparison_data = []
        
        # Agregar Cibao
        for col in cols:
            comparison_data.append({
                "label": labels[col],
                "Equipo": "Cibao FC",
                "valor": cibao_means[col]
            })
        
        # Promedio Liga (si está activado)
        if mostrar_promedio_liga and not df_liga_mayor.empty:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
            
            for col in cols:
                if col in df_liga_sin_cibao.columns:
                    liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                    comparison_data.append({
                        "label": labels[col],
                        "Equipo": "Promedio Liga",
                        "valor": liga_val if not pd.isna(liga_val) else 0
                    })
        
        # Crear dataframe
        df_plot = pd.DataFrame(comparison_data)
        
        # Ordenar por valor de Cibao
        cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=True)["label"].tolist()
        df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
        df_plot = df_plot.sort_values("label")
        
        # Mapa de colores
        color_map = {
            "Cibao FC": CIBAO_ORANGE,
            "Promedio Liga": CIBAO_ORANGE_LIGHT,
        }

        fig = px.bar(
            df_plot,
            x="valor",
            y="label",
            color="Equipo",
            orientation="h",
            text_auto=".2f",
            color_discrete_map=color_map,
            barmode="group",
        )

        fig.update_layout(
            height=350,
            template="plotly_dark",
            plot_bgcolor=CIBAO_BLACK,
            paper_bgcolor=CIBAO_BLACK,
            title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            margin=dict(l=30, r=20, t=50, b=20),
            font=dict(color=CIBAO_GRAY),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)",
                font=dict(size=10)
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Conclusiones
        cibao_data = df_plot[df_plot["Equipo"] == "Cibao FC"].copy()
        if not cibao_data.empty:
            max_row = cibao_data.loc[cibao_data["valor"].idxmax()]
            min_row = cibao_data.loc[cibao_data["valor"].idxmin()]

            st.markdown(f"""
            <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px;margin-bottom:25px;'>
            <b>Conclusiones tácticas</b><br><br>
            • <b>Comportamiento destacado:</b> Mayor solvencia en <b>{max_row['label']}</b> ({max_row['valor']:.2f}).<br><br>
            • <b>Aspecto mejorable:</b> Valor más bajo en <b>{min_row['label']}</b> ({min_row['valor']:.2f}).
            </div>
            """, unsafe_allow_html=True)

    # --- BARRAS VERTICALES ---
    def plot_vertical(nombre, mapping):

        cols = [v for v in mapping.values() if v in df_filtrado.columns]
        labels = {v: k for k, v in mapping.items() if v in df_filtrado.columns}

        if not cols:
            st.warning(f"No hay datos para {nombre}")
            return

        # Calcular promedio de Cibao
        cibao_means = df_filtrado[cols].mean()
        
        # Preparar datos para comparación
        comparison_data = []
        
        # Agregar Cibao
        for col in cols:
            comparison_data.append({
                "label": labels[col],
                "Equipo": "Cibao FC",
                "valor": cibao_means[col]
            })
        
        # Promedio Liga (si está activado)
        if mostrar_promedio_liga and not df_liga_mayor.empty:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
            
            for col in cols:
                if col in df_liga_sin_cibao.columns:
                    liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                    comparison_data.append({
                        "label": labels[col],
                        "Equipo": "Promedio Liga",
                        "valor": liga_val if not pd.isna(liga_val) else 0
                    })
        
        # Crear dataframe
        df_plot = pd.DataFrame(comparison_data)
        
        # Ordenar por valor de Cibao
        cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=False)["label"].tolist()
        df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
        df_plot = df_plot.sort_values("label")
        
        # Mapa de colores
        color_map = {
            "Cibao FC": CIBAO_ORANGE,
            "Promedio Liga": CIBAO_ORANGE_LIGHT,
        }

        fig = px.bar(
            df_plot,
            x="label",
            y="valor",
            color="Equipo",
            text_auto=".2f",
            color_discrete_map=color_map,
            barmode="group",
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor=CIBAO_BLACK,
            paper_bgcolor=CIBAO_BLACK,
            title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(color=CIBAO_GRAY),
            xaxis=dict(tickangle=-30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)",
                font=dict(size=10)
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Conclusiones
        cibao_data = df_plot[df_plot["Equipo"] == "Cibao FC"].copy()
        if not cibao_data.empty:
            max_row = cibao_data.loc[cibao_data["valor"].idxmax()]
            min_row = cibao_data.loc[cibao_data["valor"].idxmin()]

            st.markdown(f"""
            <div style='background:#111;padding:12px;border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px;margin-bottom:25px;'>
            <b>Conclusiones tácticas</b><br><br>
            • <b>Mayor influencia:</b> <b>{max_row['label']}</b> ({max_row['valor']:.2f}).<br><br>
            • <b>Zona con margen de mejora:</b> <b>{min_row['label']}</b> ({min_row['valor']:.2f}).
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
# EXPORTACIÓN DIRECTA A PDF - CON GRÁFICOS VISIBLES
# ===========================================

import io
from datetime import datetime
import base64
import requests
import plotly.io as pio
import tempfile

# ===========================================
# CAPTURAR GRÁFICO COMO BASE64
# ===========================================

def grafico_a_base64(fig, width=1200, height=600):
    """Captura gráfico de Plotly y lo convierte a base64."""
    try:
        img_bytes = pio.to_image(fig, format='png', width=width, height=height, scale=2, engine='kaleido')
        return base64.b64encode(img_bytes).decode()
    except Exception as e:
        return None

# ===========================================
# GENERAR SECCIÓN CON GRÁFICOS COMO IMÁGENES
# ===========================================

def generar_seccion_html_con_imagenes(titulo, grupos, df_filtrado, df_liga_mayor, mostrar_prom, orientacion):
    """Genera HTML con gráficos capturados como imágenes base64."""
    
    html = f'<div class="page"><h2 class="section-title">{titulo}</h2><div class="grid-2-cols">'
    
    for nombre_grupo, metricas in grupos.items():
        columnas = [v for v in metricas.values() if v in df_filtrado.columns]
        if not columnas:
            continue
        
        etiquetas = {v: k for k, v in metricas.items() if v in df_filtrado.columns}
        cibao_means = df_filtrado[columnas].mean()
        
        data = []
        for col in columnas:
            data.append({"label": etiquetas[col], "Equipo": "Cibao FC", "valor": cibao_means[col]})
        
        if mostrar_prom and not df_liga_mayor.empty:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
            for col in columnas:
                if col in df_liga_sin_cibao.columns:
                    liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                    data.append({"label": etiquetas[col], "Equipo": "Promedio Liga", "valor": liga_val if not pd.isna(liga_val) else 0})
        
        df_plot = pd.DataFrame(data)
        colors = {"Cibao FC": "#FF8C00", "Promedio Liga": "#FFC966"}
        
        if orientacion == 'h':
            fig = px.bar(df_plot, x="valor", y="label", color="Equipo", orientation="h", text_auto=".2f", color_discrete_map=colors, barmode="group", title=nombre_grupo)
        else:
            fig = px.bar(df_plot, x="label", y="valor", color="Equipo", text_auto=".2f", color_discrete_map=colors, barmode="group", title=nombre_grupo)
            fig.update_layout(xaxis=dict(tickangle=-35))
        
        fig.update_layout(template="plotly_dark", plot_bgcolor="#111", paper_bgcolor="#111", font=dict(color="#DDD", size=11), title=dict(font=dict(size=15, color="#FF8C00")), showlegend=True, height=320, margin=dict(l=20, r=20, t=50, b=20))
        
        # Capturar como imagen
        img_base64 = grafico_a_base64(fig, width=1200, height=650)
        
        if img_base64:
            grafico_img = f"<img src='data:image/png;base64,{img_base64}' style='width:100%; height:auto;'>"
        else:
            grafico_img = f"<div style='text-align:center; color:#888; padding:40px;'>[Gráfico: {nombre_grupo}]</div>"
        
        valores = {etiquetas[col]: cibao_means[col] for col in columnas}
        max_metrica = max(valores, key=valores.get)
        min_metrica = min(valores, key=valores.get)
        
        conclusion = f"<div class='conclusion-small'><strong>↑</strong> {max_metrica} ({valores[max_metrica]:.2f}) | <strong>↓</strong> {min_metrica} ({valores[min_metrica]:.2f})</div>"
        
        html += f'<div class="grafico-grid-item">{grafico_img}{conclusion}</div>'
    
    html += '</div></div>'
    return html

def generar_seccion_heatmaps_con_imagenes(titulo, grupos, df_filtrado):
    """Genera HTML para heatmaps como imágenes."""
    
    html = f'<div class="page"><h2 class="section-title">{titulo}</h2><div class="grid-2-cols">'
    
    for nombre_grupo, metricas in grupos.items():
        cols = [v for v in metricas.values() if v in df_filtrado.columns]
        if not cols:
            continue
        
        labels = [k for k, v in metricas.items() if v in df_filtrado.columns]
        series = df_filtrado[cols].mean().fillna(0)
        rank = series.rank(method="dense") - 1
        z_vals = rank.astype(int).to_numpy().reshape(1, -1)
        
        fig = go.Figure(data=go.Heatmap(z=z_vals, x=labels, y=[""], colorscale=[[0, "#2a2a2a"], [0.5, "#ff7b00"], [1, "#ffae42"]], showscale=True, colorbar=dict(tickvals=[0, 1, 2], ticktext=["Bajo", "Medio", "Alto"])))
        
        annotations = [dict(x=labels[j], y="", text=f"{series.iloc[j]:.1f}", font=dict(color="white", size=13), showarrow=False) for j in range(len(labels))]
        
        fig.update_layout(annotations=annotations, template="plotly_dark", title=dict(text=nombre_grupo, font=dict(size=15, color="#FF8C00")), paper_bgcolor="#111", height=320, margin=dict(l=20, r=20, t=50, b=20))
        
        img_base64 = grafico_a_base64(fig, width=1200, height=650)
        
        if img_base64:
            grafico_img = f"<img src='data:image/png;base64,{img_base64}' style='width:100%; height:auto;'>"
        else:
            grafico_img = f"<div style='text-align:center; color:#888; padding:40px;'>[Heatmap: {nombre_grupo}]</div>"
        
        max_metrica = labels[series.argmax()]
        conclusion = f"<div class='conclusion-small'><strong>Mayor actividad:</strong> {max_metrica}</div>"
        
        html += f'<div class="grafico-grid-item">{grafico_img}{conclusion}</div>'
    
    html += '</div></div>'
    return html

# ===========================================
# GENERAR PDF DIRECTO
# ===========================================

def generar_pdf_directo(df_filtrado, df_liga_mayor, partidos_sel, mostrar_prom):
    """Genera PDF directo con todos los gráficos visibles."""
    
    # Logo
    logo_base64 = ""
    try:
        logo_url = "https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png"
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            logo_base64 = base64.b64encode(response.content).decode()
    except:
        pass
    
    fecha_gen = datetime.now().strftime("%d/%m/%Y - %H:%M")
    
    # KPIs
    kpis_html = ""
    if not df_filtrado.empty:
        ultimo = df_filtrado.sort_values("Date", ascending=False).iloc[0]
        fecha_partido = pd.to_datetime(ultimo.get("Date")).strftime("%d-%m-%Y") if pd.notna(ultimo.get("Date")) else "-"
        
        kpis_html = f"""
        <div class="kpis-container">
            <div class="kpi-card"><div class="kpi-value">{fecha_partido}</div><div class="kpi-label">Fecha</div></div>
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('Jornada', '-')}</div><div class="kpi-label">Jornada</div></div>
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('Match', '-')}</div><div class="kpi-label">Partido</div></div>
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('Final Result', '-')}</div><div class="kpi-label">Resultado</div></div>
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('Alineacion', '-')}</div><div class="kpi-label">Formación</div></div>
        </div>
        <div class="kpis-container">
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('xg', 0):.2f}</div><div class="kpi-label">xG</div></div>
            <div class="kpi-card"><div class="kpi-value">{ultimo.get('possession_percent', 0):.1f}%</div><div class="kpi-label">Posesión</div></div>
            <div class="kpi-card"><div class="kpi-value">{int(ultimo.get('yellow_cards', 0))}</div><div class="kpi-label">T. Amarillas</div></div>
            <div class="kpi-card"><div class="kpi-value">{int(ultimo.get('red_cards', 0))}</div><div class="kpi-label">T. Rojas</div></div>
        </div>
        """
    
    # Gráfico comparativo
    grafico_comp_img = ""
    if not df_liga_mayor.empty:
        try:
            if 'opponent_choice' in globals() and 'x_choice' in globals() and 'y_choice' in globals():
                fig_comp, _, _ = make_team_scatter(df_liga_mayor, primary_team="Cibao", opponent=opponent_choice, x_metric=METRIC_OPTIONS.get(x_choice), y_metric=METRIC_OPTIONS.get(y_choice), x_label=x_choice, y_label=y_choice, title=f"Cibao FC vs {opponent_choice}", filters={"Competition": lambda s: s.str.contains("Liga", case=False, na=False)})
                fig_comp.update_layout(height=500, margin=dict(l=30, r=30, t=60, b=30))
                
                img_comp_base64 = grafico_a_base64(fig_comp, width=2400, height=1200)
                if img_comp_base64:
                    grafico_comp_img = f"<img src='data:image/png;base64,{img_comp_base64}' style='width:100%; height:auto;'>"
        except:
            pass
    
    # Tabs
    grupos_eficiencia = {
        "Producción ofensiva directa": {"Goles por partido": "goals", "Goles en contra": "conceded_goals", "xG": "xg"},
        "Eficiencia en el tiro": {"Disparos a puerta (%)": "shots_on_target_percent", "Disparos fuera área (%)": "shots_from_outside_penalty_area_on_target_percent"},
        "Patrones de ataque": {"Ataques posicionales (%)": "positional_attacks_with_shots_percent", "Contraataques (%)": "counter_attacks_with_shots_percent"},
        "Balón parado": {"Set pieces (%)": "set_pieces_with_shots_percent", "Corners (%)": "corners_with_shots_percent", "Penaltis (%)": "penalties_converted_percent"},
        "Juego interior": {"Entradas área": "penalty_area_entries", "Toques área": "touches_in_penalty_area", "Centros": "penalty_area_entries_crosses"},
    }
    
    tab1 = generar_seccion_html_con_imagenes("EFICIENCIA Y ATAQUE", grupos_eficiencia, df_filtrado, df_liga_mayor, mostrar_prom, 'h')
    
    grupos_construccion = {
        "Control y circulación": {"Posesión (%)": "possession_percent", "Precisión pase (%)": "passes_accurate_percent"},
        "Progresión": {"Pases progresivos (%)": "progressive_passes_accurate_percent", "Pases atrás (%)": "back_passes_accurate_percent"},
        "Conexiones": {"Pases último tercio (%)": "passes_to_final_third_accurate_percent", "Pases inteligentes (%)": "smart_passes_accurate_percent"},
        "Reinicios": {"Saques banda": "throw_ins", "Saques meta": "goal_kicks"},
    }
    
    tab2 = generar_seccion_html_con_imagenes("CONSTRUCCIÓN Y PASES", grupos_construccion, df_filtrado, df_liga_mayor, mostrar_prom, 'v')
    
    grupos_defensa = {
        "Dominio en duelos": {"Duelos ofensivos (%)": "offensive_duels_won_percent", "Duelos generales (%)": "duels_won_percent"},
        "Solidez defensiva": {"Duelos defensivos (%)": "defensive_duels_won_percent", "Duelos aéreos (%)": "aerial_duels_won_percent"},
        "Acciones defensivas": {"Intercepciones": "interceptions", "Despejes": "clearances", "Pérdidas": "losses"},
        "Presión rival": {"Disparos contra": "shots_against", "Disparos contra puerta": "shots_against_on_target"},
    }
    
    tab3 = generar_seccion_html_con_imagenes("DEFENSA Y EFICIENCIA", grupos_defensa, df_filtrado, df_liga_mayor, mostrar_prom, 'h')
    
    grupos_tactica = {
        "Recuperaciones por altura": {"Altas": "recoveries_high", "Medias": "recoveries_medium", "Bajas": "recoveries_low"},
        "Presión por altura": {"Alta": "losses_high", "Media": "losses_medium", "Baja": "losses_low"},
    }
    
    tab4 = generar_seccion_heatmaps_con_imagenes("DISTRIBUCIÓN TÁCTICA", grupos_tactica, df_filtrado)
    
    # HTML completo
    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4 landscape; margin: 8mm; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background-color: #111111; color: #DDDDDD; }}
        
        .page {{ background-color: #111111; padding: 15px; min-height: 100vh; page-break-after: always; }}
        .page:last-child {{ page-break-after: auto; }}
        
        .portada {{ display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; height: 100vh; }}
        .portada img {{ width: 150px; margin-bottom: 40px; }}
        .portada h1 {{ color: #FF8C00; font-size: 48px; font-weight: 900; margin: 10px 0; }}
        .portada h2 {{ color: #DDDDDD; font-size: 24px; margin-bottom: 60px; }}
        .portada .fecha {{ color: #999999; font-size: 14px; margin: 5px 0; }}
        
        .kpis-container {{ display: flex; justify-content: space-around; margin: 15px 0; gap: 8px; }}
        .kpi-card {{ background: rgba(30,30,30,0.8); border: 2px solid rgba(255,140,0,0.4); border-radius: 10px; padding: 12px; text-align: center; flex: 1; }}
        .kpi-value {{ color: #FF8C00; font-size: 20px; font-weight: 900; margin-bottom: 6px; }}
        .kpi-label {{ color: #CCCCCC; font-size: 11px; }}
        
        .section-title {{ color: #FF8C00; font-size: 26px; font-weight: 900; text-align: center; margin: 15px 0 20px 0; }}
        
        .grid-2-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px; }}
        .grafico-grid-item {{ background: rgba(20,20,20,0.5); border-radius: 8px; padding: 10px; page-break-inside: avoid; }}
        .grafico-grid-item img {{ width: 100%; height: auto; display: block; }}
        
        .conclusion-small {{ background: rgba(30,30,30,0.9); border-left: 3px solid #FF8C00; padding: 8px; margin-top: 8px; font-size: 11px; color: #DDDDDD; }}
        .conclusion-small strong {{ color: #FF8C00; }}
        
        .final {{ display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; }}
        .final h1 {{ color: #FF8C00; font-size: 48px; margin-bottom: 20px; }}
        .final p {{ color: #AAAAAA; font-size: 18px; margin: 5px 0; }}
    </style>
</head>
<body>

<div class="page portada">
    {"<img src='data:image/png;base64," + logo_base64 + "' alt='Logo'>" if logo_base64 else ""}
    <h1>REPORTE DE RENDIMIENTO</h1>
    <h1>COLECTIVO</h1>
    <h2>Liga Dominicana - Temporada 2024/2025</h2>
    <p class="fecha">Generado: {fecha_gen}</p>
    {f"<p class='fecha'>Partidos: {', '.join(partidos_sel[:3])}</p>" if partidos_sel else ""}
</div>

<div class="page">
    <h2 class="section-title">INDICADORES DEL ÚLTIMO PARTIDO</h2>
    {kpis_html}
    <div style="margin-top: 20px;">{grafico_comp_img}</div>
</div>

{tab1}
{tab2}
{tab3}
{tab4}

<div class="page final">
    <h1>CIBAO FC</h1>
    <p>Departamento de Análisis y Rendimiento</p>
    <p>www.cibaofc.com</p>
</div>

</body>
</html>"""
    
    # Convertir a PDF con weasyprint
    from weasyprint import HTML
    pdf_bytes = HTML(string=html_completo).write_pdf()
    
    return pdf_bytes

# ===========================================
# INTERFAZ STREAMLIT
# ===========================================

st.markdown("<hr style='margin:40px 0; border-color:#ff8c00;'>", unsafe_allow_html=True)

st.markdown("""
<h2 style='color:#ff8c00; text-align:center;'>
    📄 Descargar Reporte PDF Profesional
</h2>
<p style='text-align:center; color:#ccc; font-size:14px;'>
    PDF directo con todos los gráficos visibles - Layout 2x2
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🚀 GENERAR PDF DIRECTO", use_container_width=True, type="primary"):
        with st.spinner("Generando PDF con todos los gráficos... 60-120 segundos ⏳"):
            try:
                pdf_bytes = generar_pdf_directo(df_filtrado, df_liga_mayor, partidos_seleccionados if 'partidos_seleccionados' in locals() else [], mostrar_promedio_liga)
                
                fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M")
                nombre_archivo = f"Cibao_FC_Reporte_{fecha_archivo}.pdf"
                
                st.success("✅ PDF profesional generado con éxito!")
                
                st.download_button(
                    label="📥 DESCARGAR PDF COMPLETO",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
