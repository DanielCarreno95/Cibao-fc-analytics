# ===========================================
# 7_Comparacion_de_Equipos.py — Comparación de Equipos
# ===========================================
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import csv

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

# === IMPORTA EL TEMA OSCURO GLOBAL + TÍTULOS NARANJA ===
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja

# ===========================================
# COLORES DE EQUIPOS
# ===========================================
def load_team_colors():
    """Carga los colores de los equipos desde el CSV."""
    colors = {}
    color_file = Path(__file__).resolve().parent.parent / "assets" / "Esquema de Colores.csv"
    try:
        with open(color_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                team_name = row['Equipo'].strip()
                hex_color = row['Hex Color'].strip()
                if not hex_color.startswith('#'):
                    hex_color = '#' + hex_color
                colors[team_name] = hex_color
    except Exception as e:
        st.warning(f"No se pudo cargar el archivo de colores: {e}")
        colors['Cibao'] = '#FF9900'
    return colors

TEAM_COLORS = load_team_colors()
CIBAO_COLOR = TEAM_COLORS.get('Cibao', '#FF9900')
CIBAO_TEAM_NAME = "Cibao"

# ===========================================
# CONFIGURACIÓN
# ===========================================
st.set_page_config(
    page_title="Comparación de Equipos | Cibao FC",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_dark_theme()

# ===========================================
# FUNCIONES DE CARGA DE DATOS (reutilizadas)
# ===========================================
def load_all_matches() -> List[Dict]:
    """Carga todos los partidos desde archivos JSON."""
    matches = []
    data_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "concacaf" / "matchstats"
    
    if not data_dir.exists():
        return matches
    
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
                matches.append(match_data)
        except Exception as e:
            continue
    
    return matches

def extract_match_info(match_data: Dict) -> Optional[Dict]:
    """Extrae información básica del partido."""
    try:
        match_info = match_data.get("matchInfo", {})
        match_details = match_data.get("liveData", {}).get("matchDetails", {})
        
        contestants = match_info.get("contestant", [])
        if len(contestants) < 2:
            return None
        
        home_team = None
        away_team = None
        for contestant in contestants:
            position = contestant.get("position", "").lower()
            name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
            if position == "home":
                home_team = name
            elif position == "away":
                away_team = name
        
        if not home_team and contestants:
            home_team = contestants[0].get("name") or contestants[0].get("shortName", "")
        if not away_team and len(contestants) > 1:
            away_team = contestants[1].get("name") or contestants[1].get("shortName", "")
        
        match_date_str = match_info.get("localDate", "")
        match_date = None
        if match_date_str:
            try:
                match_date = datetime.strptime(match_date_str, "%Y-%m-%d")
            except:
                pass
        
        return {
            "match_id": match_info.get("id", ""),
            "date": match_date,
            "date_str": match_date_str,
            "home_team": home_team,
            "away_team": away_team,
            "match_data": match_data
        }
    except Exception as e:
        return None

def extract_team_stats_from_match(match_data: Dict, team_name: str) -> Optional[Dict]:
    """Extrae estadísticas de un equipo específico de un partido."""
    try:
        live_data = match_data.get("liveData", {})
        lineups = live_data.get("lineUp", [])
        
        team_lineup = None
        team_name_lower = team_name.lower().strip()
        team_base = team_name_lower.replace(' fc', '').strip()
        
        for lineup in lineups:
            contestant_id = lineup.get("contestantId", "")
            match_info = match_data.get("matchInfo", {})
            contestants = match_info.get("contestant", [])
            
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    name_lower = name.lower().strip() if name else ""
                    name_base = name_lower.replace(' fc', '').strip()
                    
                    if (team_name_lower in name_lower or 
                        name_lower in team_name_lower or
                        team_base in name_base or
                        name_base in team_base):
                        team_lineup = lineup
                        break
            
            if team_lineup:
                break
        
        if not team_lineup:
            return None
        
        stats_list = team_lineup.get("stat", [])
        stats_dict = {}
        
        for stat in stats_list:
            stat_type = stat.get("type", "")
            value = stat.get("value", "0")
            try:
                if isinstance(value, str):
                    stats_dict[stat_type] = float(value)
                else:
                    stats_dict[stat_type] = value
            except:
                stats_dict[stat_type] = 0
        
        return stats_dict
    except Exception as e:
        return None

def get_team_matches_data(all_matches: List[Dict], team_name: str) -> List[Dict]:
    """Obtiene todos los partidos donde aparece el equipo."""
    team_matches = []
    seen_match_ids = set()
    
    team_name_lower = team_name.lower().strip()
    team_base = team_name_lower.replace(' fc', '').strip()
    
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if not match_info:
            continue
        
        match_id = match_info.get("match_id", "")
        if match_id in seen_match_ids:
            continue
        seen_match_ids.add(match_id)
        
        home = match_info.get("home_team", "")
        away = match_info.get("away_team", "")
        
        home_lower = home.lower().strip() if home else ""
        away_lower = away.lower().strip() if away else ""
        
        home_match = (team_name_lower in home_lower or 
                     home_lower in team_name_lower or
                     team_base in home_lower.replace(' fc', '').strip() or
                     home_lower.replace(' fc', '').strip() in team_base)
        
        away_match = (team_name_lower in away_lower or 
                     away_lower in team_name_lower or
                     team_base in away_lower.replace(' fc', '').strip() or
                     away_lower.replace(' fc', '').strip() in team_base)
        
        if home_match or away_match:
            team_stats = extract_team_stats_from_match(match_data, team_name)
            if team_stats:
                match_info["team_stats"] = team_stats
            team_matches.append(match_info)
    
    return team_matches

def get_all_teams_from_matches(all_matches: List[Dict]) -> List[str]:
    """Obtiene lista de todos los equipos únicos."""
    teams = set()
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if match_info:
            home = match_info.get("home_team", "")
            away = match_info.get("away_team", "")
            if home:
                teams.add(home)
            if away:
                teams.add(away)
    return sorted(list(teams))

def calculate_team_average_metrics(team_matches: List[Dict]) -> Dict[str, float]:
    """Calcula promedios de métricas para un equipo."""
    if not team_matches:
        return {}
    
    metrics_to_sum = {
        "goals": 0,
        "goalsConceded": 0,
        "totalScoringAtt": 0,
        "ontargetScoringAtt": 0,
        "wonCorners": 0,
        "lostCorners": 0,
        "fkFoulWon": 0,
        "fkFoulLost": 0,
        "totalYellowCard": 0,
        "totalRedCard": 0,
        "saves": 0,
        "possessionPercentage": 0,
        "totalPass": 0,
        "accuratePass": 0,
        "totalTackle": 0,
        "wonTackle": 0,
        "totalClearance": 0,
        "interception": 0,
    }
    
    match_count = 0
    
    for match in team_matches:
        stats = match.get("team_stats", {})
        if not stats:
            continue
        
        match_count += 1
        for metric in metrics_to_sum:
            value = stats.get(metric, 0)
            try:
                metrics_to_sum[metric] += float(value)
            except:
                pass
    
    if match_count == 0:
        return {}
    
    averages = {}
    for metric, total in metrics_to_sum.items():
        averages[metric] = total / match_count
    
    # Calcular métricas derivadas
    if averages.get("totalPass", 0) > 0:
        pass_accuracy = (averages.get("accuratePass", 0) / averages["totalPass"]) * 100
        averages["passAccuracy"] = round(pass_accuracy, 1)
    else:
        averages["passAccuracy"] = 0
    
    if averages.get("totalTackle", 0) > 0:
        tackle_success = (averages.get("wonTackle", 0) / averages["totalTackle"]) * 100
        averages["tackleSuccess"] = round(tackle_success, 1)
    else:
        averages["tackleSuccess"] = 0
    
    if averages.get("totalScoringAtt", 0) > 0:
        shot_accuracy = (averages.get("ontargetScoringAtt", 0) / averages["totalScoringAtt"]) * 100
        averages["shotAccuracy"] = round(shot_accuracy, 1)
    else:
        averages["shotAccuracy"] = 0
    
    for key, value in averages.items():
        if isinstance(value, float):
            averages[key] = round(value, 2)
    
    return averages

# ===========================================
# DEFINICIÓN DE MÉTRICAS Y TIPOS DE GRÁFICOS
# ===========================================
METRIC_DEFINITIONS = {
    "Goles por Partido": {
        "key": "goals",
        "chart_type": "bar",
        "unit": "goles",
        "category": "Ofensiva"
    },
    "Goles Recibidos por Partido": {
        "key": "goalsConceded",
        "chart_type": "bar",
        "unit": "goles",
        "category": "Defensiva",
        "invert": True  # Menos es mejor
    },
    "Disparos por Partido": {
        "key": "totalScoringAtt",
        "chart_type": "bar",
        "unit": "disparos",
        "category": "Ofensiva"
    },
    "Disparos al Arco por Partido": {
        "key": "ontargetScoringAtt",
        "chart_type": "bar",
        "unit": "disparos",
        "category": "Ofensiva"
    },
    "Precisión de Disparos": {
        "key": "shotAccuracy",
        "chart_type": "bar",
        "unit": "%",
        "category": "Ofensiva"
    },
    "Posesión": {
        "key": "possessionPercentage",
        "chart_type": "gauge",
        "unit": "%",
        "category": "Control"
    },
    "Pases Totales por Partido": {
        "key": "totalPass",
        "chart_type": "bar",
        "unit": "pases",
        "category": "Control"
    },
    "Pases Precisos por Partido": {
        "key": "accuratePass",
        "chart_type": "bar",
        "unit": "pases",
        "category": "Control"
    },
    "Precisión de Pases": {
        "key": "passAccuracy",
        "chart_type": "bar",
        "unit": "%",
        "category": "Control"
    },
    "Corners Ganados por Partido": {
        "key": "wonCorners",
        "chart_type": "bar",
        "unit": "corners",
        "category": "Set Pieces"
    },
    "Corners Recibidos por Partido": {
        "key": "lostCorners",
        "chart_type": "bar",
        "unit": "corners",
        "category": "Set Pieces",
        "invert": True
    },
    "Tackles Totales por Partido": {
        "key": "totalTackle",
        "chart_type": "bar",
        "unit": "tackles",
        "category": "Defensiva"
    },
    "Tackles Exitosos por Partido": {
        "key": "wonTackle",
        "chart_type": "bar",
        "unit": "tackles",
        "category": "Defensiva"
    },
    "Efectividad de Tackles": {
        "key": "tackleSuccess",
        "chart_type": "bar",
        "unit": "%",
        "category": "Defensiva"
    },
    "Despejes por Partido": {
        "key": "totalClearance",
        "chart_type": "bar",
        "unit": "despejes",
        "category": "Defensiva"
    },
    "Intercepciones por Partido": {
        "key": "interception",
        "chart_type": "bar",
        "unit": "intercepciones",
        "category": "Defensiva"
    },
    "Atajadas por Partido": {
        "key": "saves",
        "chart_type": "bar",
        "unit": "atajadas",
        "category": "Defensiva"
    },
    "Faltas Cometidas por Partido": {
        "key": "fkFoulLost",
        "chart_type": "bar",
        "unit": "faltas",
        "category": "Disciplina",
        "invert": True
    },
    "Faltas Recibidas por Partido": {
        "key": "fkFoulWon",
        "chart_type": "bar",
        "unit": "faltas",
        "category": "Disciplina"
    },
    "Tarjetas Amarillas por Partido": {
        "key": "totalYellowCard",
        "chart_type": "bar",
        "unit": "tarjetas",
        "category": "Disciplina",
        "invert": True
    },
    "Tarjetas Rojas por Partido": {
        "key": "totalRedCard",
        "chart_type": "bar",
        "unit": "tarjetas",
        "category": "Disciplina",
        "invert": True
    },
}

# ===========================================
# FUNCIONES DE RENDERIZADO DE GRÁFICOS
# ===========================================
def create_bar_chart(teams_data: Dict[str, Dict], metric_name: str, metric_key: str, unit: str = "") -> go.Figure:
    """Crea un gráfico de barras comparativo."""
    teams = list(teams_data.keys())
    values = [teams_data[team].get(metric_key, 0) for team in teams]
    colors = [TEAM_COLORS.get(team, '#888888') for team in teams]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=teams,
        y=values,
        marker_color=colors,
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(size=14, color='white')
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        title=f"{metric_name}",
        xaxis_title="Equipos",
        yaxis_title=f"{metric_name} ({unit})" if unit else metric_name,
        showlegend=False,
        font=dict(size=12, color='white'),
        xaxis=dict(tickangle=-45 if len(teams) > 3 else 0)
    )
    
    return fig

def create_gauge_chart(teams_data: Dict[str, Dict], metric_name: str, metric_key: str, unit: str = "%") -> go.Figure:
    """Crea gráficos de gauge (uno por equipo)."""
    teams = list(teams_data.keys())
    n_teams = len(teams)
    
    # Determinar layout de subplots
    if n_teams == 1:
        rows, cols = 1, 1
    elif n_teams == 2:
        rows, cols = 1, 2
    elif n_teams <= 4:
        rows, cols = 2, 2
    else:
        rows = (n_teams + 2) // 3
        cols = 3
    
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=rows, cols=cols,
        specs=[[{"type": "indicator"}] * cols for _ in range(rows)],
        subplot_titles=teams,
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    max_val = max([teams_data[team].get(metric_key, 0) for team in teams] + [100])
    
    for idx, team in enumerate(teams):
        row = (idx // cols) + 1
        col = (idx % cols) + 1
        value = teams_data[team].get(metric_key, 0)
        color = TEAM_COLORS.get(team, '#888888')
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{value:.1f}{unit}"},
                gauge={
                    'axis': {'range': [None, max_val]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, max_val * 0.5], 'color': "lightgray"},
                        {'range': [max_val * 0.5, max_val * 0.8], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_val * 0.9
                    }
                }
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300 * rows,
        title=f"{metric_name}",
        font=dict(size=12, color='white')
    )
    
    return fig

def create_scatter_chart(teams_data: Dict[str, Dict], metric_x: str, metric_y: str, 
                         metric_x_key: str, metric_y_key: str, 
                         metric_x_name: str, metric_y_name: str) -> go.Figure:
    """Crea un gráfico de dispersión para comparar dos métricas."""
    teams = list(teams_data.keys())
    x_values = [teams_data[team].get(metric_x_key, 0) for team in teams]
    y_values = [teams_data[team].get(metric_y_key, 0) for team in teams]
    colors = [TEAM_COLORS.get(team, '#888888') for team in teams]
    
    fig = go.Figure()
    
    for i, team in enumerate(teams):
        fig.add_trace(go.Scatter(
            x=[x_values[i]],
            y=[y_values[i]],
            mode='markers+text',
            name=team,
            marker=dict(
                size=15,
                color=colors[i],
                line=dict(width=2, color='white')
            ),
            text=team,
            textposition="top center",
            textfont=dict(size=11, color='white')
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        title=f"{metric_x_name} vs {metric_y_name}",
        xaxis_title=metric_x_name,
        yaxis_title=metric_y_name,
        showlegend=False,
        font=dict(size=12, color='white')
    )
    
    return fig

def render_chart_for_metric(teams_data: Dict[str, Dict], metric_name: str, metric_def: Dict) -> None:
    """Renderiza el gráfico apropiado para una métrica."""
    metric_key = metric_def["key"]
    chart_type = metric_def["chart_type"]
    unit = metric_def.get("unit", "")
    
    if chart_type == "bar":
        fig = create_bar_chart(teams_data, metric_name, metric_key, unit)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "gauge":
        fig = create_gauge_chart(teams_data, metric_name, metric_key, unit)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Default to bar
        fig = create_bar_chart(teams_data, metric_name, metric_key, unit)
        st.plotly_chart(fig, use_container_width=True)

def render_multiple_metrics_chart(teams_data: Dict[str, Dict], selected_metrics: List[str]) -> None:
    """Renderiza un gráfico combinado para múltiples métricas."""
    teams = list(teams_data.keys())
    colors = [TEAM_COLORS.get(team, '#888888') for team in teams]
    
    fig = go.Figure()
    
    for i, team in enumerate(teams):
        values = []
        metric_labels = []
        
        for metric_name in selected_metrics:
            if metric_name in METRIC_DEFINITIONS:
                metric_key = METRIC_DEFINITIONS[metric_name]["key"]
                value = teams_data[team].get(metric_key, 0)
                values.append(value)
                metric_labels.append(metric_name)
        
        fig.add_trace(go.Bar(
            name=team,
            x=metric_labels,
            y=values,
            marker_color=colors[i],
            text=[f"{v:.2f}" for v in values],
            textposition='outside'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        title="Comparación de Múltiples Métricas",
        xaxis_title="Métricas",
        yaxis_title="Valor",
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(tickangle=-45),
        font=dict(size=12, color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ===========================================
# INTERFAZ PRINCIPAL
# ===========================================
def main():
    st.markdown("""
    <h1 style='text-align:center; color:#FF9900; text-shadow: 0 0 15px rgba(255,153,0,0.65); font-weight:900;'>
        Comparación de Equipos
    </h1>
    <p style='text-align:center; color:#D1D5DB; font-size:17px;'>
        Compare métricas entre múltiples equipos con visualizaciones personalizadas
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner("Cargando datos de partidos..."):
        all_matches = load_all_matches()
    
    if not all_matches:
        st.error("No se encontraron partidos. Verifique que los archivos JSON estén en la carpeta correcta.")
        return
    
    # Sidebar: Selectores
    with st.sidebar:
        st.markdown("""
        <h3 style='margin-top:0; color:#ff7b00;'>Configuración</h3>
        <hr style='margin-top:6px; margin-bottom:20px; opacity:0.3;'>
        """, unsafe_allow_html=True)
        
        # Obtener todos los equipos
        all_teams = get_all_teams_from_matches(all_matches)
        
        # Selector de equipos (multi-select)
        st.markdown("**Seleccionar Equipos:**")
        selected_teams = st.multiselect(
            "Equipos a comparar",
            options=all_teams,
            default=[CIBAO_TEAM_NAME] if CIBAO_TEAM_NAME in all_teams else [all_teams[0]] if all_teams else [],
            key="team_selector",
            label_visibility="collapsed"
        )
        
        if not selected_teams:
            st.warning("Por favor seleccione al menos un equipo.")
            return
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Selector de métricas (multi-select)
        st.markdown("**Seleccionar Métricas:**")
        
        # Agrupar métricas por categoría
        metrics_by_category = {}
        for metric_name, metric_def in METRIC_DEFINITIONS.items():
            category = metric_def.get("category", "Otros")
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append(metric_name)
        
        # Crear opciones con categorías
        metric_options = []
        for category, metrics in sorted(metrics_by_category.items()):
            metric_options.extend(metrics)
        
        selected_metrics = st.multiselect(
            "Métricas a comparar",
            options=metric_options,
            default=["Goles por Partido", "Posesión", "Precisión de Pases"],
            key="metric_selector",
            label_visibility="collapsed"
        )
        
        if not selected_metrics:
            st.warning("Por favor seleccione al menos una métrica.")
            return
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Opción de visualización
        display_mode = st.radio(
            "Modo de visualización",
            ["Individual (un gráfico por métrica)", "Combinado (todas las métricas en un gráfico)"],
            key="display_mode"
        )
    
    # Calcular métricas para cada equipo seleccionado
    teams_data = {}
    
    with st.spinner("Calculando métricas..."):
        for team_name in selected_teams:
            team_matches = get_team_matches_data(all_matches, team_name)
            if team_matches:
                team_metrics = calculate_team_average_metrics(team_matches)
                teams_data[team_name] = team_metrics
    
    if not teams_data:
        st.error("No se pudieron calcular métricas para los equipos seleccionados.")
        return
    
    # Mostrar resultados
    st.markdown("---")
    
    if display_mode == "Individual (un gráfico por métrica)":
        # Mostrar un gráfico por cada métrica seleccionada
        for metric_name in selected_metrics:
            if metric_name in METRIC_DEFINITIONS:
                metric_def = METRIC_DEFINITIONS[metric_name]
                st.markdown(f"### {metric_name}")
                render_chart_for_metric(teams_data, metric_name, metric_def)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        # Mostrar todas las métricas en un gráfico combinado
        render_multiple_metrics_chart(teams_data, selected_metrics)
    
    # Tabla de resumen
    st.markdown("---")
    st.markdown("### Resumen de Métricas")
    
    summary_data = []
    for team_name in selected_teams:
        row = {"Equipo": team_name}
        for metric_name in selected_metrics:
            if metric_name in METRIC_DEFINITIONS:
                metric_key = METRIC_DEFINITIONS[metric_name]["key"]
                unit = METRIC_DEFINITIONS[metric_name].get("unit", "")
                value = teams_data[team_name].get(metric_key, 0)
                row[metric_name] = f"{value:.2f} {unit}" if unit else f"{value:.2f}"
        summary_data.append(row)
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()




