# =========================================================
# 📊 ANÁLISIS DE MÉTRICAS EN COPA CONCACAF
# =========================================================
from src.data_processing.load_concacaf_matchstats_data import load_concacaf_matchstats_data
from src.utils.metrics_dictionary_concacaf import METRICS_CONCACAF, METRIC_GROUPS_CONCACAF
from src.utils.global_dark_theme import titulo_naranja  # usa tu mismo tema global

titulo_naranja("Análisis de Métricas — Copa Concacaf")
st.markdown(
    f"""
    <p style='text-align:center; color:{CIBAO_GRAY}; font-size:17px;'>
    Exploración de métricas clave del Cibao FC durante la Copa Concacaf, incluyendo desempeño ofensivo,
    defensivo y de construcción.
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
    def titulo_naranja_copa(texto: str):
        st.markdown(
            f"""
            <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
                Comparativa Copa (Cibao vs Rival)
            </h2>
            <p style='text-align:center; color:{CIBAO_GRAY}; font-size:16px;'>
                Evalúa el rendimiento del Cibao FC frente a sus rivales en Copa Concacaf,
                considerando métricas ofensivas y defensivas clave.
            </p>
            <h1 style="
                text-align:center;
                font-weight:900;
                color:#ff8c00;
                text-shadow:0 0 14px rgba(255,140,0,0.65);
            ">{texto}</h1>
            """,
            unsafe_allow_html=True,
        )

    titulo_naranja_copa("Bloque comparativo Copa Concacaf")

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
            # --- ✨ Preparar dataset completo de Copa
            df_copa_adapter = df_copa_cibao.copy()
            df_copa_adapter["Team"] = df_copa_adapter["team"]
            df_copa_adapter["Opponent"] = df_copa_adapter.apply(
                lambda r: r["away_team"] if r["team"] == r["home_team"] else r["home_team"],
                axis=1,
            )
            df_copa_adapter["Competition"] = "Copa Concacaf"
            df_copa_adapter["Date"] = pd.to_datetime(df_copa_adapter["match_date"])
            df_copa_adapter["Match"] = df_copa_adapter.apply(
                lambda r: f"{r['home_team']} vs {r['away_team']}",
                axis=1,
            )
            if "Jornada" not in df_copa_adapter.columns:
                df_copa_adapter["Jornada"] = df_copa_adapter.get("stage", "Copa")

            for col_num in [x_column_copa, y_column_copa]:
                if col_num in df_copa_adapter.columns:
                    df_copa_adapter[col_num] = (
                        pd.to_numeric(df_copa_adapter[col_num], errors="coerce")
                        .fillna(0)
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
                        ann
                        for ann in fig_copa.layout.annotations
                        if ann.yref != "paper" or ann.y < 1
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
