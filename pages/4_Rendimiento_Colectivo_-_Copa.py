import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing.load_concacaf_matchstats_data import load_concacaf_matchstats_data
from src.utils.metrics_dictionary_concacaf import METRICS_CONCACAF, METRIC_GROUPS_CONCACAF
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja
from graficos_de_navaja_suiza import make_team_scatter

CIBAO_ORANGE = "#FF8C00"  # Naranja vibrante principal
CIBAO_ORANGE_LIGHT = "#FFC966"  # Naranja dorado/ámbar claro para rivales (mayor contraste)
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

df_ultima_cibao = df_ultima_jornada[df_ultima_jornada["team"].str.contains("Cibao", case=False, na=False)].copy()
if df_ultima_cibao.empty:
    st.warning("No hay registros del Cibao FC en la última fecha.")
    st.stop()

fecha_str = ultima_fecha.strftime("%d-%m-%Y")
fila_principal = df_ultima_cibao.iloc[0]

st.markdown("### Indicadores del último partido (Copa)")
kpi_texts = [
    ("Fecha", fecha_str),
    ("Fase", fila_principal.get("stage", "-")),
    ("Equipo Local", fila_principal.get("home_team", "-")),
    ("Equipo Visitante", fila_principal.get("away_team", "-")),
]
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

tarjetas = df_ultima_cibao[["yellowCard", "redCard"]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()
kpi_cards = [
    ("Tarjetas Amarillas", int(tarjetas["yellowCard"])),
    ("Tarjetas Rojas", int(tarjetas["redCard"])),
]
cols_cards = st.columns(len(kpi_cards))
for (label, value), col in zip(kpi_cards, cols_cards):
    with col:
        st.markdown(
            f"""
            <div style='background:rgba(25,25,25,0.95);
                        border:1px solid rgba(255,140,0,0.35);
                        border-radius:14px;padding:18px;
                        text-align:center;box-shadow:0 0 18px rgba(255,140,0,0.12);'>
                <div style='font-size:1.8rem;color:{CIBAO_ORANGE};font-weight:800;'>{value}</div>
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
# =========================================================
# 🔶 PESTAÑAS DE ANÁLISIS ESPECÍFICO — COPA
# =========================================================
tab_ofensivo, tab_pases, tab_defensivo, tab_set_pieces, tab_general = st.tabs(
    [
        "Eficiencia y Ataque",
        "Construcción y Pases",
        "Defensa y Eficiencia",
        "Acciones a balón parado",
        "Análisis Comparativo (Tablas)",
    ]
)

def _dedup_pairs(metric_mapping):
    seen = set()
    pairs = []
    for label, col in metric_mapping.items():
        real_col = METRICS_CONCACAF.get(label, col)
        if real_col and real_col not in seen and real_col in df_copa_cibao.columns:
            seen.add(real_col)
            pairs.append((label, real_col))
    return pairs

def plot_horizontal_group(group_title, mapping_pairs):
    if not mapping_pairs:
        st.warning(f"No hay datos para {group_title}.")
        return

    df_block = df_copa_cibao.copy()
    cols = [col for _, col in mapping_pairs]
    for col in cols:
        df_block[col] = pd.to_numeric(df_block[col], errors="coerce").fillna(0)

    # Calcular promedio solo de Cibao
    df_cibao_only = df_block[df_block["team"].str.contains("Cibao", case=False, na=False)]
    mean_vals = df_cibao_only[cols].mean() if not df_cibao_only.empty else pd.Series(0, index=cols)

    # Calcular promedio de rivales (equipos que NO son Cibao)
    df_rivales = df_block[~df_block["team"].str.contains("Cibao", case=False, na=False)]
    rival_means = df_rivales[cols].mean() if not df_rivales.empty else pd.Series(0, index=cols)

    df_plot = (
        pd.DataFrame(
            {
                "label": [label for label, col in mapping_pairs],
                "valor": [mean_vals[col] for _, col in mapping_pairs],
                "rival_avg": [rival_means[col] for _, col in mapping_pairs],
            }
        )
        .sort_values("valor", ascending=True)
        .reset_index(drop=True)
    )

    # Preparar datos para gráfico de barras agrupadas
    df_plot_melted = df_plot.melt(id_vars=['label'], value_vars=['valor', 'rival_avg'], 
                                   var_name='Equipo', value_name='Valor')
    df_plot_melted['Equipo'] = df_plot_melted['Equipo'].map({'valor': 'Cibao FC', 'rival_avg': 'Promedio Rivales'})
    
    fig = px.bar(
        df_plot_melted,
        x="Valor",
        y="label",
        color="Equipo",
        text_auto=".2f",
        orientation="h",
        color_discrete_map={"Cibao FC": CIBAO_ORANGE, "Promedio Rivales": "#FFA64D"},
        barmode="group",
        height=350,
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0B0B0B",
        paper_bgcolor="#0B0B0B",
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(text=f"<b>{group_title}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        title_x=0.5,
        font=dict(color=CIBAO_GRAY, size=12),
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

    # Conclusiones basadas en Cibao únicamente
    max_row = df_plot.iloc[-1]
    min_row = df_plot.iloc[0]
    st.markdown(
        f"""
        <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                    margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
            <b>Conclusiones tácticas</b><br><br>
            • <b>Punto fuerte:</b> mayor incidencia en <b>{max_row['label']}</b> ({max_row['valor']:.2f} vs Rivales: {max_row['rival_avg']:.2f}).<br>
            • <b>Área a potenciar:</b> menor impacto en <b>{min_row['label']}</b> ({min_row['valor']:.2f} vs Rivales: {min_row['rival_avg']:.2f}).<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_ofensivo:
    st.markdown(
        """
        <h3 style='text-align:center; color:#ff8c00;'>Eficiencia y Ataque</h3>
        <p style='text-align:center; color:#bbb; font-size:14px;'>
            Producción ofensiva, volumen de tiro y ventajas obtenidas en acciones ofensivas.
        </p>
        """,
        unsafe_allow_html=True,
    )

    grupo1 = {
        "Goles": "goals",
        "Intentos de Gol": "totalScoringAtt",
        "Asistencias de Gol": "goalAssist",
    }
    grupo2 = {
        "Disparos Totales": "totalScoringAtt",
        "Disparos al Arco": "ontargetScoringAtt",
        "Disparos Fuera del Arco": "shotOffTarget",
        "Disparos Bloqueados": "blockedScoringAtt",
    }
    grupo3 = {
        "Faltas a Favor": "wasFouled",
        "Fuera de Juego": "totalOffside",
    }

    col1, col2 = st.columns(2)
    with col1:
        plot_horizontal_group("Productividad ofensiva directa", _dedup_pairs(grupo1))
    with col2:
        plot_horizontal_group("Distribución de disparos", _dedup_pairs(grupo2))

    plot_horizontal_group("Ventajas generadas", _dedup_pairs(grupo3))
    
with tab_pases:
    st.markdown(
        """
        <h3 style='text-align:center; color:#ff8c00;'>Construcción y Pases</h3>
        <p style='text-align:center; color:#bbb; font-size:14px;'>
            Volumen total, precisión y proxy de posesión en Copa Concacaf.
        </p>
        """,
        unsafe_allow_html=True,
    )

    pases_grupo = {
        "Total de Pases": "totalPass",
        "Pases Precisos": "accuratePass",
        "Posesión (aprox.)": "totalPass",
    }

    pares = _dedup_pairs(pases_grupo)

    if pares:
        cols = [col for _, col in pares]
        df_p = df_copa_cibao.copy()
        for col in cols:
            df_p[col] = pd.to_numeric(df_p[col], errors="coerce").fillna(0)

        # Calcular promedio solo de Cibao
        df_cibao_only = df_p[df_p["team"].str.contains("Cibao", case=False, na=False)]
        mean_vals = df_cibao_only[cols].mean() if not df_cibao_only.empty else pd.Series(0, index=cols)

        # Calcular promedio de rivales
        df_rivales = df_p[~df_p["team"].str.contains("Cibao", case=False, na=False)]
        rival_means = df_rivales[cols].mean() if not df_rivales.empty else pd.Series(0, index=cols)

        df_plot = pd.DataFrame(
            {
                "label": [label for label, _ in pares],
                "valor": [mean_vals[col] for _, col in pares],
                "rival_avg": [rival_means[col] for _, col in pares],
            }
        ).sort_values("valor", ascending=False)

        # Preparar datos para gráfico de barras agrupadas
        df_plot_melted = df_plot.melt(id_vars=['label'], value_vars=['valor', 'rival_avg'], 
                                       var_name='Equipo', value_name='Valor')
        df_plot_melted['Equipo'] = df_plot_melted['Equipo'].map({'valor': 'Cibao FC', 'rival_avg': 'Promedio Rivales'})
        
        fig = px.bar(
            df_plot_melted,
            x="label",
            y="Valor",
            color="Equipo",
            text_auto=".2f",
            color_discrete_map={"Cibao FC": CIBAO_ORANGE, "Promedio Rivales": "#FFA64D"},
            barmode="group",
            height=420,
        )

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0B0B0B",
            paper_bgcolor="#0B0B0B",
            margin=dict(l=40, r=40, t=60, b=40),
            title=dict(text="<b>Volumen y precisión en la circulación</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            title_x=0.5,
            font=dict(color=CIBAO_GRAY, size=12),
            xaxis=dict(tickangle=-15),
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

        # Obtener valores originales de df_plot (antes del melt)
        max_row = df_plot.iloc[0]
        min_row = df_plot.iloc[-1]

        st.markdown(
            f"""
            <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px; border-radius:6px;'>
                <b>Conclusiones tácticas</b><br><br>
                • <b>Punto fuerte:</b> mayor aporte en <b>{max_row['label']}</b> ({max_row['valor']:.2f} vs Rivales: {max_row['rival_avg']:.2f}).<br>
                • <b>Área por optimizar:</b> menor incidencia en <b>{min_row['label']}</b> ({min_row['valor']:.2f} vs Rivales: {min_row['rival_avg']:.2f}).<br>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("No hay datos disponibles para Construcción y Pases.")

with tab_defensivo:
    st.markdown(
        """
        <h3 style='text-align:center; color:#ff8c00;'>Defensa y Eficiencia</h3>
        <p style='text-align:center; color:#bbb; font-size:14px;'>
            Volumen de acciones defensivas, contenciones bajo palos y castigo recibido en Copa Concacaf.
        </p>
        """,
        unsafe_allow_html=True,
    )

    grupo_def1 = {
        "Entradas Totales": "totalTackle",
        "Entradas Ganadas": "wonTackle",
        "Despejes": "totalClearance",
        "Faltas Cometidas": "fouls",
    }

    grupo_def2 = {
        "Atajadas": "saves",
        "Valla Invicta": "cleanSheet",
        "Goles Recibidos": "goalsConceded",
    }

    def plot_def_block(title, mapping):
        pares = _dedup_pairs(mapping)
        if not pares:
            st.warning(f"No hay datos para {title}.")
            return

        cols = [col for _, col in pares]
        df_d = df_copa_cibao.copy()
        for col in cols:
            df_d[col] = pd.to_numeric(df_d[col], errors="coerce").fillna(0)

        # Calcular promedio solo de Cibao
        df_cibao_only = df_d[df_d["team"].str.contains("Cibao", case=False, na=False)]
        mean_vals = df_cibao_only[cols].mean() if not df_cibao_only.empty else pd.Series(0, index=cols)

        # Calcular promedio de rivales
        df_rivales = df_d[~df_d["team"].str.contains("Cibao", case=False, na=False)]
        rival_means = df_rivales[cols].mean() if not df_rivales.empty else pd.Series(0, index=cols)

        df_plot = (
            pd.DataFrame({
                "label": [label for label, _ in pares], 
                "valor": [mean_vals[col] for _, col in pares],
                "rival_avg": [rival_means[col] for _, col in pares]
            })
            .sort_values("valor", ascending=True)
            .reset_index(drop=True)
        )

        # Preparar datos para gráfico de barras agrupadas
        df_plot_melted = df_plot.melt(id_vars=['label'], value_vars=['valor', 'rival_avg'], 
                                       var_name='Equipo', value_name='Valor')
        df_plot_melted['Equipo'] = df_plot_melted['Equipo'].map({'valor': 'Cibao FC', 'rival_avg': 'Promedio Rivales'})
        
        fig = px.bar(
            df_plot_melted,
            x="Valor",
            y="label",
            color="Equipo",
            text_auto=".2f",
            orientation="h",
            color_discrete_map={"Cibao FC": CIBAO_ORANGE, "Promedio Rivales": "#FFA64D"},
            barmode="group",
            height=360,
        )

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0B0B0B",
            paper_bgcolor="#0B0B0B",
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(text=f"<b>{title}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            title_x=0.5,
            font=dict(color=CIBAO_GRAY, size=12),
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

        max_row = df_plot.iloc[-1]
        min_row = df_plot.iloc[0]
        st.markdown(
            f"""
            <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
                <b>Conclusiones tácticas</b><br><br>
                • <b>Punto fuerte:</b> mayor impacto en <b>{max_row['label']}</b> ({max_row['valor']:.2f} vs Rivales: {max_row['rival_avg']:.2f}).<br>
                • <b>Área a vigilar:</b> menor incidencia en <b>{min_row['label']}</b> ({min_row['valor']:.2f} vs Rivales: {min_row['rival_avg']:.2f}).<br>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_def1, col_def2 = st.columns(2)
    with col_def1:
        plot_def_block("Acciones defensivas y disputas", grupo_def1)
    with col_def2:
        plot_def_block("Contención bajo palos", grupo_def2)

with tab_set_pieces:
    st.markdown(
        """
        <h3 style='text-align:center; color:#ff8c00;'>Acciones a balón parado</h3>
        <p style='text-align:center; color:#bbb; font-size:14px;'>
            Lectura de reinicios y saques que activan el juego en Copa Concacaf.
        </p>
        """,
        unsafe_allow_html=True,
    )

    grupo_sp1 = {
        "Saques de Meta": "goalKicks",
        "Saques de Banda": "totalThrows",
    }

    grupo_sp2 = {
        "Saques de Esquina Ganados": "wonCorners",
        "Saques de Esquina Perdidos": "lostCorners",
        "Saques de Esquina Ejecutados": "cornerTaken",
    }

    def plot_setpiece_group(title, mapping):
        pares = _dedup_pairs(mapping)
        if not pares:
            st.warning(f"No hay datos para {title}.")
            return

        cols = [col for _, col in pares]
        df_sp = df_copa_cibao.copy()
        for col in cols:
            df_sp[col] = pd.to_numeric(df_sp[col], errors="coerce").fillna(0)

        # Calcular promedio solo de Cibao
        df_cibao_only = df_sp[df_sp["team"].str.contains("Cibao", case=False, na=False)]
        mean_vals = df_cibao_only[cols].mean() if not df_cibao_only.empty else pd.Series(0, index=cols)

        # Calcular promedio de rivales
        df_rivales = df_sp[~df_sp["team"].str.contains("Cibao", case=False, na=False)]
        rival_means = df_rivales[cols].mean() if not df_rivales.empty else pd.Series(0, index=cols)

        df_plot = (
            pd.DataFrame({
                "label": [label for label, _ in pares], 
                "valor": [mean_vals[col] for _, col in pares],
                "rival_avg": [rival_means[col] for _, col in pares]
            })
            .sort_values("valor", ascending=True)
            .reset_index(drop=True)
        )

        # Preparar datos para gráfico de barras agrupadas
        df_plot_melted = df_plot.melt(id_vars=['label'], value_vars=['valor', 'rival_avg'], 
                                       var_name='Equipo', value_name='Valor')
        df_plot_melted['Equipo'] = df_plot_melted['Equipo'].map({'valor': 'Cibao FC', 'rival_avg': 'Promedio Rivales'})
        
        fig = px.bar(
            df_plot_melted,
            x="Valor",
            y="label",
            color="Equipo",
            text_auto=".2f",
            orientation="h",
            color_discrete_map={"Cibao FC": CIBAO_ORANGE, "Promedio Rivales": "#FFA64D"},
            barmode="group",
            height=360,
        )

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0B0B0B",
            paper_bgcolor="#0B0B0B",
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(text=f"<b>{title}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            title_x=0.5,
            font=dict(color=CIBAO_GRAY, size=12),
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

        max_row = df_plot.iloc[-1]
        min_row = df_plot.iloc[0]
        st.markdown(
            f"""
            <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
                <b>Conclusiones tácticas</b><br><br>
                • <b>Punto fuerte:</b> mayor producción en <b>{max_row['label']}</b> ({max_row['valor']:.2f} vs Rivales: {max_row['rival_avg']:.2f}).<br>
                • <b>Área a seguir:</b> menor incidencia en <b>{min_row['label']}</b> ({min_row['valor']:.2f} vs Rivales: {min_row['rival_avg']:.2f}).<br>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_sp1, col_sp2 = st.columns(2)
    with col_sp1:
        plot_setpiece_group("Reinicios básicos", grupo_sp1)
    with col_sp2:
        plot_setpiece_group("Saques de esquina", grupo_sp2)

with tab_general:
    st.markdown(
        """
        <h3 style='text-align:center; color:#ff8c00;'>Análisis Comparativo (Tablas)</h3>
        <p style='text-align:center; color:#bbb; font-size:14px;'>
            Comparación detallada de métricas clave entre Cibao FC y el promedio de sus rivales en Copa Concacaf.
        </p>
        """,
        unsafe_allow_html=True,
    )
    
    # Preparar datos comparativos
    metricas_comparativas = {
        "⚽ Ofensivas": {
            "Goles": "goals",
            "Intentos de Gol": "totalScoringAtt",
            "Disparos al Arco": "ontargetScoringAtt",
            "Asistencias": "goalAssist",
        },
        "🎯 Pases": {
            "Total de Pases": "totalPass",
            "Pases Precisos": "accuratePass",
        },
        "🛡️ Defensivas": {
            "Entradas Totales": "totalTackle",
            "Entradas Ganadas": "wonTackle",
            "Despejes": "totalClearance",
            "Atajadas": "saves",
            "Goles Recibidos": "goalsConceded",
        },
        "⚡ Balón Parado": {
            "Saques de Esquina Ganados": "wonCorners",
            "Saques de Esquina Ejecutados": "cornerTaken",
            "Saques de Meta": "goalKicks",
        }
    }
    
    for categoria, metricas in metricas_comparativas.items():
        st.markdown(f"### {categoria}")
        
        # Filtrar métricas disponibles
        metricas_disponibles = {k: v for k, v in metricas.items() if v in df_copa_cibao.columns}
        
        if not metricas_disponibles:
            st.warning(f"No hay datos disponibles para {categoria}")
            continue
        
        # Calcular promedios
        df_temp = df_copa_cibao.copy()
        cols = list(metricas_disponibles.values())
        
        for col in cols:
            df_temp[col] = pd.to_numeric(df_temp[col], errors="coerce").fillna(0)
        
        # Cibao
        df_cibao_only = df_temp[df_temp["team"].str.contains("Cibao", case=False, na=False)]
        cibao_means = df_cibao_only[cols].mean() if not df_cibao_only.empty else pd.Series(0, index=cols)
        
        # Rivales
        df_rivales = df_temp[~df_temp["team"].str.contains("Cibao", case=False, na=False)]
        rival_means = df_rivales[cols].mean() if not df_rivales.empty else pd.Series(0, index=cols)
        
        # Crear tabla comparativa
        tabla_data = []
        for label, col in metricas_disponibles.items():
            cibao_val = cibao_means[col]
            rival_val = rival_means[col]
            diferencia = cibao_val - rival_val
            porcentaje = ((cibao_val / rival_val - 1) * 100) if rival_val != 0 else 0
            
            # Indicador visual
            if diferencia > 0:
                indicador = "🟢"
                color_diff = "green"
            elif diferencia < 0:
                indicador = "🔴"
                color_diff = "red"
            else:
                indicador = "⚪"
                color_diff = "gray"
            
            tabla_data.append({
                "Métrica": label,
                "Cibao FC": f"{cibao_val:.2f}",
                "Promedio Rivales": f"{rival_val:.2f}",
                "Diferencia": f"{diferencia:+.2f}",
                "% Diferencia": f"{porcentaje:+.1f}%",
                "": indicador
            })
        
        df_tabla = pd.DataFrame(tabla_data)
        
        # Mostrar tabla con estilo
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
                "Cibao FC": st.column_config.TextColumn("Cibao FC", width="small"),
                "Promedio Rivales": st.column_config.TextColumn("Promedio Rivales", width="small"),
                "Diferencia": st.column_config.TextColumn("Diferencia", width="small"),
                "% Diferencia": st.column_config.TextColumn("% Diferencia", width="small"),
                "": st.column_config.TextColumn("", width="small"),
            }
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Leyenda
    st.markdown(
        f"""
        <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE}; border-radius:6px; margin-top:20px;'>
            <b>Leyenda:</b><br>
            🟢 Cibao FC supera al promedio de rivales<br>
            🔴 Cibao FC por debajo del promedio de rivales<br>
            ⚪ Valores iguales
        </div>
        """,
        unsafe_allow_html=True,
    )

