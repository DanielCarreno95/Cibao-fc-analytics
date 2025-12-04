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
# SECCIÓN DE EXPORTACIÓN A PDF
# ===========================================

import io
import tempfile
from fpdf import FPDF
import plotly.io as pio
from datetime import datetime
import requests
from PIL import Image

# ===========================================
# CLASE PDF PERSONALIZADA CIBAO FC
# ===========================================

class CibaoReportPDF(FPDF):
    """PDF personalizado con header y footer institucional."""
    
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Header institucional en cada página (excepto portada)."""
        if self.page_no() > 1:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(255, 140, 0)  # Naranja Cibao
            self.cell(0, 10, 'Cibao FC - Rendimiento Colectivo (Liga)', 0, 1, 'L')
            self.set_draw_color(255, 140, 0)
            self.line(10, 20, 287, 20)
            self.ln(5)
    
    def footer(self):
        """Footer con número de página."""
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(180, 180, 180)
            self.cell(0, 10, f'Página {self.page_no()-1}', 0, 0, 'C')

# ===========================================
# FUNCIÓN: CAPTURAR GRÁFICO PLOTLY COMO IMAGEN
# ===========================================

def plotly_to_image_bytes(fig, width=1400, height=800):
    """Convierte figura de Plotly a bytes de imagen PNG."""
    try:
        img_bytes = pio.to_image(fig, format='png', width=width, height=height, scale=2)
        return img_bytes
    except Exception as e:
        st.warning(f"Error capturando gráfico: {e}")
        return None

# ===========================================
# FUNCIÓN: GENERAR CONCLUSIONES AUTOMÁTICAS
# ===========================================

def generar_conclusiones_automaticas(df_cibao, df_liga_mayor):
    """
    Genera conclusiones automáticas comparando Cibao con promedio de liga.
    Retorna dict con fortalezas y debilidades.
    """
    
    # Métricas clave para analizar
    metricas_analisis = {
        "xg": "Goles Esperados (xG)",
        "possession_percent": "Posesión (%)",
        "passes_accurate_percent": "Precisión de Pase (%)",
        "shots_on_target_percent": "Disparos a Puerta (%)",
        "duels_won_percent": "Duelos Ganados (%)",
        "interceptions": "Intercepciones p90",
    }
    
    fortalezas = []
    debilidades = []
    
    if df_liga_mayor.empty:
        return {"fortalezas": ["Datos de liga no disponibles"], "debilidades": []}
    
    # Calcular promedios
    df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
    
    for col_key, nombre_metrica in metricas_analisis.items():
        if col_key not in df_cibao.columns or col_key not in df_liga_sin_cibao.columns:
            continue
            
        val_cibao = pd.to_numeric(df_cibao[col_key], errors='coerce').mean()
        val_liga = pd.to_numeric(df_liga_sin_cibao[col_key], errors='coerce').mean()
        
        if pd.isna(val_cibao) or pd.isna(val_liga):
            continue
        
        diferencia = val_cibao - val_liga
        porcentaje_dif = (diferencia / val_liga * 100) if val_liga != 0 else 0
        
        # Si está 10% o más por encima = fortaleza
        if porcentaje_dif >= 10:
            fortalezas.append({
                "metrica": nombre_metrica,
                "cibao": val_cibao,
                "liga": val_liga,
                "diferencia": porcentaje_dif
            })
        # Si está 10% o más por debajo = debilidad
        elif porcentaje_dif <= -10:
            debilidades.append({
                "metrica": nombre_metrica,
                "cibao": val_cibao,
                "liga": val_liga,
                "diferencia": porcentaje_dif
            })
    
    # Ordenar por diferencia
    fortalezas = sorted(fortalezas, key=lambda x: x['diferencia'], reverse=True)[:3]
    debilidades = sorted(debilidades, key=lambda x: x['diferencia'])[:3]
    
    return {"fortalezas": fortalezas, "debilidades": debilidades}

# ===========================================
# FUNCIÓN: DESCARGAR LOGO DESDE URL
# ===========================================

def descargar_logo():
    """Descarga el logo de Cibao FC y lo guarda temporalmente."""
    try:
        logo_url = "https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png"
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            temp_logo = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_logo.write(response.content)
            temp_logo.close()
            return temp_logo.name
        return None
    except:
        return None

# ===========================================
# FUNCIÓN PRINCIPAL: GENERAR PDF COMPLETO
# ===========================================

def generar_pdf_completo(df_filtrado, df_liga_mayor, partidos_seleccionados, 
                         fig_comparativa, figs_tabs):
    """
    Genera PDF completo con todas las secciones del análisis.
    
    Args:
        df_filtrado: DataFrame con datos de Cibao filtrados
        df_liga_mayor: DataFrame con datos de toda la liga
        partidos_seleccionados: Lista de partidos incluidos en el análisis
        fig_comparativa: Figura de la comparativa Cibao vs Rival
        figs_tabs: Dict con las figuras de cada tab organizadas por sección
    
    Returns:
        bytes del PDF generado
    """
    
    pdf = CibaoReportPDF()
    
    # ===========================================
    # PORTADA
    # ===========================================
    
    pdf.add_page()
    
    # Fondo de color
    pdf.set_fill_color(17, 17, 17)
    pdf.rect(0, 0, 297, 210, 'F')
    
    # Logo
    logo_path = descargar_logo()
    if logo_path:
        try:
            pdf.image(logo_path, x=115, y=30, w=60)
        except:
            pass
    
    # Título principal
    pdf.set_y(100)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(255, 140, 0)
    pdf.cell(0, 15, 'REPORTE DE RENDIMIENTO COLECTIVO', 0, 1, 'C')
    
    # Subtítulo
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(220, 220, 220)
    pdf.cell(0, 10, 'Liga Dominicana - Temporada 2024/2025', 0, 1, 'C')
    
    pdf.ln(15)
    
    # Información del reporte
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(180, 180, 180)
    
    fecha_generacion = datetime.now().strftime("%d/%m/%Y - %H:%M")
    pdf.cell(0, 8, f'Fecha de generación: {fecha_generacion}', 0, 1, 'C')
    
    if partidos_seleccionados:
        partidos_texto = ", ".join(partidos_seleccionados[:3])
        if len(partidos_seleccionados) > 3:
            partidos_texto += "..."
        pdf.cell(0, 8, f'Partidos analizados: {partidos_texto}', 0, 1, 'C')
    
    # Línea decorativa
    pdf.set_y(165)
    pdf.set_draw_color(255, 140, 0)
    pdf.set_line_width(1)
    pdf.line(50, 165, 247, 165)
    
    # Footer portada
    pdf.set_y(180)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, 'Análisis táctico y estadístico avanzado', 0, 1, 'C')
    pdf.cell(0, 6, 'Departamento de Análisis - Cibao FC', 0, 1, 'C')
    
    # ===========================================
    # PÁGINA 2: CONCLUSIONES EJECUTIVAS
    # ===========================================
    
    pdf.add_page()
    
    # Título de sección
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(255, 140, 0)
    pdf.cell(0, 12, 'RESUMEN EJECUTIVO', 0, 1, 'C')
    pdf.ln(8)
    
    # Generar conclusiones
    conclusiones = generar_conclusiones_automaticas(df_filtrado, df_liga_mayor)
    
    # FORTALEZAS
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(100, 220, 100)  # Verde
    pdf.cell(0, 10, 'FORTALEZAS PRINCIPALES', 0, 1, 'L')
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(220, 220, 220)
    
    if conclusiones["fortalezas"]:
        for item in conclusiones["fortalezas"]:
            # Bullet point
            pdf.set_x(15)
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(255, 140, 0)
            pdf.cell(5, 7, chr(149), 0, 0, 'L')  # Bullet
            
            # Texto
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(220, 220, 220)
            texto = f"{item['metrica']}: Cibao {item['cibao']:.2f} vs Liga {item['liga']:.2f} "
            texto += f"(+{item['diferencia']:.1f}%)"
            pdf.cell(0, 7, texto, 0, 1, 'L')
    else:
        pdf.set_x(15)
        pdf.cell(0, 7, 'Rendimiento equilibrado respecto al promedio de liga', 0, 1, 'L')
    
    pdf.ln(8)
    
    # ÁREAS DE MEJORA
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 100, 100)  # Rojo suave
    pdf.cell(0, 10, 'AREAS DE MEJORA', 0, 1, 'L')
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(220, 220, 220)
    
    if conclusiones["debilidades"]:
        for item in conclusiones["debilidades"]:
            pdf.set_x(15)
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(255, 140, 0)
            pdf.cell(5, 7, chr(149), 0, 0, 'L')
            
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(220, 220, 220)
            texto = f"{item['metrica']}: Cibao {item['cibao']:.2f} vs Liga {item['liga']:.2f} "
            texto += f"({item['diferencia']:.1f}%)"
            pdf.cell(0, 7, texto, 0, 1, 'L')
    else:
        pdf.set_x(15)
        pdf.cell(0, 7, 'No se identificaron areas significativas de mejora', 0, 1, 'L')
    
    pdf.ln(10)
    
    # Marco decorativo
    pdf.set_draw_color(255, 140, 0)
    pdf.set_line_width(0.5)
    pdf.rect(10, 30, 277, 150)
    
    # ===========================================
    # COMPARATIVA CIBAO VS RIVAL
    # ===========================================
    
    if fig_comparativa:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(255, 140, 0)
        pdf.cell(0, 12, 'COMPARATIVA: CIBAO FC VS RIVAL', 0, 1, 'C')
        pdf.ln(5)
        
        img_bytes = plotly_to_image_bytes(fig_comparativa, width=2400, height=1400)
        if img_bytes:
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_img.write(img_bytes)
            temp_img.close()
            try:
                pdf.image(temp_img.name, x=15, y=45, w=265)
            except:
                pass
    
    # ===========================================
    # SECCIONES DE ANÁLISIS (TABS)
    # ===========================================
    
    secciones = [
        ("EFICIENCIA Y ATAQUE", "eficiencia_ataque"),
        ("CONSTRUCCION Y PASES", "construccion_pases"),
        ("DEFENSA Y EFICIENCIA", "defensa"),
        ("DISTRIBUCION TACTICA", "tactica"),
    ]
    
    for titulo_seccion, key_seccion in secciones:
        if key_seccion not in figs_tabs or not figs_tabs[key_seccion]:
            continue
        
        figuras = figs_tabs[key_seccion]
        
        # Título de sección en nueva página
        pdf.add_page()
        pdf.set_font('Arial', 'B', 20)
        pdf.set_text_color(255, 140, 0)
        pdf.cell(0, 12, titulo_seccion, 0, 1, 'C')
        pdf.ln(3)
        
        # Agregar cada gráfico de la sección
        y_position = 40
        graficos_por_pagina = 2
        contador = 0
        
        for fig in figuras:
            if contador > 0 and contador % graficos_por_pagina == 0:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 16)
                pdf.set_text_color(255, 140, 0)
                pdf.cell(0, 10, f'{titulo_seccion} (continuación)', 0, 1, 'C')
                y_position = 40
            
            img_bytes = plotly_to_image_bytes(fig, width=2400, height=1200)
            if img_bytes:
                temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_img.write(img_bytes)
                temp_img.close()
                try:
                    pdf.image(temp_img.name, x=15, y=y_position, w=265, h=75)
                    y_position += 85
                except:
                    pass
            
            contador += 1
    
    # ===========================================
    # PÁGINA FINAL
    # ===========================================
    
    pdf.add_page()
    pdf.set_y(90)
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(255, 140, 0)
    pdf.cell(0, 15, 'CIBAO FC', 0, 1, 'C')
    
    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 8, 'Departamento de Analisis y Rendimiento', 0, 1, 'C')
    pdf.cell(0, 8, 'www.cibaofc.com', 0, 1, 'C')
    
    # Generar PDF
    return pdf.output(dest='S').encode('latin-1')

# ===========================================
# INTERFAZ EN STREAMLIT
# ===========================================

st.markdown("<hr style='margin:40px 0; border-color:#ff8c00;'>", unsafe_allow_html=True)

st.markdown("""
<h2 style='color:#ff8c00; text-align:center; margin-top:30px;'>
    📄 Exportar Reporte Completo en PDF
</h2>
<p style='text-align:center; color:#ccc; font-size:15px;'>
    Genera un reporte profesional con todas las métricas, gráficos y conclusiones del análisis.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Botón para generar PDF
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    if st.button("🚀 GENERAR REPORTE PDF", use_container_width=True, type="primary"):
        
        with st.spinner("Generando reporte... Esto puede tomar 30-60 segundos ⏳"):
            
            try:
                # ===== CAPTURAR TODAS LAS FIGURAS =====
                
                # 1. Figura comparativa (si existe)
                fig_comparativa_pdf = None
                if not df_liga_mayor.empty and opponent_choice:
                    try:
                        fig_comparativa_pdf, _, _ = make_team_scatter(
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
                    except:
                        pass
                
                # 2. Figuras de las tabs
                figs_dict = {
                    "eficiencia_ataque": [],
                    "construccion_pases": [],
                    "defensa": [],
                    "tactica": [],
                }
                
                # TAB 1: Eficiencia y Ataque
                for nombre_grupo, mapping in grupos.items():
                    fig = crear_grafico_para_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor, 
                                                   mostrar_promedio_liga, tipo='horizontal')
                    if fig:
                        figs_dict["eficiencia_ataque"].append(fig)
                
                # TAB 2: Construcción y Pases
                for nombre_grupo, mapping in grupos_pases.items():
                    if nombre_grupo == "Longitud media de pase":
                        fig = crear_gauge_para_pdf(mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga)
                    else:
                        fig = crear_grafico_para_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor,
                                                       mostrar_promedio_liga, tipo='vertical')
                    if fig:
                        figs_dict["construccion_pases"].append(fig)
                
                # TAB 3: Defensa
                for nombre_grupo, mapping in grupos_def.items():
                    if nombre_grupo == "Distancia media de disparo":
                        fig = crear_gauge_para_pdf(mapping, df_filtrado, df_liga_mayor, mostrar_promedio_liga)
                    else:
                        fig = crear_grafico_para_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor,
                                                       mostrar_promedio_liga, tipo='horizontal')
                    if fig:
                        figs_dict["defensa"].append(fig)
                
                # TAB 4: Táctica
                for nombre_grupo, mapping in grupos_tacticos.items():
                    fig = crear_heatmap_para_pdf(nombre_grupo, mapping, df_filtrado)
                    if fig:
                        figs_dict["tactica"].append(fig)
                
                # ===== GENERAR PDF =====
                pdf_bytes = generar_pdf_completo(
                    df_filtrado,
                    df_liga_mayor,
                    partidos_seleccionados,
                    fig_comparativa_pdf,
                    figs_dict
                )
                
                # ===== BOTÓN DE DESCARGA =====
                fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M")
                nombre_archivo = f"Cibao_FC_Rendimiento_Colectivo_{fecha_archivo}.pdf"
                
                st.success("✅ ¡Reporte generado exitosamente!")
                
                st.download_button(
                    label="📥 DESCARGAR PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"❌ Error generando el reporte: {str(e)}")
                st.exception(e)

# ===========================================
# FUNCIONES AUXILIARES PARA RECREAR GRÁFICOS
# ===========================================

def crear_grafico_para_pdf(nombre_grupo, mapping, df_filtrado, df_liga_mayor, 
                            mostrar_promedio, tipo='horizontal'):
    """Recrea un gráfico de barras para el PDF."""
    
    columnas = [v for v in mapping.values() if v in df_filtrado.columns]
    etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if not columnas:
        return None
    
    cibao_means = df_filtrado[columnas].mean()
    comparison_data = []
    
    for col in columnas:
        comparison_data.append({
            "label": etiquetas[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    if mostrar_promedio and not df_liga_mayor.empty:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        for col in columnas:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": etiquetas[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    df_plot = pd.DataFrame(comparison_data)
    color_map = {
        "Cibao FC": "#FF8C00",
        "Promedio Liga": "#FFC966",
    }
    
    if tipo == 'horizontal':
        fig = px.bar(df_plot, x="valor", y="label", color="Equipo",
                     orientation="h", text_auto=".2f", color_discrete_map=color_map,
                     barmode="group", title=nombre_grupo)
    else:
        fig = px.bar(df_plot, x="label", y="valor", color="Equipo",
                     text_auto=".2f", color_discrete_map=color_map,
                     barmode="group", title=nombre_grupo)
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="#D3D3D3", size=14),
        title=dict(font=dict(size=20, color="#FF8C00")),
        showlegend=True
    )
    
    return fig

def crear_gauge_para_pdf(mapping, df_filtrado, df_liga_mayor, mostrar_promedio):
    """Recrea un gráfico de gauge para el PDF."""
    
    col = list(mapping.values())[0]
    label = list(mapping.keys())[0]
    
    if col not in df_filtrado.columns:
        return None
    
    value_cibao = df_filtrado[col].mean()
    value_liga = None
    
    if mostrar_promedio and not df_liga_mayor.empty and col in df_liga_mayor.columns:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        value_liga = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value_cibao,
        title={'text': f"<b>{label}</b>", 'font': {'color': '#FF8C00', 'size': 20}},
        number={'font': {'color': '#FF8C00', 'size': 48}},
        gauge={
            'axis': {'range': [0, max(40, value_cibao * 1.5)]},
            'bar': {'color': "#FF8C00", 'thickness': 0.7},
            'bgcolor': "#333",
            'threshold': {
                'line': {'color': "#FFC966", 'width': 3},
                'thickness': 0.8,
                'value': value_liga if value_liga and not pd.isna(value_liga) else 0
            } if value_liga and not pd.isna(value_liga) else None
        },
    ))
    
    fig.update_layout(
        paper_bgcolor="#111",
        font=dict(color="#D3D3D3")
    )
    
    return fig

def crear_heatmap_para_pdf(nombre_grupo, mapping, df_filtrado):
    """Recrea un heatmap para el PDF."""
    
    cols = [v for v in mapping.values() if v in df_filtrado.columns]
    labels = [k for k, v in mapping.items() if v in df_filtrado.columns]
    
    if not cols:
        return None
    
    series_real = df_filtrado[cols].mean().fillna(0)
    rank = series_real.rank(method="dense") - 1
    z_vals = rank.astype(int).to_numpy().reshape(1, -1)
    
    HEATMAP_COLORSCALE = [
        [0.0, "#2a2a2a"],
        [0.5, "#ff7b00"],
        [1.0, "#ffae42"]
    ]
    
    fig = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=labels,
            y=[""],
            colorscale=HEATMAP_COLORSCALE,
            showscale=True,
            colorbar=dict(
                tickvals=[0, 1, 2],
                ticktext=["Bajo", "Medio", "Alto"],
            )
        )
    )
    
    annotations = []
    for j, label in enumerate(labels):
        annotations.append(
            dict(x=label, y="", text=f"{series_real.iloc[j]:.2f}",
                 font=dict(color="white", size=16), showarrow=False)
        )
    
    fig.update_layout(
        annotations=annotations,
        template="plotly_dark",
        title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=20, color="#FF8C00")),
        paper_bgcolor="#111",
        plot_bgcolor="#111",
    )
    
    return fig
