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

def titulo_naranja(texto):
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
        ">
            {texto}
        </h1>
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
