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

    mean_vals = df_block[cols].mean()
    
    # Calcular promedio de la liga (EXCLUYENDO Cibao FC)
    df_liga = df_copa_merged.copy()
    
    # Manejo robusto para encontrar la columna de equipo
    if "team" not in df_liga.columns:
        df_liga = df_liga.reset_index()
        
    team_col = None
    possible_cols = ["team", "Team", "equipo", "Equipo", "Team Name", "Squad"]
    for col_name in possible_cols:
        if col_name in df_liga.columns:
            team_col = col_name
            break
    
    if team_col:
        df_liga = df_liga[~df_liga[team_col].str.contains("Cibao", case=False, na=False)]
        
    for col in cols:
        if col in df_liga.columns:
            df_liga[col] = pd.to_numeric(df_liga[col], errors="coerce").fillna(0)
    liga_means = df_liga[cols].mean()
    
    # Preparar datos para gráfico de barras agrupadas
    data_list = []
    for label, col in mapping_pairs:
        # Valor Cibao
        data_list.append({
            "Métrica": label,
            "Valor": mean_vals[col],
            "Equipo": "Cibao FC"
        })
        # Valor Liga
        data_list.append({
            "Métrica": label,
            "Valor": liga_means[col] if col in liga_means else 0,
            "Equipo": "Promedio Liga"
        })
        
    df_plot = pd.DataFrame(data_list)

    fig = px.bar(
        df_plot,
        x="Valor",
        y="Métrica",
        color="Equipo",
        barmode="group",
        orientation="h",
        text_auto=".2f",
        color_discrete_map={
            "Cibao FC": CIBAO_ORANGE,
            "Promedio Liga": "#00D9FF"
        },
        height=400,
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
            x=1
        ),
        xaxis_title="",
        yaxis_title=""
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Conclusiones Tácticas
    # Encontramos la métrica con mayor diferencia positiva para Cibao y la de mayor déficit
    df_diff = df_plot.pivot(index="Métrica", columns="Equipo", values="Valor")
    if not df_diff.empty and "Cibao FC" in df_diff.columns and "Promedio Liga" in df_diff.columns:
        df_diff["Diff"] = df_diff["Cibao FC"] - df_diff["Promedio Liga"]
        
        max_diff_metric = df_diff["Diff"].idxmax()
        min_diff_metric = df_diff["Diff"].idxmin()
        
        val_cibao_max = df_diff.loc[max_diff_metric, "Cibao FC"]
        val_liga_max = df_diff.loc[max_diff_metric, "Promedio Liga"]
        
        val_cibao_min = df_diff.loc[min_diff_metric, "Cibao FC"]
        val_liga_min = df_diff.loc[min_diff_metric, "Promedio Liga"]

        st.markdown(
            f"""
            <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
                <b>Conclusiones tácticas</b><br><br>
                • <b>Punto fuerte:</b> mayor ventaja en <b>{max_diff_metric}</b> ({val_cibao_max:.2f} vs Liga: {val_liga_max:.2f}).<br>
                • <b>Área a vigilar:</b> menor desempeño relativo en <b>{min_diff_metric}</b> ({val_cibao_min:.2f} vs Liga: {val_liga_min:.2f}).<br>
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

        mean_vals = df_p[cols].mean()
        df_plot = pd.DataFrame(
            {
                "label": [label for label, _ in pares],
                "valor": [mean_vals[col] for _, col in pares],
            }
        ).sort_values("valor", ascending=False)

        fig = px.bar(
            df_plot,
            x="label",
            y="valor",
            text_auto=".2f",
            color_discrete_sequence=[CIBAO_ORANGE],
            height=380,
        )
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0B0B0B",
            paper_bgcolor="#0B0B0B",
            margin=dict(l=40, r=40, t=60, b=40),
            title=dict(text="<b>Volumen y precisión en la circulación</b>", font=dict(size=18, color=CIBAO_ORANGE)),
            title_x=0.5,
            font=dict(color=CIBAO_GRAY, size=12),
            showlegend=False,
            xaxis=dict(tickangle=-15),
        )

        st.plotly_chart(fig, use_container_width=True)

        max_row = df_plot.iloc[0]
        min_row = df_plot.iloc[-1]

        st.markdown(
            f"""
            <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                        margin-top:-8px; border-radius:6px;'>
                <b>Conclusiones tácticas</b><br><br>
                • <b>Punto fuerte:</b> mayor aporte en <b>{max_row['label']}</b> ({max_row['valor']:.2f}).<br>
                • <b>Área por optimizar:</b> menor incidencia en <b>{min_row['label']}</b> ({min_row['valor']:.2f}).<br>
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

        mean_vals = df_d[cols].mean()
        
        # Calcular promedio de la liga (EXCLUYENDO Cibao FC)
        df_liga = df_copa_merged.copy()
        
        # Manejo robusto para encontrar la columna de equipo
        if "team" not in df_liga.columns:
            df_liga = df_liga.reset_index()
            
        team_col = None
        possible_cols = ["team", "Team", "equipo", "Equipo", "Team Name", "Squad"]
        for col_name in possible_cols:
            if col_name in df_liga.columns:
                team_col = col_name
                break
        
        if team_col:
            df_liga = df_liga[~df_liga[team_col].str.contains("Cibao", case=False, na=False)]
            
        for col in cols:
            if col in df_liga.columns:
                df_liga[col] = pd.to_numeric(df_liga[col], errors="coerce").fillna(0)
        liga_means = df_liga[cols].mean()
        
        # Preparar datos para gráfico de barras agrupadas
        data_list = []
        for label, col in pares:
            # Valor Cibao
            data_list.append({
                "Métrica": label,
                "Valor": mean_vals[col],
                "Equipo": "Cibao FC"
            })
            # Valor Liga
            data_list.append({
                "Métrica": label,
                "Valor": liga_means[col] if col in liga_means else 0,
                "Equipo": "Promedio Liga"
            })
            
        df_plot = pd.DataFrame(data_list)

        fig = px.bar(
            df_plot,
            x="Valor",
            y="Métrica",
            color="Equipo",
            barmode="group",
            orientation="h",
            text_auto=".2f",
            color_discrete_map={
                "Cibao FC": CIBAO_ORANGE,
                "Promedio Liga": "#00D9FF"
            },
            height=400,
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
                x=1
            ),
            xaxis_title="",
            yaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Conclusiones Tácticas
        df_diff = df_plot.pivot(index="Métrica", columns="Equipo", values="Valor")
        if not df_diff.empty and "Cibao FC" in df_diff.columns and "Promedio Liga" in df_diff.columns:
            df_diff["Diff"] = df_diff["Cibao FC"] - df_diff["Promedio Liga"]
            
            max_diff_metric = df_diff["Diff"].idxmax()
            min_diff_metric = df_diff["Diff"].idxmin()
            
            val_cibao_max = df_diff.loc[max_diff_metric, "Cibao FC"]
            val_liga_max = df_diff.loc[max_diff_metric, "Promedio Liga"]
            
            val_cibao_min = df_diff.loc[min_diff_metric, "Cibao FC"]
            val_liga_min = df_diff.loc[min_diff_metric, "Promedio Liga"]

            st.markdown(
                f"""
                <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                            margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
                    <b>Conclusiones tácticas</b><br><br>
                    • <b>Punto fuerte:</b> mayor ventaja en <b>{max_diff_metric}</b> ({val_cibao_max:.2f} vs Liga: {val_liga_max:.2f}).<br>
                    • <b>Área a vigilar:</b> menor desempeño relativo en <b>{min_diff_metric}</b> ({val_cibao_min:.2f} vs Liga: {val_liga_min:.2f}).<br>
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

        mean_vals = df_sp[cols].mean()
        
        # Calcular promedio de la liga (EXCLUYENDO Cibao FC)
        df_liga = df_copa_merged.copy()
        
        # Manejo robusto para encontrar la columna de equipo
        if "team" not in df_liga.columns:
            df_liga = df_liga.reset_index()
            
        team_col = None
        possible_cols = ["team", "Team", "equipo", "Equipo", "Team Name", "Squad"]
        for col_name in possible_cols:
            if col_name in df_liga.columns:
                team_col = col_name
                break
        
        if team_col:
            df_liga = df_liga[~df_liga[team_col].str.contains("Cibao", case=False, na=False)]
            
        for col in cols:
            if col in df_liga.columns:
                df_liga[col] = pd.to_numeric(df_liga[col], errors="coerce").fillna(0)
        liga_means = df_liga[cols].mean()
        
        # Preparar datos para gráfico de barras agrupadas
        data_list = []
        for label, col in pares:
            # Valor Cibao
            data_list.append({
                "Métrica": label,
                "Valor": mean_vals[col],
                "Equipo": "Cibao FC"
            })
            # Valor Liga
            data_list.append({
                "Métrica": label,
                "Valor": liga_means[col] if col in liga_means else 0,
                "Equipo": "Promedio Liga"
            })
            
        df_plot = pd.DataFrame(data_list)

        fig = px.bar(
            df_plot,
            x="Valor",
            y="Métrica",
            color="Equipo",
            barmode="group",
            orientation="h",
            text_auto=".2f",
            color_discrete_map={
                "Cibao FC": CIBAO_ORANGE,
                "Promedio Liga": "#00D9FF"
            },
            height=400,
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
                x=1
            ),
            xaxis_title="",
            yaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Conclusiones Tácticas
        df_diff = df_plot.pivot(index="Métrica", columns="Equipo", values="Valor")
        if not df_diff.empty and "Cibao FC" in df_diff.columns and "Promedio Liga" in df_diff.columns:
            df_diff["Diff"] = df_diff["Cibao FC"] - df_diff["Promedio Liga"]
            
            max_diff_metric = df_diff["Diff"].idxmax()
            min_diff_metric = df_diff["Diff"].idxmin()
            
            val_cibao_max = df_diff.loc[max_diff_metric, "Cibao FC"]
            val_liga_max = df_diff.loc[max_diff_metric, "Promedio Liga"]
            
            val_cibao_min = df_diff.loc[min_diff_metric, "Cibao FC"]
            val_liga_min = df_diff.loc[min_diff_metric, "Promedio Liga"]

            st.markdown(
                f"""
                <div style='background:#111; padding:12px; border-left:3px solid {CIBAO_ORANGE};
                            margin-top:-8px; margin-bottom:24px; border-radius:6px;'>
                    <b>Conclusiones tácticas</b><br><br>
                    • <b>Punto fuerte:</b> mayor producción en <b>{max_diff_metric}</b> ({val_cibao_max:.2f} vs Liga: {val_liga_max:.2f}).<br>
                    • <b>Área a seguir:</b> menor incidencia en <b>{min_diff_metric}</b> ({val_cibao_min:.2f} vs Liga: {val_liga_min:.2f}).<br>
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
            Aquí podrás incorporar las tablas comparativas o cualquier reporte final que quieras mostrar.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.info("Pendiente de integrar las tablas dinámicas para Copa Concacaf.")
