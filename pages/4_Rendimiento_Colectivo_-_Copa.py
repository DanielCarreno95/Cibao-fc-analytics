import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing.load_concacaf_matchstats_data import load_concacaf_matchstats_data
from src.utils.metrics_dictionary_concacaf import METRICS_CONCACAF, METRIC_GROUPS_CONCACAF
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja
from graficos_de_navaja_suiza import make_team_scatter

CIBAO_ORANGE = "#FF8C00"
CIBAO_GRAY = "#D3D3D3"

st.set_page_config(page_title="Rendimiento Colectivo - Copa", layout="wide")
inject_dark_theme()

# =========================================================
# ✳️ ENCABEZADO PRINCIPAL
# =========================================================
titulo_naranja("Rendimiento Colectivo — Cibao FC (Copa)")
st.markdown(
    f"""
    <p style='text-align:center; color:{CIBAO_GRAY}; font-size:17px;'>
    Lectura de <b>modelo de juego</b>, <b>eficiencia por fases</b> y <b>tendencias competitivas</b>.
    Diseñado para soporte táctico del staff técnico — decisiones claras, con contexto.
    </p>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 📂 CARGA DE DATOS COPA
# =========================================================
try:
    df_copa_merged, df_copa_cibao, df_copa_rivales = load_concacaf_matchstats_data()
except Exception as e:
    st.error(f"⚠️ Error al cargar los datos de Copa Concacaf: {e}")
    st.stop()

if df_copa_cibao.empty:
    st.warning("No hay registros de partidos de Copa Concacaf disponibles.")
    st.stop()

df_copa_cibao["Match_Date"] = pd.to_datetime(df_copa_cibao["match_date"], errors="coerce")
df_copa_cibao = df_copa_cibao.sort_values("Match_Date")

ultima_fecha = df_copa_cibao["Match_Date"].dropna().max()
df_ultima_jornada = (
    df_copa_cibao[df_copa_cibao["Match_Date"] == ultima_fecha].copy()
    if pd.notna(ultima_fecha)
    else df_copa_cibao.head(0)
)

if df_ultima_jornada.empty:
    st.warning("No se pudo determinar la última jornada de Copa.")
    st.stop()

fecha_str = ultima_fecha.strftime("%d-%m-%Y")
fila_principal = df_ultima_jornada.iloc[0]

kpi_texts = [
    ("Fecha", fecha_str),
    ("Fase", fila_principal.get("stage", "-")),
    ("Equipo Local", fila_principal.get("home_team", "-")),
    ("Equipo Visitante", fila_principal.get("away_team", "-")),
]

st.markdown("### Indicadores del último partido (Copa)")
cols_text = st.columns(len(kpi_texts))
for (label, value), col in zip(kpi_texts, cols_text):
    display = str(value) if pd.notna(value) else "-"
    with col:
        st.markdown(
            f"""
            <div style='background:rgba(25,25,25,0.95);
                        border:1px solid rgba(255,140,0,0.35);
                        border-radius:14px;padding:18px;
                        text-align:center;box-shadow:0 0 18px rgba(255,140,0,0.12);'>
                <div style='font-size:1.3rem;color:{CIBAO_ORANGE};font-weight:700;'>{display}</div>
                <div style='color:#cfcfcf;font-size:0.9rem;'>{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 🧩 COMPARATIVA CIBAO VS RIVAL (Copa)
# =========================================================
st.markdown(
    f"""
    <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
        Comparativa Copa (Cibao vs Rival)
    </h2>
    <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
        Evalúa el rendimiento del Cibao FC frente a sus rivales en Copa Concacaf,
        considerando métricas ofensivas y defensivas clave.
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
    x_default_copa = metric_labels_copa.index("Goles") if "Goles" in metric_labels_copa else 0
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

    x_column_copa = METRICS_CONCACAF.get(x_choice_copa)
    y_column_copa = METRICS_CONCACAF.get(y_choice_copa)

    if x_column_copa is None or y_column_copa is None:
        st.error("No se encontró la métrica seleccionada en el dataset de Copa.")
    else:
        df_copa_adapter = df_copa_cibao.copy()
        df_copa_adapter["Team"] = df_copa_adapter["team"]
        df_copa_adapter["Opponent"] = df_copa_adapter.apply(
            lambda r: r["away_team"] if r["team"] == r["home_team"] else r["home_team"],
            axis=1,
        )
        df_copa_adapter["Competition"] = "Copa Concacaf"
        df_copa_adapter["Date"] = pd.to_datetime(df_copa_adapter["match_date"], errors="coerce")
        df_copa_adapter["Match"] = df_copa_adapter.apply(
            lambda r: f"{r['home_team']} vs {r['away_team']}",
            axis=1,
        )
        if "Jornada" not in df_copa_adapter.columns:
            df_copa_adapter["Jornada"] = df_copa_adapter.get("stage", "Copa")

        for col_num in [x_column_copa, y_column_copa]:
            if col_num in df_copa_adapter.columns:
                df_copa_adapter[col_num] = (
                    pd.to_numeric(df_copa_adapter[col_num], errors="coerce").fillna(0)
                )

        df_copa_view = df_copa_adapter.fillna(0)

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

                fig_copa.layout.annotations = [
                    ann for ann in fig_copa.layout.annotations if ann.yref != "paper" or ann.y < 1
                ]
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

                if resumen_copa:
                    st.markdown("---")
                    st.caption(f"**Resumen:** {resumen_copa}")

            except Exception as e:
                st.warning(f"No se pudo usar make_team_scatter ({e}). Se muestra un scatter básico.")
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


def _ensure_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def _map_metrics(names):
    cols = []
    for n in names:
        col = METRICS_CONCACAF.get(n)
        if col:
            cols.append(col)
    return cols
