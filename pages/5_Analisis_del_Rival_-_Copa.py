# ===========================================
# 5_Analisis_del_Rival_-_Copa.py — Análisis del Rival - Copa Concacaf
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
                # Asegurar que el color tenga el formato correcto
                if not hex_color.startswith('#'):
                    hex_color = '#' + hex_color
                colors[team_name] = hex_color
    except Exception as e:
        st.warning(f"No se pudo cargar el archivo de colores: {e}")
        # Color por defecto para Cibao
        colors['Cibao'] = '#FF9900'
    return colors

TEAM_COLORS = load_team_colors()
CIBAO_COLOR = TEAM_COLORS.get('Cibao', '#FF9900')  # Color oficial de Cibao

# ===========================================
# CONFIGURACIÓN
# ===========================================
st.set_page_config(
    page_title="Análisis del Rival - Copa Concacaf | Cibao FC",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ACTIVAR TEMA OSCURO GLOBAL ----------
inject_dark_theme()

# ===========================================
# ESTILOS ADICIONALES - TEXTO MÁS GRANDE PARA LEGIBILIDAD
# ===========================================
st.markdown("""
<style>
    /* Texto general del cuerpo - mantener grande para legibilidad */
    .stApp {
        font-size: 1.3rem !important;
    }
    
    /* Párrafos y texto general */
    p, div, span, label {
        font-size: 1.3rem !important;
    }
    
    /* Tablas */
    .stDataFrame {
        font-size: 1.4rem !important;
    }
    
    .stDataFrame table {
        font-size: 1.4rem !important;
    }
    
    .stDataFrame th {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        padding: 12px !important;
    }
    
    .stDataFrame td {
        font-size: 1.4rem !important;
        padding: 10px !important;
    }
    
    /* Métricas de Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.4rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.3rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        font-size: 1.3rem !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 1.6rem !important;
    }
    
    /* Selectores y controles */
    .stSelectbox label,
    .stRadio label,
    .stMultiselect label {
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox [class*="selectbox"],
    .stRadio [class*="radio"],
    .stMultiselect [class*="multiselect"] {
        font-size: 1.3rem !important;
    }
    
    /* Info boxes y warnings */
    .stInfo, .stWarning, .stError, .stSuccess {
        font-size: 1.3rem !important;
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 12px 24px;
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Botones */
    .stButton button {
        font-size: 1.3rem !important;
        padding: 0.5rem 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ===========================================
# RUTAS DE DATOS
# ===========================================
REPO_ROOT = Path(__file__).parents[1]
MATCHSTATS_DIR = REPO_ROOT / "data" / "raw" / "concacaf" / "matchstats"
MATCHES_DIR = REPO_ROOT / "data" / "raw" / "concacaf" / "matches"
CIBAO_TEAM_NAME = "Cibao"

# ===========================================
# FUNCIONES DE CARGA DE DATOS
# ===========================================

@st.cache_data
def load_all_matches() -> List[Dict]:
    """Carga todos los partidos desde los archivos JSON."""
    matches = []
    
    # Cargar desde matchstats
    if MATCHSTATS_DIR.exists():
        for json_file in MATCHSTATS_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    matches.append(data)
            except Exception as e:
                st.warning(f"⚠️ Error cargando {json_file.name}: {e}")
                continue
    
    return matches


def extract_match_info(match_data: Dict) -> Optional[Dict]:
    """Extrae información clave de un partido."""
    try:
        match_info = match_data.get("matchInfo", {})
        live_data = match_data.get("liveData", {})
        match_details = live_data.get("matchDetails", {})
        
        # Obtener equipos
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
        
        # Si no hay posición, usar orden
        if not home_team and contestants:
            home_team = contestants[0].get("name") or contestants[0].get("shortName", "")
        if not away_team and len(contestants) > 1:
            away_team = contestants[1].get("name") or contestants[1].get("shortName", "")
        
        # Obtener fecha
        match_date_str = match_info.get("localDate", "")
        match_date = None
        if match_date_str:
            try:
                match_date = datetime.strptime(match_date_str, "%Y-%m-%d")
            except:
                pass
        
        # Estado del partido
        match_status_raw = match_details.get("matchStatus", "Scheduled")
        # Traducir estados comunes
        status_translation = {
            "Scheduled": "Programado",
            "Played": "Jugado",
            "Finished": "Finalizado",
            "FT": "Finalizado",
            "Not Started": "No Iniciado"
        }
        match_status = status_translation.get(match_status_raw, match_status_raw)
        
        # Si el status está vacío o es Unknown, verificar si hay score (indica que fue jugado)
        if not match_status or match_status == "Unknown" or match_status == {}:
            scores = match_details.get("scores", {})
            if scores and (scores.get("ft") or scores.get("total")):
                match_status = "Jugado"  # Si hay score, el partido fue jugado
        
        return {
            "match_id": match_info.get("id", ""),
            "date": match_date,
            "date_str": match_date_str,
            "home_team": home_team,
            "away_team": away_team,
            "status": match_status,
            "description": match_info.get("description", f"{home_team} vs {away_team}"),
            "match_data": match_data  # Guardar datos completos
        }
    except Exception as e:
        return None


def get_cibao_matches(matches: List[Dict]) -> List[Dict]:
    """Filtra partidos donde juega Cibao."""
    cibao_matches = []
    
    for match_data in matches:
        match_info = extract_match_info(match_data)
        if not match_info:
            continue
        
        # Verificar si Cibao juega en este partido
        home = match_info["home_team"] or ""
        away = match_info["away_team"] or ""
        
        if CIBAO_TEAM_NAME.lower() in home.lower() or CIBAO_TEAM_NAME.lower() in away.lower():
            # Identificar el oponente
            if CIBAO_TEAM_NAME.lower() in home.lower():
                opponent = away
                is_home = True
            else:
                opponent = home
                is_home = False
            
            match_info["opponent"] = opponent
            match_info["is_home"] = is_home
            cibao_matches.append(match_info)
    
    return cibao_matches


def get_upcoming_opponents(cibao_matches: List[Dict]) -> List[Tuple[str, Dict]]:
    """Identifica próximos oponentes basado en partidos no jugados o próximos."""
    today = datetime.now()
    
    # Separar partidos jugados y no jugados
    played_matches = []
    upcoming_matches = []
    
    for match in cibao_matches:
        status = match.get("status", "").lower()
        match_date = match.get("date")
        
        # Si el partido ya se jugó
        if status in ["played", "finished", "ft", "jugado", "finalizado"]:
            played_matches.append(match)
        # Si está programado o es futuro
        elif status in ["scheduled", "not started", "programado", "no iniciado", ""] or (match_date and match_date > today):
            upcoming_matches.append(match)
        # Si no hay status claro, verificar por fecha
        elif match_date and match_date > today:
            upcoming_matches.append(match)
        else:
            played_matches.append(match)
    
    # Ordenar partidos futuros por fecha
    upcoming_matches.sort(key=lambda x: x.get("date") or datetime.max)
    
    # Crear lista de oponentes únicos (próximos)
    opponents_dict = {}
    for match in upcoming_matches:
        opponent = match.get("opponent", "Desconocido")
        if opponent not in opponents_dict:
            opponents_dict[opponent] = match
    
    # Si no hay partidos futuros, usar el último oponente o todos los oponentes únicos
    if not opponents_dict:
        # Usar todos los oponentes únicos de partidos jugados
        for match in played_matches:
            opponent = match.get("opponent", "Desconocido")
            if opponent and opponent not in opponents_dict:
                opponents_dict[opponent] = match
    
    # Convertir a lista de tuplas (nombre, match_info)
    opponents_list = [(name, info) for name, info in opponents_dict.items()]
    opponents_list.sort(key=lambda x: x[1].get("date") or datetime.min, reverse=True)
    
    return opponents_list


def get_all_opponents(cibao_matches: List[Dict]) -> List[str]:
    """Obtiene lista de todos los oponentes únicos."""
    opponents = set()
    for match in cibao_matches:
        opponent = match.get("opponent")
        if opponent:
            opponents.add(opponent)
    return sorted(list(opponents))


def get_all_teams_from_matches(all_matches: List[Dict]) -> List[str]:
    """Obtiene lista de todos los equipos únicos de todos los partidos."""
    teams = set()
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if match_info:
            home_team = match_info.get("home_team")
            away_team = match_info.get("away_team")
            if home_team:
                teams.add(home_team)
            if away_team:
                teams.add(away_team)
    return sorted(list(teams))


def filter_matches_by_type(matches: List[Dict], team_name: str, filter_type: str, all_matches: List[Dict] = None) -> List[Dict]:
    """Filtra partidos por tipo: 'all', 'home', 'away', 'vs_cibao'."""
    if filter_type == "all":
        return matches
    
    filtered = []
    cibao_name_lower = "Cibao".lower().strip()
    cibao_base = cibao_name_lower.replace(' fc', '').strip()
    team_name_lower = team_name.lower().strip()
    team_base = team_name_lower.replace(' fc', '').strip()
    
    for match in matches:
        # Los matches ya tienen la estructura de match_info (con home_team, away_team, etc.)
        match_info = match
        
        if not match_info:
            continue
        
        home = match_info.get("home_team", "")
        away = match_info.get("away_team", "")
        
        # Convertir a string y normalizar
        home_str = str(home).lower().strip() if home else ""
        away_str = str(away).lower().strip() if away else ""
        
        if filter_type == "home":
            # Solo partidos en casa
            home_match = (team_name_lower in home_str or home_str in team_name_lower or
                         team_base in home_str.replace(' fc', '').strip() or
                         home_str.replace(' fc', '').strip() in team_base)
            if home_match:
                filtered.append(match)
        
        elif filter_type == "away":
            # Solo partidos fuera
            away_match = (team_name_lower in away_str or away_str in team_name_lower or
                         team_base in away_str.replace(' fc', '').strip() or
                         away_str.replace(' fc', '').strip() in team_base)
            if away_match:
                filtered.append(match)
        
        elif filter_type == "vs_cibao":
            # Solo partidos contra Cibao
            home_match_cibao = (cibao_name_lower in home_str or home_str in cibao_name_lower or
                               cibao_base in home_str.replace(' fc', '').strip() or
                               home_str.replace(' fc', '').strip() in cibao_base)
            away_match_cibao = (cibao_name_lower in away_str or away_str in cibao_name_lower or
                               cibao_base in away_str.replace(' fc', '').strip() or
                               away_str.replace(' fc', '').strip() in cibao_base)
            home_match_team = (team_name_lower in home_str or home_str in team_name_lower or
                              team_base in home_str.replace(' fc', '').strip() or
                              home_str.replace(' fc', '').strip() in team_base)
            away_match_team = (team_name_lower in away_str or away_str in team_name_lower or
                              team_base in away_str.replace(' fc', '').strip() or
                              away_str.replace(' fc', '').strip() in team_base)
            
            if (home_match_cibao or away_match_cibao) and (home_match_team or away_match_team):
                filtered.append(match)
    
    return filtered


def extract_team_stats_from_match(match_data: Dict, team_name: str) -> Optional[Dict]:
    """Extrae estadísticas de un equipo específico de un partido."""
    try:
        live_data = match_data.get("liveData", {})
        lineups = live_data.get("lineUp", [])
        
        # Buscar el lineup del equipo
        team_lineup = None
        team_name_lower = team_name.lower().strip()
        team_base = team_name_lower.replace(' fc', '').strip()
        
        for lineup in lineups:
            contestant_id = lineup.get("contestantId", "")
            # Verificar si este lineup corresponde al equipo
            match_info = match_data.get("matchInfo", {})
            contestants = match_info.get("contestant", [])
            
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    # Matching más flexible: verificar si el nombre del equipo está en el nombre del contestant o viceversa
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
        
        # Extraer estadísticas
        stats_list = team_lineup.get("stat", [])
        stats_dict = {}
        
        for stat in stats_list:
            stat_type = stat.get("type", "")
            value = stat.get("value", "0")
            
            # Convertir a número si es posible
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


def get_opponent_matches_data(all_matches: List[Dict], opponent_name: str) -> List[Dict]:
    """Obtiene todos los partidos donde aparece el oponente (no solo contra Cibao)."""
    opponent_matches = []
    seen_match_ids = set()  # Para evitar duplicados
    
    # Normalizar nombre del oponente para matching más flexible
    opponent_name_lower = opponent_name.lower().strip()
    # Remover sufijos comunes para matching más flexible
    opponent_base = opponent_name_lower.replace(' fc', '').replace(' fc', '').strip()
    
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if not match_info:
            continue
        
        match_id = match_info.get("match_id", "")
        
        # Evitar duplicados usando match_id
        if match_id in seen_match_ids:
            continue
        seen_match_ids.add(match_id)
        
        home = match_info.get("home_team", "")
        away = match_info.get("away_team", "")
        
        # Verificar si el oponente juega en este partido (matching más flexible)
        home_lower = home.lower().strip() if home else ""
        away_lower = away.lower().strip() if away else ""
        
        # Matching: verificar si el nombre del oponente está en el nombre del equipo o viceversa
        home_match = (opponent_name_lower in home_lower or 
                     home_lower in opponent_name_lower or
                     opponent_base in home_lower.replace(' fc', '').strip() or
                     home_lower.replace(' fc', '').strip() in opponent_base)
        
        away_match = (opponent_name_lower in away_lower or 
                     away_lower in opponent_name_lower or
                     opponent_base in away_lower.replace(' fc', '').strip() or
                     away_lower.replace(' fc', '').strip() in opponent_base)
        
        if home_match or away_match:
            # Extraer estadísticas del oponente (si están disponibles)
            opponent_stats = extract_team_stats_from_match(match_data, opponent_name)
            if opponent_stats:
                match_info["opponent_stats"] = opponent_stats
            # Agregar el partido incluso si no hay estadísticas (para contar partidos jugados)
            opponent_matches.append(match_info)
    
    return opponent_matches


def get_cibao_average_metrics(all_matches: List[Dict]) -> Dict[str, float]:
    """Calcula promedios de métricas clave para Cibao."""
    cibao_matches = []
    
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if not match_info:
            continue
        
        home = match_info.get("home_team", "")
        away = match_info.get("away_team", "")
        
        # Verificar si Cibao juega en este partido
        if CIBAO_TEAM_NAME.lower() in home.lower() or CIBAO_TEAM_NAME.lower() in away.lower():
            cibao_stats = extract_team_stats_from_match(match_data, CIBAO_TEAM_NAME)
            if cibao_stats:
                match_info["cibao_stats"] = cibao_stats
                cibao_matches.append(match_info)
    
    return calculate_average_metrics_from_matches(cibao_matches, "cibao_stats")


def calculate_average_metrics(opponent_matches: List[Dict]) -> Dict[str, float]:
    """Calcula promedios de métricas clave para el oponente."""
    return calculate_average_metrics_from_matches(opponent_matches, "opponent_stats")


def get_all_teams_average_metrics(all_matches: List[Dict], filter_type: str = "all", opponent_name: str = None) -> Dict[str, float]:
    """Calcula promedios de métricas clave para todos los equipos en la competencia, opcionalmente filtrados."""
    all_teams_stats = []
    
    # Obtener todos los equipos únicos
    all_teams = get_all_teams_from_matches(all_matches)
    
    # Para cada equipo, obtener sus partidos y estadísticas
    for team_name in all_teams:
        team_matches = get_opponent_matches_data(all_matches, team_name)
        
        # Aplicar filtro si es necesario
        if filter_type != "all":
            if filter_type == "vs_cibao":
                # Para "vs_cibao", filtrar partidos donde el equipo jugó contra Cibao
                team_matches = filter_matches_by_type(team_matches, team_name, filter_type, all_matches)
            else:
                # Para otros filtros (home, away)
                team_matches = filter_matches_by_type(team_matches, team_name, filter_type, all_matches)
        
        for match in team_matches:
            stats = match.get("opponent_stats", {})
            if stats:
                all_teams_stats.append(stats)
    
    # Calcular promedios de todas las estadísticas
    if not all_teams_stats:
        return {}
    
    # Métricas a calcular
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
    }
    
    match_count = len(all_teams_stats)
    
    for stats in all_teams_stats:
        for metric in metrics_to_sum:
            value = stats.get(metric, 0)
            try:
                metrics_to_sum[metric] += float(value)
            except:
                pass
    
    if match_count == 0:
        return {}
    
    # Calcular promedios
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
    
    # Redondear valores
    for key, value in averages.items():
        if isinstance(value, float):
            averages[key] = round(value, 2)
    
    return averages


def get_cibao_average_metrics_filtered(all_matches: List[Dict], filter_type: str = "all", opponent_name: str = None) -> Dict[str, float]:
    """Calcula promedios de métricas clave para Cibao, opcionalmente filtrados por tipo de partido."""
    cibao_matches = []
    
    for match_data in all_matches:
        match_info = extract_match_info(match_data)
        if not match_info:
            continue
        
        home = match_info.get("home_team", "")
        away = match_info.get("away_team", "")
        
        # Verificar si Cibao juega en este partido
        if CIBAO_TEAM_NAME.lower() in home.lower() or CIBAO_TEAM_NAME.lower() in away.lower():
            cibao_stats = extract_team_stats_from_match(match_data, CIBAO_TEAM_NAME)
            if cibao_stats:
                match_info["cibao_stats"] = cibao_stats
                cibao_matches.append(match_info)
    
    # Aplicar filtro si es necesario
    if filter_type != "all":
        if filter_type == "vs_cibao" and opponent_name:
            # Para "vs_cibao", filtrar partidos donde Cibao jugó contra el oponente seleccionado
            filtered_cibao_matches = []
            cibao_name_lower = CIBAO_TEAM_NAME.lower().strip()
            opponent_name_lower = opponent_name.lower().strip() if opponent_name else ""
            opponent_base = opponent_name_lower.replace(' fc', '').strip()
            cibao_base = cibao_name_lower.replace(' fc', '').strip()
            
            for match in cibao_matches:
                home = match.get("home_team", "")
                away = match.get("away_team", "")
                home_str = str(home).lower().strip() if home else ""
                away_str = str(away).lower().strip() if away else ""
                
                home_match_cibao = (cibao_name_lower in home_str or home_str in cibao_name_lower or
                                   cibao_base in home_str.replace(' fc', '').strip() or
                                   home_str.replace(' fc', '').strip() in cibao_base)
                away_match_cibao = (cibao_name_lower in away_str or away_str in cibao_name_lower or
                                   cibao_base in away_str.replace(' fc', '').strip() or
                                   away_str.replace(' fc', '').strip() in cibao_base)
                home_match_opponent = (opponent_name_lower in home_str or home_str in opponent_name_lower or
                                      opponent_base in home_str.replace(' fc', '').strip() or
                                      home_str.replace(' fc', '').strip() in opponent_base)
                away_match_opponent = (opponent_name_lower in away_str or away_str in opponent_name_lower or
                                      opponent_base in away_str.replace(' fc', '').strip() or
                                      away_str.replace(' fc', '').strip() in opponent_base)
                
                if (home_match_cibao or away_match_cibao) and (home_match_opponent or away_match_opponent):
                    filtered_cibao_matches.append(match)
            
            cibao_matches = filtered_cibao_matches
        else:
            # Para otros filtros (home, away), usar la función estándar
            cibao_matches = filter_matches_by_type(cibao_matches, CIBAO_TEAM_NAME, filter_type, all_matches)
    
    return calculate_average_metrics_from_matches(cibao_matches, "cibao_stats")


def calculate_average_metrics_from_matches(matches: List[Dict], stats_key: str) -> Dict[str, float]:
    """Calcula promedios de métricas clave desde una lista de partidos."""
    if not matches:
        return {}
    
    # Métricas a calcular
    metrics_to_sum = {
        "goals": 0,
        "goalsConceded": 0,
        "totalScoringAtt": 0,  # Disparos totales
        "ontargetScoringAtt": 0,  # Disparos al arco
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
    }
    
    match_count = 0
    
    for match in matches:
        stats = match.get(stats_key, {})
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
    
    # Calcular promedios
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
    
    # Redondear valores
    for key, value in averages.items():
        if isinstance(value, float):
            averages[key] = round(value, 2)
    
    return averages


def display_metric_card(label: str, value: str, icon: str = "", delta: str = "", color: str = "normal", 
                       competition_avg: str = None, cibao_avg: str = None, higher_is_better: bool = True):
    """Muestra una tarjeta de métrica con estilo mejorado, incluyendo indicadores visuales de comparación."""
    color_map = {
        "normal": "#1E293B",
        "good": "#10B981",
        "bad": "#EF4444",
        "warning": "#F59E0B"
    }
    bg_color = color_map.get(color, color_map["normal"])
    
    # Solo mostrar icono si no está vacío
    if icon:
        icon_html = f'<div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>'
    else:
        icon_html = ''
    
    # Construir el HTML evitando conflictos de comillas
    delta_html = f'<div style="color: #94A3B8; font-size: 1.0rem; margin-top: 0.5rem;">{delta}</div>' if delta else ''
    
    # Calcular diferencias y crear indicadores visuales
    comparison_html = ""
    if competition_avg is not None or cibao_avg is not None:
        comparison_parts = []
        
        # Comparar con competencia
        if competition_avg is not None:
            try:
                value_num = float(value.replace('%', '').replace('A', '').replace('R', '').strip())
                comp_num = float(str(competition_avg).replace('%', '').replace('A', '').replace('R', '').strip())
                diff = value_num - comp_num
                
                # Determinar si es mejor o peor
                if higher_is_better:
                    is_better = diff > 0
                else:
                    is_better = diff < 0
                
                # Crear indicador visual
                if abs(diff) > 0.01:  # Solo mostrar si hay diferencia significativa
                    arrow = "↑" if is_better else "↓"
                    arrow_color = "#10B981" if is_better else "#EF4444"
                    diff_str = f"{diff:+.2f}".replace('+', '+').replace('-', '-')
                    if '%' in value:
                        diff_str += '%'
                    indicator = f'<span style="color: {arrow_color}; font-weight: bold; margin-left: 0.3rem;">{arrow} {diff_str}</span>'
                else:
                    indicator = '<span style="color: #94A3B8; margin-left: 0.3rem;">≈</span>'
                
                comparison_parts.append(
                    f'<div style="color: #64748B; font-size: 0.85rem; margin-top: 0.5rem; display: flex; align-items: center; justify-content: center;">'
                    f'<span>Comp: {competition_avg}</span>{indicator}'
                    f'</div>'
                )
            except (ValueError, AttributeError):
                # Si no se puede calcular, mostrar sin indicador
                comparison_parts.append(f'<div style="color: #64748B; font-size: 0.85rem; margin-top: 0.5rem;">Comp: {competition_avg}</div>')
        
        # Comparar con Cibao
        if cibao_avg is not None:
            try:
                value_num = float(value.replace('%', '').replace('A', '').replace('R', '').strip())
                cibao_num = float(str(cibao_avg).replace('%', '').replace('A', '').replace('R', '').strip())
                diff = value_num - cibao_num
                
                # Determinar si es mejor o peor
                if higher_is_better:
                    is_better = diff > 0
                else:
                    is_better = diff < 0
                
                # Crear indicador visual
                if abs(diff) > 0.01:  # Solo mostrar si hay diferencia significativa
                    arrow = "↑" if is_better else "↓"
                    arrow_color = "#10B981" if is_better else "#EF4444"
                    diff_str = f"{diff:+.2f}".replace('+', '+').replace('-', '-')
                    if '%' in value:
                        diff_str += '%'
                    indicator = f'<span style="color: {arrow_color}; font-weight: bold; margin-left: 0.3rem;">{arrow} {diff_str}</span>'
                else:
                    indicator = '<span style="color: #94A3B8; margin-left: 0.3rem;">≈</span>'
                
                comparison_parts.append(
                    f'<div style="color: #FF9900; font-size: 0.85rem; margin-top: 0.25rem; display: flex; align-items: center; justify-content: center;">'
                    f'<span>Cibao: {cibao_avg}</span>{indicator}'
                    f'</div>'
                )
            except (ValueError, AttributeError):
                # Si no se puede calcular, mostrar sin indicador
                comparison_parts.append(f'<div style="color: #FF9900; font-size: 0.85rem; margin-top: 0.25rem;">Cibao: {cibao_avg}</div>')
        
        comparison_html = ''.join(comparison_parts)
    
    # Construir HTML de forma más segura
    html_parts = [
        f'<div style="background: linear-gradient(135deg, {bg_color} 0%, rgba(30, 41, 59, 0.8) 100%); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); transition: transform 0.2s;">',
        icon_html,
        f'<div style="color: #94A3B8; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 500;">{label}</div>',
        f'<div style="color: #FFFFFF; font-size: 2rem; font-weight: bold;">{value}</div>',
        delta_html,
        comparison_html,
        '</div>'
    ]
    
    html_content = ''.join(html_parts)
    st.markdown(html_content, unsafe_allow_html=True)


def extract_match_result(match_data: Dict, team_name: str) -> Optional[Dict]:
    """Extrae el resultado de un partido para un equipo específico."""
    try:
        live_data = match_data.get("liveData", {})
        match_details = live_data.get("matchDetails", {})
        match_info = match_data.get("matchInfo", {})
        
        # Obtener equipos
        contestants = match_info.get("contestant", [])
        home_team = None
        away_team = None
        team_is_home = None
        
        for contestant in contestants:
            position = contestant.get("position", "").lower()
            name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
            if position == "home":
                home_team = name
            elif position == "away":
                away_team = name
        
        # Si no hay posición, usar orden
        if not home_team and contestants:
            home_team = contestants[0].get("name") or contestants[0].get("shortName", "")
        if not away_team and len(contestants) > 1:
            away_team = contestants[1].get("name") or contestants[1].get("shortName", "")
        
        # Determinar si el equipo es local o visitante
        if team_name.lower() in (home_team or "").lower():
            team_is_home = True
            opponent_name = away_team
        elif team_name.lower() in (away_team or "").lower():
            team_is_home = False
            opponent_name = home_team
        else:
            return None
        
        # Obtener marcador
        scores = match_details.get("scores", {})
        total_scores = scores.get("total", {})
        home_goals = total_scores.get("home", 0)
        away_goals = total_scores.get("away", 0)
        
        # Determinar goles del equipo y del oponente
        if team_is_home:
            team_goals = home_goals
            opponent_goals = away_goals
        else:
            team_goals = away_goals
            opponent_goals = home_goals
        
        # Determinar resultado (W/D/L)
        if team_goals > opponent_goals:
            result = "W"  # Win / Victoria
            result_emoji = "✅"
        elif team_goals < opponent_goals:
            result = "L"  # Loss / Derrota
            result_emoji = "❌"
        else:
            result = "D"  # Draw / Empate
            result_emoji = "➖"
        
        # Obtener fecha
        match_date_str = match_info.get("localDate", "")
        
        return {
            "date": match_date_str,
            "opponent": opponent_name,
            "team_goals": team_goals,
            "opponent_goals": opponent_goals,
            "result": result,
            "result_emoji": result_emoji,
            "is_home": team_is_home,
            "score": f"{team_goals}-{opponent_goals}"
        }
    except Exception as e:
        return None


def get_recent_form(matches: List[Dict], team_name: str, num_matches: Optional[int] = 5) -> List[Dict]:
    """Obtiene los últimos N partidos con sus resultados. Si num_matches es None, devuelve todos."""
    recent_matches = []
    seen_match_ids = set()  # Para evitar duplicados
    
    # Ordenar partidos por fecha (más recientes primero)
    sorted_matches = sorted(matches, key=lambda x: x.get("date") or datetime.min, reverse=True)
    
    # Obtener solo partidos jugados
    played_matches = [m for m in sorted_matches if m.get("status", "").lower() in ["played", "finished", "ft", "jugado", "finalizado"]]
    
    # Tomar los últimos N, evitando duplicados
    for match in played_matches:
        match_id = match.get("match_id", "")
        
        # Evitar duplicados
        if match_id in seen_match_ids:
            continue
        seen_match_ids.add(match_id)
        
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        result = extract_match_result(match_data, team_name)
        if result:
            # Incluir match_data para poder acceder a las estadísticas detalladas
            result["match_data"] = match_data
            result["match_id"] = match_id
            recent_matches.append(result)
            
            # Detener cuando tengamos suficientes partidos únicos (solo si num_matches no es None)
            if num_matches is not None and len(recent_matches) >= num_matches:
                break
    
    return recent_matches


def display_recent_form(recent_matches: List[Dict], team_name: str):
    """Muestra el formulario reciente en un formato visual."""
    if not recent_matches:
        st.info("No hay suficientes partidos jugados para mostrar el formulario reciente.")
        return
    
    # Calcular estadísticas de forma
    wins = sum(1 for m in recent_matches if m["result"] == "W")
    draws = sum(1 for m in recent_matches if m["result"] == "D")
    losses = sum(1 for m in recent_matches if m["result"] == "L")
    
    # Mostrar resumen de forma
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Últimos Partidos", len(recent_matches))
    
    with col2:
        st.metric("Victorias", wins, delta=f"{wins}/{len(recent_matches)}")
    
    with col3:
        st.metric("Empates", draws, delta=f"{draws}/{len(recent_matches)}")
    
    with col4:
        st.metric("Derrotas", losses, delta=f"{losses}/{len(recent_matches)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mostrar cadena de resultados (W/D/L)
    form_string = "".join([m["result_emoji"] for m in recent_matches])
    st.markdown(f"""
    <div style='
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    '>
        <div style='color: #94A3B8; font-size: 0.9rem; margin-bottom: 0.5rem;'>Forma Reciente</div>
        <div style='display: flex; align-items: center; justify-content: center; gap: 1rem; color: #FFFFFF; font-size: 2.5rem; font-weight: bold; letter-spacing: 0.5rem;'>
            <span style='color: #94A3B8; font-size: 0.8rem; font-weight: normal; letter-spacing: normal;'>Más reciente</span>
            <span>{form_string}</span>
            <span style='color: #94A3B8; font-size: 0.8rem; font-weight: normal; letter-spacing: normal;'>Más antiguo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar tabla de partidos recientes
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Detalle de Partidos Recientes</h3>
    """, unsafe_allow_html=True)
    
    # Removed matches_data list as we're using custom HTML table now
    # This was only used for display, but we're rendering directly with columns
    
    # Initialize session state for selected match and timeline
    if "selected_match_index" not in st.session_state:
        st.session_state.selected_match_index = None
    if "selected_timeline_index" not in st.session_state:
        st.session_state.selected_timeline_index = None
    
    # Create a clickable table using Streamlit components
    # Header row - updated column widths for new headers
    header_cols = st.columns([0.5, 1.5, 2, 1, 1, 1, 1.5, 1.5])
    headers = ["#", "Fecha", "Oponente", "Resultado", "Marcador", "Lugar", "Disparos/Precisión", "Disparos Recibidos/Precisión"]
    for i, header in enumerate(headers):
        with header_cols[i]:
            st.markdown(f"""
            <div style='color:#FF9900; font-weight:600; padding:0.5rem 0; border-bottom:2px solid #FF9900;'>
                {header}
            </div>
            """, unsafe_allow_html=True)
    
    # Data rows - each row is clickable via a button
    for idx, match in enumerate(recent_matches, 1):
        venue = "Casa" if match["is_home"] else "Fuera"
        
        # Extract shots statistics from match data
        match_data = match.get("match_data")
        team_shots = 0
        team_shots_on_target = 0
        team_shots_pct = 0.0
        opp_shots = 0
        opp_shots_on_target = 0
        opp_shots_pct = 0.0
        
        if match_data:
            team_stats = extract_team_stats_from_match(match_data, team_name)
            opponent_name = match.get("opponent", "")
            opponent_stats = extract_team_stats_from_match(match_data, opponent_name) if opponent_name else None
            
            if team_stats:
                team_shots = int(team_stats.get("totalScoringAtt", 0))
                team_shots_on_target = int(team_stats.get("ontargetScoringAtt", 0))
                if team_shots > 0:
                    team_shots_pct = (team_shots_on_target / team_shots) * 100
            
            if opponent_stats:
                opp_shots = int(opponent_stats.get("totalScoringAtt", 0))
                opp_shots_on_target = int(opponent_stats.get("ontargetScoringAtt", 0))
                if opp_shots > 0:
                    opp_shots_pct = (opp_shots_on_target / opp_shots) * 100
        
        # Create columns for this row - updated widths
        row_cols = st.columns([0.5, 1.5, 2, 1, 1, 1, 1.5, 1.5])
        
        with row_cols[0]:
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{idx}</div>", unsafe_allow_html=True)
        with row_cols[1]:
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{match['date']}</div>", unsafe_allow_html=True)
        with row_cols[2]:
            # Make the opponent name clickable
            if st.button(f"📊 {match['opponent']}", key=f"row_btn_{idx-1}", use_container_width=True):
                st.session_state.selected_match_index = idx - 1
                st.rerun()
        with row_cols[3]:
            # Make the result emoji clickable for timeline
            if st.button(f"{match['result_emoji']}", key=f"timeline_btn_{idx-1}", use_container_width=True, help="Ver línea de tiempo"):
                # Toggle timeline - if already selected, close it; otherwise open it
                if st.session_state.selected_timeline_index == idx - 1:
                    st.session_state.selected_timeline_index = None
                else:
                    st.session_state.selected_timeline_index = idx - 1
                st.rerun()
        with row_cols[4]:
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{match['score']}</div>", unsafe_allow_html=True)
        with row_cols[5]:
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{venue}</div>", unsafe_allow_html=True)
        with row_cols[6]:
            # Team shots / shots on target %
            shots_display = f"{team_shots}/{team_shots_on_target} ({team_shots_pct:.0f}%)"
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{shots_display}</div>", unsafe_allow_html=True)
        with row_cols[7]:
            # Opponent shots / shots on target %
            opp_shots_display = f"{opp_shots}/{opp_shots_on_target} ({opp_shots_pct:.0f}%)"
            st.markdown(f"<div style='padding:0.5rem 0; color:#D1D5DB;'>{opp_shots_display}</div>", unsafe_allow_html=True)
        
        # Display timeline popout if this row is selected
        if st.session_state.selected_timeline_index == idx - 1:
            display_match_timeline(match, team_name, match.get("opponent", "Oponente"), idx - 1)
        
        # Add separator line
        st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.1); margin:0.25rem 0;'></div>", unsafe_allow_html=True)
    
    # Display modal popup if a match is selected
    if st.session_state.selected_match_index is not None:
        selected_match = recent_matches[st.session_state.selected_match_index]
        display_match_modal(selected_match, team_name)


def extract_match_events(match_data: Dict, team_name: str, opponent_name: str) -> List[Dict]:
    """Extrae todos los eventos del partido (goles, tarjetas, sustituciones, VAR) y los ordena cronológicamente."""
    if not match_data:
        return []
    
    live_data = match_data.get("liveData", {})
    if not live_data:
        return []
    
    events = []
    
    # Get team IDs from matchInfo
    match_info_data = match_data.get("matchInfo", {})
    contestants = match_info_data.get("contestant", [])
    
    # Map contestant IDs to team names
    contestant_to_team = {}
    for contestant in contestants:
        contestant_id = contestant.get("id", "")
        team_name_from_contestant = contestant.get("name") or contestant.get("shortName", "")
        contestant_to_team[contestant_id] = team_name_from_contestant
    
    # Extract goals
    goals = live_data.get("goal", [])
    for goal in goals:
        contestant_id = goal.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        goal_type = goal.get("type", "G")
        goal_type_text = {
            "G": "Gol",
            "PG": "Gol de Penalti",
            "OG": "Gol en Contra",
            "FG": "Gol de Falta"
        }.get(goal_type, "Gol")
        
        scorer_name = goal.get("scorerName", "Desconocido")
        assist_name = goal.get("assistPlayerName", "")
        
        home_score = goal.get("homeScore", 0)
        away_score = goal.get("awayScore", 0)
        
        # Build goal description with assist if available
        if assist_name:
            goal_details = f"{goal_type_text} - {scorer_name} (Asistencia: {assist_name})"
        else:
            goal_details = f"{goal_type_text} - {scorer_name}"
        
        events.append({
            "type": "goal",
            "time": goal.get("timeMin", 0),
            "time_display": goal.get("timeMinSec", f"{goal.get('timeMin', 0)}'"),
            "period": goal.get("periodId", 1),
            "player": scorer_name,
            "assist": assist_name,
            "team": team_name if is_team_event else opponent_name,
            "details": goal_details,
            "score": f"{home_score}-{away_score}",
            "icon": "⚽",
            "color": "#10B981" if is_team_event else "#EF4444"
        })
    
    # Extract cards
    cards = live_data.get("card", [])
    for card in cards:
        contestant_id = card.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        card_type = card.get("type", "")
        card_type_text = {
            "YC": "Tarjeta Amarilla",
            "RC": "Tarjeta Roja",
            "Y2C": "Segunda Amarilla"
        }.get(card_type, "Tarjeta")
        
        card_reason = card.get("cardReason", "")
        reason_text = f" - {card_reason}" if card_reason else ""
        
        events.append({
            "type": "card",
            "time": card.get("timeMin", 0),
            "time_display": card.get("timeMinSec", f"{card.get('timeMin', 0)}'"),
            "period": card.get("periodId", 1),
            "player": card.get("playerName", "Desconocido"),
            "team": team_name if is_team_event else opponent_name,
            "details": f"{card_type_text}{reason_text} - {card.get('playerName', 'Desconocido')}",
            "icon": "🟨" if card_type == "YC" else "🟥",
            "color": "#F59E0B" if card_type == "YC" else "#EF4444"
        })
    
    # Extract substitutions
    substitutions = live_data.get("substitute", [])
    for sub in substitutions:
        contestant_id = sub.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        player_on = sub.get("playerOnName", "Desconocido")
        player_off = sub.get("playerOffName", "Desconocido")
        sub_reason = sub.get("subReason", "Táctica")
        
        events.append({
            "type": "substitution",
            "time": sub.get("timeMin", 0),
            "time_display": sub.get("timeMinSec", f"{sub.get('timeMin', 0)}'"),
            "period": sub.get("periodId", 1),
            "player": f"{player_off} → {player_on}",
            "team": team_name if is_team_event else opponent_name,
            "details": f"Sustitución: {player_off} sale, {player_on} entra ({sub_reason})",
            "icon": "🔄",
            "color": "#3B82F6"
        })
    
    # Extract VAR decisions
    var_decisions = live_data.get("VAR", [])
    for var in var_decisions:
        contestant_id = var.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        var_type = var.get("type", "VAR")
        decision = var.get("decision", "")
        outcome = var.get("outcome", "")
        
        events.append({
            "type": "var",
            "time": var.get("timeMin", 0),
            "time_display": var.get("timeMinSec", f"{var.get('timeMin', 0)}'"),
            "period": var.get("periodId", 1),
            "player": var.get("playerName", ""),
            "team": team_name if is_team_event else opponent_name,
            "details": f"VAR: {var_type} - {decision} ({outcome})",
            "icon": "📺",
            "color": "#8B5CF6"
        })
    
    # Sort events by period and time
    events.sort(key=lambda x: (x["period"], x["time"]))
    
    return events


def display_match_timeline(match: Dict, team_name: str, opponent_name: str, match_index: int):
    """Muestra la línea de tiempo de eventos del partido en un popout."""
    match_data = match.get("match_data")
    if not match_data:
        return
    
    events = extract_match_events(match_data, team_name, opponent_name)
    
    # Get match summary info
    live_data = match_data.get("liveData", {})
    match_details = live_data.get("matchDetails", {})
    match_info_data = match_data.get("matchInfo", {})
    match_details_extra = live_data.get("matchDetailsExtra", {})
    
    # Extract final score
    scores = match_details.get("scores", {})
    ft_score = scores.get("ft", {})
    home_score = ft_score.get("home", 0) if ft_score else 0
    away_score = ft_score.get("away", 0) if ft_score else 0
    
    # Get team names
    contestants = match_info_data.get("contestant", [])
    home_team_name = ""
    away_team_name = ""
    for contestant in contestants:
        position = contestant.get("position", "").lower()
        name = contestant.get("name") or contestant.get("shortName", "")
        if position == "home":
            home_team_name = name
        elif position == "away":
            away_team_name = name
    
    # Get attendance and referee
    attendance = match_details_extra.get("attendance", "")
    match_official = match_details_extra.get("matchOfficial", [])
    referee_name = ""
    if match_official:
        for official in match_official:
            if official.get("type") == "Referee":
                referee_name = official.get("name", "")
                break
    
    # Get injury time info (convert from seconds to minutes)
    periods = match_details.get("period", [])
    injury_time_info = []
    for period in periods:
        period_id = period.get("id", 0)
        injury_time_seconds = period.get("announcedInjuryTime", 0)
        if injury_time_seconds > 0:
            injury_time_minutes = injury_time_seconds // 60  # Convert seconds to minutes
            period_name = "1er Tiempo" if period_id == 1 else "2do Tiempo"
            injury_time_info.append(f"{period_name}: +{injury_time_minutes}'")
    
    if not events:
        st.info("No hay eventos disponibles para este partido.")
        return
    
    # Display timeline
    st.markdown("""
    <style>
    .timeline-container {
        background: rgba(30, 41, 59, 0.8);
        border: 2px solid #FF9900;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .timeline-summary {
        background: rgba(255, 153, 0, 0.1);
        border: 1px solid rgba(255, 153, 0, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .timeline-summary-row {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
        color: #D1D5DB;
    }
    .timeline-summary-label {
        color: #94A3B8;
        font-weight: 500;
    }
    .timeline-event {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 3px solid;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.05);
    }
    .timeline-time {
        font-weight: bold;
        min-width: 60px;
        color: #FF9900;
    }
    .timeline-icon {
        font-size: 1.5rem;
        margin: 0 1rem;
    }
    .timeline-details {
        flex: 1;
        color: #D1D5DB;
    }
    .timeline-team {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-top: 0.25rem;
    }
    </style>
    <div class="timeline-container">
        <h4 style='color:#FF9900; margin-top:0; margin-bottom:1rem;'>Línea de Tiempo del Partido</h4>
    """, unsafe_allow_html=True)
    
    # Display match summary
    st.markdown("""
    <div class="timeline-summary">
    """, unsafe_allow_html=True)
    
    # Result row
    st.markdown(f"""
    <div class="timeline-summary-row">
        <span class="timeline-summary-label">Resultado Final:</span>
        <span style="font-weight: bold; color: #FF9900;">{home_team_name} {home_score} - {away_score} {away_team_name}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if referee_name:
        st.markdown(f"""
        <div class="timeline-summary-row">
            <span class="timeline-summary-label">Árbitro:</span>
            <span>{referee_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if attendance:
        st.markdown(f"""
        <div class="timeline-summary-row">
            <span class="timeline-summary-label">Asistencia:</span>
            <span>{attendance}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if injury_time_info:
        st.markdown(f"""
        <div class="timeline-summary-row">
            <span class="timeline-summary-label">Tiempo Adicional:</span>
            <span>{', '.join(injury_time_info)}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Group events by period
    first_half = [e for e in events if e["period"] == 1]
    second_half = [e for e in events if e["period"] == 2]
    
    if first_half:
        st.markdown("<h5 style='color:#94A3B8; margin-top:1rem;'>Primer Tiempo</h5>", unsafe_allow_html=True)
        for event in first_half:
            # Build event HTML properly
            if event['type'] == 'goal':
                # Goals always show score
                event_html = f"""
                <div class="timeline-event" style="border-left-color: {event['color']};">
                    <div class="timeline-time">{event['time_display']}</div>
                    <div class="timeline-icon">{event['icon']}</div>
                    <div class="timeline-details">
                        <div style="font-weight: 600;">{event['details']}</div>
                        <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.25rem;">Marcador: {event['score']}</div>
                        <div class="timeline-team">{event['team']}</div>
                    </div>
                </div>
                """
            else:
                # Other events (cards, subs, VAR)
                event_html = f"""
                <div class="timeline-event" style="border-left-color: {event['color']};">
                    <div class="timeline-time">{event['time_display']}</div>
                    <div class="timeline-icon">{event['icon']}</div>
                    <div class="timeline-details">
                        <div>{event['details']}</div>
                        <div class="timeline-team">{event['team']}</div>
                    </div>
                </div>
                """
            
            st.markdown(event_html, unsafe_allow_html=True)
    
    if second_half:
        st.markdown("<h5 style='color:#94A3B8; margin-top:1rem;'>Segundo Tiempo</h5>", unsafe_allow_html=True)
        for event in second_half:
            # Build event HTML properly
            if event['type'] == 'goal':
                # Goals always show score
                event_html = f"""
                <div class="timeline-event" style="border-left-color: {event['color']};">
                    <div class="timeline-time">{event['time_display']}</div>
                    <div class="timeline-icon">{event['icon']}</div>
                    <div class="timeline-details">
                        <div style="font-weight: 600;">{event['details']}</div>
                        <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.25rem;">Marcador: {event['score']}</div>
                        <div class="timeline-team">{event['team']}</div>
                    </div>
                </div>
                """
            else:
                # Other events (cards, subs, VAR)
                event_html = f"""
                <div class="timeline-event" style="border-left-color: {event['color']};">
                    <div class="timeline-time">{event['time_display']}</div>
                    <div class="timeline-icon">{event['icon']}</div>
                    <div class="timeline-details">
                        <div>{event['details']}</div>
                        <div class="timeline-team">{event['team']}</div>
                    </div>
                </div>
                """
            
            st.markdown(event_html, unsafe_allow_html=True)
    
    # Close timeline container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add a close button
    if st.button("✕ Cerrar Línea de Tiempo", key=f"close_timeline_{match_index}", use_container_width=True):
        st.session_state.selected_timeline_index = None
        st.rerun()


def display_match_modal(match: Dict, team_name: str):
    """Muestra métricas detalladas de un partido específico en formato KPI tiles en un modal popup."""
    match_data = match.get("match_data")
    if not match_data:
        st.warning("No se encontraron datos detallados para este partido.")
        return
    
    # Extraer estadísticas del equipo y del oponente
    team_stats = extract_team_stats_from_match(match_data, team_name)
    opponent_name = match.get("opponent", "Oponente")
    opponent_stats = extract_team_stats_from_match(match_data, opponent_name)
    
    if not team_stats:
        st.warning("No se pudieron extraer las estadísticas del equipo para este partido.")
        return
    
    venue = "Casa" if match.get("is_home") else "Fuera"
    
    # Create modal popup window with prominent styling
    st.markdown("""
    <style>
    .match-modal-container {
        background: linear-gradient(135deg, #1E293B 0%, rgba(30, 41, 59, 0.98) 100%);
        border: 4px solid #FF9900;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.9);
        position: relative;
    }
    </style>
    <div class="match-modal-container">
    """, unsafe_allow_html=True)
    
    # Header with close button
    col_close, col_title, _ = st.columns([1, 9, 1])
    with col_close:
        if st.button("✕", key="close_modal_top", help="Cerrar ventana", use_container_width=True):
            st.session_state.selected_match_index = None
            st.rerun()
    
    with col_title:
        st.markdown(f"""
        <h2 style='color:#FF9900; text-align:center; margin-top:0; margin-bottom:0.5rem;'>
            {team_name} vs {opponent_name}
        </h2>
        <p style='text-align:center; color:#94A3B8; font-size:1rem; margin-bottom:1.5rem;'>
            {match.get('date', 'N/A')} | {venue} | Resultado: {match.get('score', 'N/A')} {match.get('result_emoji', '')}
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Métricas del equipo seleccionado
    st.markdown(f"""
    <h3 style='color:#FF9900; text-align:center; margin-top:20px;'>Métricas Clave - {team_name}</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fila 1: Ofensivas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        goals = team_stats.get("goals", 0)
        opp_goals = opponent_stats.get("goals", 0) if opponent_stats else 0
        display_metric_card(
            "Goles",
            f"{goals:.0f}",
            "",
            f"vs {opp_goals:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col2:
        shots = team_stats.get("totalScoringAtt", 0)
        shots_on_target = team_stats.get("ontargetScoringAtt", 0)
        shot_accuracy = (shots_on_target / shots * 100) if shots > 0 else 0
        opp_shots = opponent_stats.get("totalScoringAtt", 0) if opponent_stats else 0
        display_metric_card(
            "Disparos",
            f"{shots:.0f}",
            "",
            f"{shot_accuracy:.1f}% precisión | vs {opp_shots:.0f}",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col3:
        shots_on_target = team_stats.get("ontargetScoringAtt", 0)
        opp_sot = opponent_stats.get("ontargetScoringAtt", 0) if opponent_stats else 0
        display_metric_card(
            "Disparos al Arco",
            f"{shots_on_target:.0f}",
            "",
            f"vs {opp_sot:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col4:
        possession = team_stats.get("possessionPercentage", 0)
        opp_poss = opponent_stats.get("possessionPercentage", 0) if opponent_stats else 0
        display_metric_card(
            "Posesión %",
            f"{possession:.1f}%",
            "",
            f"vs {opp_poss:.1f}% del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fila 2: Defensivas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        goals_conceded = team_stats.get("goalsConceded", 0)
        display_metric_card(
            "Goles Recibidos",
            f"{goals_conceded:.0f}",
            "",
            "",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col2:
        saves = team_stats.get("saves", 0)
        opp_saves = opponent_stats.get("saves", 0) if opponent_stats else 0
        display_metric_card(
            "Atajadas",
            f"{saves:.0f}",
            "",
            f"vs {opp_saves:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col3:
        clearances = team_stats.get("totalClearance", 0)
        opp_clear = opponent_stats.get("totalClearance", 0) if opponent_stats else 0
        display_metric_card(
            "Despejes",
            f"{clearances:.0f}",
            "",
            f"vs {opp_clear:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col4:
        tackles_won = team_stats.get("wonTackle", 0)
        total_tackles = team_stats.get("totalTackle", 0)
        tackle_success = (tackles_won / total_tackles * 100) if total_tackles > 0 else 0
        opp_tackles = opponent_stats.get("wonTackle", 0) if opponent_stats else 0
        display_metric_card(
            "Tackles Exitosos",
            f"{tackles_won:.0f}",
            "",
            f"{tackle_success:.1f}% efectividad | vs {opp_tackles:.0f}",
            competition_avg=None,
            cibao_avg=None
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fila 3: Set Pieces y Disciplina
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        corners_won = team_stats.get("wonCorners", 0)
        opp_corners = opponent_stats.get("wonCorners", 0) if opponent_stats else 0
        display_metric_card(
            "Corners Ganados",
            f"{corners_won:.0f}",
            "",
            f"vs {opp_corners:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col2:
        total_pass = team_stats.get("totalPass", 0)
        accurate_pass = team_stats.get("accuratePass", 0)
        pass_accuracy = (accurate_pass / total_pass * 100) if total_pass > 0 else 0
        opp_pass_acc = 0
        if opponent_stats:
            opp_total = opponent_stats.get("totalPass", 0)
            opp_accurate = opponent_stats.get("accuratePass", 0)
            opp_pass_acc = (opp_accurate / opp_total * 100) if opp_total > 0 else 0
        display_metric_card(
            "Precisión de Pases",
            f"{pass_accuracy:.1f}%",
            "",
            f"vs {opp_pass_acc:.1f}% del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col3:
        fouls = team_stats.get("fkFoulLost", 0)
        opp_fouls = opponent_stats.get("fkFoulLost", 0) if opponent_stats else 0
        display_metric_card(
            "Faltas Cometidas",
            f"{fouls:.0f}",
            "",
            f"vs {opp_fouls:.0f} del oponente",
            competition_avg=None,
            cibao_avg=None
        )
    
    with col4:
        yellow_cards = team_stats.get("totalYellowCard", 0)
        red_cards = team_stats.get("totalRedCard", 0)
        total_cards = yellow_cards + red_cards
        opp_yellow = opponent_stats.get("totalYellowCard", 0) if opponent_stats else 0
        opp_red = opponent_stats.get("totalRedCard", 0) if opponent_stats else 0
        opp_total = opp_yellow + opp_red
        display_metric_card(
            "Tarjetas",
            f"{total_cards:.0f}",
            "",
            f"{yellow_cards:.0f}A, {red_cards:.0f}R | vs {opp_total:.0f}",
            competition_avg=None,
            cibao_avg=None
        )
    
    # Close button at bottom (prominent)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✕ Cerrar Ventana", key="close_modal_bottom", use_container_width=True, type="primary"):
            st.session_state.selected_match_index = None
            st.rerun()
    
    # Close modal HTML
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)


def calculate_single_match_metrics(stats: Dict, opponent_stats: Dict = None) -> Dict[str, float]:
    """Calcula métricas derivadas para un partido individual."""
    metrics = {}
    
    # Precisión de pases
    total_pass = stats.get("totalPass", 0)
    accurate_pass = stats.get("accuratePass", 0)
    if total_pass > 0:
        metrics["passAccuracy"] = (accurate_pass / total_pass) * 100
    else:
        metrics["passAccuracy"] = 0
    
    # Efectividad de tackles
    total_tackle = stats.get("totalTackle", 0)
    won_tackle = stats.get("wonTackle", 0)
    if total_tackle > 0:
        metrics["tackleSuccess"] = (won_tackle / total_tackle) * 100
    else:
        metrics["tackleSuccess"] = 0
    
    # Precisión de disparos
    total_shots = stats.get("totalScoringAtt", 0)
    shots_on_target = stats.get("ontargetScoringAtt", 0)
    if total_shots > 0:
        metrics["shotAccuracy"] = (shots_on_target / total_shots) * 100
    else:
        metrics["shotAccuracy"] = 0
    
    return metrics


def create_radar_chart(opponent_metrics: Dict[str, float], cibao_metrics: Dict[str, float], opponent_name: str, selected_metrics: List[str] = None) -> go.Figure:
    """Crea un gráfico de radar comparando oponente vs Cibao."""
    
    # Todas las métricas disponibles con sus configuraciones
    all_radar_metrics = {
        "Goles": ("goals", 5.0),
        "Goles Recibidos": ("goalsConceded", 3.0, True),  # Invertir (menos es mejor)
        "Disparos": ("totalScoringAtt", 20.0),
        "Disparos al Arco": ("ontargetScoringAtt", 10.0),
        "Posesión": ("possessionPercentage", 100.0),
        "Precisión Pases": ("passAccuracy", 100.0),
        "Pases Totales": ("totalPass", 500.0),
        "Pases Precisos": ("accuratePass", 400.0),
        "Corners": ("wonCorners", 10.0),
        "Tackles Exitosos": ("wonTackle", 15.0),
        "Tackles Totales": ("totalTackle", 20.0),
        "Despejes": ("totalClearance", 20.0),
        "Intercepciones": ("interception", 15.0),
        "Atajadas": ("saves", 8.0),
        "Faltas": ("fkFoulLost", 15.0),
        "Tarjetas Amarillas": ("totalYellowCard", 5.0),
    }
    
    # Si no se especifican métricas, usar las predeterminadas
    if selected_metrics is None:
        selected_metrics = [
            "Goles", "Goles Recibidos", "Disparos", "Posesión",
            "Precisión Pases", "Corners", "Tackles Exitosos", "Despejes"
        ]
    
    # Filtrar métricas seleccionadas
    radar_metrics = {k: v for k, v in all_radar_metrics.items() if k in selected_metrics}
    
    categories = []
    opponent_values = []
    cibao_values = []
    
    for label, metric_info in radar_metrics.items():
        if isinstance(metric_info, tuple):
            if len(metric_info) == 3:
                metric_key, max_val, invert = metric_info
            else:
                metric_key, max_val = metric_info
                invert = False
        else:
            metric_key = metric_info
            max_val = 100.0
            invert = False
        
        categories.append(label)
        
        # Obtener valor del oponente
        opp_val = opponent_metrics.get(metric_key, 0)
        if invert:
            # Invertir: menos es mejor (goles recibidos)
            opp_val = max(0, max_val - opp_val)
        opp_normalized = min(100, (opp_val / max_val) * 100) if max_val > 0 else 0
        opponent_values.append(opp_normalized)
        
        # Obtener valor de Cibao
        cibao_val = cibao_metrics.get(metric_key, 0)
        if invert:
            cibao_val = max(0, max_val - cibao_val)
        cibao_normalized = min(100, (cibao_val / max_val) * 100) if max_val > 0 else 0
        cibao_values.append(cibao_normalized)
    
    # Crear gráfico de radar
    fig = go.Figure()
    
    # Oponente - obtener color del CSV
    opponent_color = TEAM_COLORS.get(opponent_name, '#EF4444')  # Rojo por defecto si no se encuentra
    opponent_rgb = tuple(int(opponent_color[i:i+2], 16) for i in (1, 3, 5))
    opponent_fillcolor = f'rgba({opponent_rgb[0]}, {opponent_rgb[1]}, {opponent_rgb[2]}, 0.2)'
    
    fig.add_trace(go.Scatterpolar(
        r=opponent_values + [opponent_values[0]],  # Cerrar el círculo
        theta=categories + [categories[0]],
        fill='toself',
        name=opponent_name,
        line=dict(color=opponent_color, width=3),
        fillcolor=opponent_fillcolor
    ))
    
    # Cibao - usar color oficial
    cibao_color = CIBAO_COLOR
    # Convertir hex a RGB para el fillcolor
    cibao_rgb = tuple(int(cibao_color[i:i+2], 16) for i in (1, 3, 5))
    cibao_fillcolor = f'rgba({cibao_rgb[0]}, {cibao_rgb[1]}, {cibao_rgb[2]}, 0.2)'
    
    fig.add_trace(go.Scatterpolar(
        r=cibao_values + [cibao_values[0]],  # Cerrar el círculo
        theta=categories + [categories[0]],
        fill='toself',
        name='Cibao',
        line=dict(color=cibao_color, width=3),
        fillcolor=cibao_fillcolor
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=16, color='#94A3B8'),
                gridcolor='rgba(148, 163, 184, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=17, color='#FFFFFF'),
                linecolor='rgba(148, 163, 184, 0.3)'
            )
        ),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=18, color='#FFFFFF')
        ),
        title=dict(
            text="Comparación de Fortalezas y Debilidades",
            font=dict(size=24, color='#FFFFFF'),
            x=0.5
        )
    )
    
    return fig


def extract_formation_from_match(match_data: Dict, team_name: str) -> Optional[str]:
    """Extrae la formación utilizada por un equipo en un partido."""
    try:
        live_data = match_data.get("liveData", {})
        lineups = live_data.get("lineUp", [])
        
        # Buscar el lineup del equipo
        team_lineup = None
        for lineup in lineups:
            contestant_id = lineup.get("contestantId", "")
            match_info = match_data.get("matchInfo", {})
            contestants = match_info.get("contestant", [])
            
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    if team_name.lower() in name.lower():
                        team_lineup = lineup
                        break
            
            if team_lineup:
                break
        
        if not team_lineup:
            return None
        
        # Buscar formationUsed en los stats
        stats_list = team_lineup.get("stat", [])
        for stat in stats_list:
            if stat.get("type") == "formationUsed":
                return stat.get("value", "")
        
        # Alternativa: buscar en formationUsed directamente en el lineup
        formation = team_lineup.get("formationUsed", "")
        if formation:
            return formation
        
        return None
    except Exception as e:
        return None


def analyze_formations(matches: List[Dict], team_name: str) -> Dict:
    """Analiza las formaciones utilizadas por un equipo."""
    formation_stats = {}
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        formation = extract_formation_from_match(match_data, team_name)
        if not formation:
            continue
        
        # Inicializar estadísticas de esta formación si no existe
        if formation not in formation_stats:
            formation_stats[formation] = {
                "count": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "matches": []
            }
        
        formation_stats[formation]["count"] += 1
        
        # Extraer resultado
        result = extract_match_result(match_data, team_name)
        if result:
            if result["result"] == "W":
                formation_stats[formation]["wins"] += 1
            elif result["result"] == "L":
                formation_stats[formation]["losses"] += 1
            else:
                formation_stats[formation]["draws"] += 1
            
            formation_stats[formation]["goals_for"] += result.get("team_goals", 0)
            formation_stats[formation]["goals_against"] += result.get("opponent_goals", 0)
            formation_stats[formation]["matches"].append({
                "date": match.get("date_str", "N/D"),
                "opponent": result.get("opponent", "N/D"),
                "score": result.get("score", "N/D"),
                "result": result["result"]
            })
    
    # Calcular porcentajes y promedios
    for formation, stats in formation_stats.items():
        total = stats["count"]
        if total > 0:
            stats["win_rate"] = (stats["wins"] / total) * 100
            stats["avg_goals_for"] = stats["goals_for"] / total
            stats["avg_goals_against"] = stats["goals_against"] / total
            stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]
            stats["avg_goal_difference"] = stats["goal_difference"] / total
    
    return formation_stats


def extract_player_stats_from_matches(matches: List[Dict], team_name: str) -> Dict:
    """Extrae estadísticas de jugadores de todos los partidos."""
    player_stats = {}
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        live_data = match_data.get("liveData", {})
        lineups = live_data.get("lineUp", [])
        
        # Buscar el lineup del equipo
        team_lineup = None
        for lineup in lineups:
            contestant_id = lineup.get("contestantId", "")
            match_info = match_data.get("matchInfo", {})
            contestants = match_info.get("contestant", [])
            
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    if team_name.lower() in name.lower():
                        team_lineup = lineup
                        break
            
            if team_lineup:
                break
        
        if not team_lineup:
            continue
        
        # Procesar jugadores del lineup
        players = team_lineup.get("player", [])
        for player in players:
            player_id = player.get("playerId", "")
            player_name = player.get("matchName") or f"{player.get('shortFirstName', '')} {player.get('shortLastName', '')}".strip()
            
            if not player_id or not player_name:
                continue
            
            if player_id not in player_stats:
                player_stats[player_id] = {
                    "name": player_name,
                    "position": player.get("position", "Unknown"),
                    "shirt_number": player.get("shirtNumber", 0),
                    "goals": 0,
                    "assists": 0,
                    "matches_played": 0,
                    "matches_started": 0,
                    "total_minutes": 0,
                    "matches": []
                }
            
            # Extraer stats del jugador
            stats_list = player.get("stat", [])
            for stat in stats_list:
                stat_type = stat.get("type", "")
                value = stat.get("value", "0")
                
                try:
                    if stat_type == "goals":
                        player_stats[player_id]["goals"] += int(value)
                    elif stat_type == "goalAssist":
                        player_stats[player_id]["assists"] += int(value)
                    elif stat_type == "minsPlayed":
                        player_stats[player_id]["total_minutes"] += int(value)
                    elif stat_type == "gameStarted":
                        if int(value) == 1:
                            player_stats[player_id]["matches_started"] += 1
                except:
                    pass
            
            player_stats[player_id]["matches_played"] += 1
            player_stats[player_id]["matches"].append({
                "date": match.get("date_str", "N/D"),
                "opponent": match.get("away_team") if match.get("home_team") == team_name else match.get("home_team", "N/D")
            })
        
        # También extraer goles y asistencias del array "goal"
        goals = live_data.get("goal", [])
        match_info = match_data.get("matchInfo", {})
        contestants = match_info.get("contestant", [])
        
        for goal in goals:
            contestant_id = goal.get("contestantId", "")
            # Verificar si este gol es del equipo que estamos analizando
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    if team_name.lower() in name.lower():
                        scorer_id = goal.get("scorerId", "")
                        scorer_name = goal.get("scorerName", "")
                        assist_id = goal.get("assistPlayerId", "")
                        assist_name = goal.get("assistPlayerName", "")
                        
                        # Agregar gol al goleador
                        if scorer_id and scorer_id in player_stats:
                            player_stats[scorer_id]["goals"] += 1
                        elif scorer_name:
                            # Buscar por nombre si no encontramos por ID
                            for pid, pstat in player_stats.items():
                                if scorer_name.lower() in pstat["name"].lower() or pstat["name"].lower() in scorer_name.lower():
                                    player_stats[pid]["goals"] += 1
                                    break
                        
                        # Agregar asistencia
                        if assist_id and assist_id in player_stats:
                            player_stats[assist_id]["assists"] += 1
                        elif assist_name:
                            for pid, pstat in player_stats.items():
                                if assist_name.lower() in pstat["name"].lower() or pstat["name"].lower() in assist_name.lower():
                                    player_stats[pid]["assists"] += 1
                                    break
                    break
    
    return player_stats


def analyze_set_pieces(matches: List[Dict], team_name: str) -> Dict:
    """Analiza estadísticas de set pieces."""
    set_pieces_stats = {
        "corners": {"won": 0, "lost": 0, "total": 0},
        "free_kicks": {"won": 0, "lost": 0, "total": 0},
        "penalties": {"taken": 0, "scored": 0, "missed": 0},
        "matches": 0
    }
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        stats = match.get("opponent_stats", {})
        if not stats:
            continue
        
        set_pieces_stats["matches"] += 1
        
        # Corners
        corners_won = stats.get("wonCorners", 0)
        corners_lost = stats.get("lostCorners", 0)
        set_pieces_stats["corners"]["won"] += corners_won
        set_pieces_stats["corners"]["lost"] += corners_lost
        set_pieces_stats["corners"]["total"] += (corners_won + corners_lost)
        
        # Free kicks (fouls won/lost)
        fk_won = stats.get("fkFoulWon", 0)
        fk_lost = stats.get("fkFoulLost", 0)
        set_pieces_stats["free_kicks"]["won"] += fk_won
        set_pieces_stats["free_kicks"]["lost"] += fk_lost
        set_pieces_stats["free_kicks"]["total"] += (fk_won + fk_lost)
        
        # Penalties (necesitaríamos eventos específicos, por ahora usar stats si están disponibles)
        # Esto requeriría buscar en los eventos del partido
    
    # Calcular promedios
    if set_pieces_stats["matches"] > 0:
        matches_count = set_pieces_stats["matches"]
        set_pieces_stats["corners"]["avg_won"] = set_pieces_stats["corners"]["won"] / matches_count
        set_pieces_stats["corners"]["avg_lost"] = set_pieces_stats["corners"]["lost"] / matches_count
        set_pieces_stats["free_kicks"]["avg_won"] = set_pieces_stats["free_kicks"]["won"] / matches_count
        set_pieces_stats["free_kicks"]["avg_lost"] = set_pieces_stats["free_kicks"]["lost"] / matches_count
    
    return set_pieces_stats


def display_set_pieces_analysis(set_pieces_stats: Dict, team_name: str):
    """Muestra análisis de set pieces."""
    if not set_pieces_stats or set_pieces_stats["matches"] == 0:
        st.info("No hay datos de set pieces disponibles.")
        return
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Análisis de Set Pieces</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <h4 style='color:#ff8c00; margin-top:15px;'>Corners</h4>
        """, unsafe_allow_html=True)
        corners_won = set_pieces_stats["corners"]["won"]
        corners_lost = set_pieces_stats["corners"]["lost"]
        avg_won = set_pieces_stats["corners"].get("avg_won", 0)
        avg_lost = set_pieces_stats["corners"].get("avg_lost", 0)
        
        st.metric("Corners Ganados", f"{corners_won}", delta=f"{avg_won:.2f} por partido")
        st.metric("Corners Recibidos", f"{corners_lost}", delta=f"{avg_lost:.2f} por partido")
        
        if corners_won + corners_lost > 0:
            win_rate = (corners_won / (corners_won + corners_lost)) * 100
            st.metric("Tasa de Ganancia", f"{win_rate:.1f}%")
    
    with col2:
        st.markdown("""
        <h4 style='color:#ff8c00; margin-top:15px;'>Tiros Libres</h4>
        """, unsafe_allow_html=True)
        fk_won = set_pieces_stats["free_kicks"]["won"]
        fk_lost = set_pieces_stats["free_kicks"]["lost"]
        avg_won = set_pieces_stats["free_kicks"].get("avg_won", 0)
        avg_lost = set_pieces_stats["free_kicks"].get("avg_lost", 0)
        
        st.metric("Faltas a Favor", f"{fk_won}", delta=f"{avg_won:.2f} por partido")
        st.metric("Faltas en Contra", f"{fk_lost}", delta=f"{avg_lost:.2f} por partido")
        
        if fk_won + fk_lost > 0:
            win_rate = (fk_won / (fk_won + fk_lost)) * 100
            st.metric("Tasa de Ganancia", f"{win_rate:.1f}%")
    
    with col3:
        st.markdown("""
        <h4 style='color:#ff8c00; margin-top:15px;'>Penales</h4>
        """, unsafe_allow_html=True)
        penalties_taken = set_pieces_stats["penalties"]["taken"]
        penalties_scored = set_pieces_stats["penalties"]["scored"]
        penalties_missed = set_pieces_stats["penalties"]["missed"]
        
        st.metric("Penales Ejecutados", f"{penalties_taken}", delta="Total")
        if penalties_taken > 0:
            conversion_rate = (penalties_scored / penalties_taken) * 100
            st.metric("Conversión", f"{conversion_rate:.1f}%", delta=f"{penalties_scored}/{penalties_taken}")
        else:
            st.info("Sin datos de penales")
    
    # Gráfico de set pieces
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Comparación de Set Pieces</h3>
    """, unsafe_allow_html=True)
    
    categories = ["Corners\nGanados", "Corners\nRecibidos", "Faltas a\nFavor", "Faltas en\nContra"]
    values = [
        set_pieces_stats["corners"].get("avg_won", 0),
        set_pieces_stats["corners"].get("avg_lost", 0),
        set_pieces_stats["free_kicks"].get("avg_won", 0),
        set_pieces_stats["free_kicks"].get("avg_lost", 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=['#10B981', '#EF4444', '#10B981', '#EF4444'],
        text=[f"{v:.2f}" for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Tipo de Set Piece",
        yaxis_title="Promedio por Partido",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def analyze_timeline_patterns(matches: List[Dict], team_name: str) -> Dict:
    """Analiza patrones temporales de goles (cuándo marcan y reciben)."""
    timeline_stats = {
        "goals_for": {"0-15": 0, "16-30": 0, "31-45": 0, "46-60": 0, "61-75": 0, "76-90": 0, "90+": 0},
        "goals_against": {"0-15": 0, "16-30": 0, "31-45": 0, "46-60": 0, "61-75": 0, "76-90": 0, "90+": 0},
        "total_goals_for": 0,
        "total_goals_against": 0
    }
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        live_data = match_data.get("liveData", {})
        goals = live_data.get("goal", [])
        match_info = match_data.get("matchInfo", {})
        contestants = match_info.get("contestant", [])
        
        for goal in goals:
            contestant_id = goal.get("contestantId", "")
            time_min = goal.get("timeMin", 0)
            period_id = goal.get("periodId", 1)  # 1 = first half, 2 = second half
            
            # Determinar período de tiempo
            if period_id == 1:
                if time_min <= 15:
                    period = "0-15"
                elif time_min <= 30:
                    period = "16-30"
                else:
                    period = "31-45"
            else:  # period_id == 2
                if time_min <= 60:
                    period = "46-60"
                elif time_min <= 75:
                    period = "61-75"
                elif time_min <= 90:
                    period = "76-90"
                else:
                    period = "90+"
            
            # Verificar si el gol es del equipo analizado
            for contestant in contestants:
                if contestant.get("id") == contestant_id:
                    name = contestant.get("name") or contestant.get("shortName") or contestant.get("officialName", "")
                    if team_name.lower() in name.lower():
                        timeline_stats["goals_for"][period] += 1
                        timeline_stats["total_goals_for"] += 1
                    else:
                        timeline_stats["goals_against"][period] += 1
                        timeline_stats["total_goals_against"] += 1
                    break
    
    return timeline_stats


def display_timeline_patterns(timeline_stats: Dict, team_name: str):
    """Muestra patrones temporales de goles."""
    if timeline_stats["total_goals_for"] == 0 and timeline_stats["total_goals_against"] == 0:
        st.info("No hay datos de goles para análisis temporal.")
        return
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Patrones Temporales de Goles</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    periods = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "90+"]
    goals_for = [timeline_stats["goals_for"][p] for p in periods]
    goals_against = [timeline_stats["goals_against"][p] for p in periods]
    
    # Gráfico de barras
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Goles a Favor",
        x=periods,
        y=goals_for,
        marker_color='#10B981',
        text=goals_for,
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name="Goles en Contra",
        x=periods,
        y=goals_against,
        marker_color='#EF4444',
        text=goals_against,
        textposition='outside'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis_title="Minuto del Partido",
        yaxis_title="Cantidad de Goles",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas clave
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Insights Temporales</h3>
    """, unsafe_allow_html=True)
    
    # Encontrar períodos más productivos
    max_goals_period = max(periods, key=lambda p: timeline_stats["goals_for"][p])
    max_goals_value = timeline_stats["goals_for"][max_goals_period]
    
    # Encontrar períodos más vulnerables
    max_conceded_period = max(periods, key=lambda p: timeline_stats["goals_against"][p])
    max_conceded_value = timeline_stats["goals_against"][max_conceded_period]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if max_goals_value > 0:
            percentage = (max_goals_value / timeline_stats["total_goals_for"]) * 100 if timeline_stats["total_goals_for"] > 0 else 0
            st.metric(
                "Período Más Productivo",
                f"Minutos {max_goals_period}",
                delta=f"{max_goals_value} goles ({percentage:.1f}% del total)"
            )
        else:
            st.info("Sin goles registrados")
    
    with col2:
        if max_conceded_value > 0:
            percentage = (max_conceded_value / timeline_stats["total_goals_against"]) * 100 if timeline_stats["total_goals_against"] > 0 else 0
            st.metric(
                "Período Más Vulnerable",
                f"Minutos {max_conceded_period}",
                delta=f"{max_conceded_value} goles recibidos ({percentage:.1f}% del total)"
            )
        else:
            st.info("Sin goles recibidos")
    
    # Análisis de primera y segunda parte
    first_half_goals = sum(timeline_stats["goals_for"][p] for p in ["0-15", "16-30", "31-45"])
    second_half_goals = sum(timeline_stats["goals_for"][p] for p in ["46-60", "61-75", "76-90", "90+"])
    first_half_conceded = sum(timeline_stats["goals_against"][p] for p in ["0-15", "16-30", "31-45"])
    second_half_conceded = sum(timeline_stats["goals_against"][p] for p in ["46-60", "61-75", "76-90", "90+"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Primera Parte**")
        st.metric("Goles a Favor", first_half_goals)
        st.metric("Goles en Contra", first_half_conceded)
    
    with col2:
        st.markdown("**Segunda Parte**")
        st.metric("Goles a Favor", second_half_goals)
        st.metric("Goles en Contra", second_half_conceded)
    
    if timeline_stats["total_goals_for"] > 0:
        second_half_pct = (second_half_goals / timeline_stats["total_goals_for"]) * 100
        if second_half_pct >= 60:
            st.success(f"**Insight:** Este equipo marca {second_half_pct:.1f}% de sus goles en la segunda parte. Mantener la concentración defensiva en el segundo tiempo es crucial.")


def analyze_vulnerabilities(opponent_metrics: Dict, cibao_metrics: Dict, opponent_name: str) -> List[str]:
    """Identifica vulnerabilidades del oponente basándose en comparación con Cibao y promedios."""
    vulnerabilities = []
    
    # Comparar goles recibidos
    opp_goals_conceded = opponent_metrics.get("goalsConceded", 0)
    cibao_goals_conceded = cibao_metrics.get("goalsConceded", 0)
    if opp_goals_conceded > cibao_goals_conceded * 1.2:  # 20% más
        vulnerabilities.append(f"🛡**Defensa vulnerable:** Recibe {opp_goals_conceded:.2f} goles por partido (vs {cibao_goals_conceded:.2f} de Cibao). Oportunidad para atacar.")
    
    # Comparar precisión de pases
    opp_pass_acc = opponent_metrics.get("passAccuracy", 0)
    cibao_pass_acc = cibao_metrics.get("passAccuracy", 0)
    if opp_pass_acc < cibao_pass_acc - 5:  # 5% menos
        vulnerabilities.append(f"**Pases imprecisos:** {opp_pass_acc:.1f}% de precisión (vs {cibao_pass_acc:.1f}% de Cibao). Presionar alto puede forzar errores.")
    
    # Comparar tackles exitosos
    opp_tackle_success = opponent_metrics.get("tackleSuccess", 0)
    cibao_tackle_success = cibao_metrics.get("tackleSuccess", 0)
    if opp_tackle_success < cibao_tackle_success - 10:  # 10% menos
        vulnerabilities.append(f"**Tackles débiles:** {opp_tackle_success:.1f}% de efectividad (vs {cibao_tackle_success:.1f}% de Cibao). Aprovechar espacios en el medio campo.")
    
    # Analizar tarjetas (disciplina)
    opp_yellow = opponent_metrics.get("totalYellowCard", 0)
    opp_red = opponent_metrics.get("totalRedCard", 0)
    if opp_yellow > 2.5:  # Más de 2.5 tarjetas amarillas por partido
        vulnerabilities.append(f"**Disciplina débil:** {opp_yellow:.1f} tarjetas amarillas por partido. Aprovechar faltas y situaciones de set pieces.")
    
    # Analizar corners recibidos
    opp_corners_lost = opponent_metrics.get("lostCorners", 0)
    if opp_corners_lost > 5:  # Más de 5 corners recibidos por partido
        vulnerabilities.append(f"**Vulnerable en corners:** Recibe {opp_corners_lost:.1f} corners por partido. Trabajar jugadas a balón parado.")
    
    # Analizar posesión (si es baja, pueden ser vulnerables a presión)
    opp_possession = opponent_metrics.get("possessionPercentage", 0)
    if opp_possession < 45:
        vulnerabilities.append(f"**Baja posesión:** Solo {opp_possession:.1f}% de posesión promedio. Presionar alto puede recuperar balones rápidamente.")
    
    return vulnerabilities


def generate_match_recommendations(
    opponent_metrics: Dict,
    cibao_metrics: Dict,
    formation_stats: Dict,
    timeline_stats: Dict,
    set_pieces_stats: Dict,
    vulnerabilities: List[str],
    opponent_name: str
) -> List[str]:
    """Genera recomendaciones automáticas para la preparación del partido."""
    recommendations = []
    
    # Recomendaciones basadas en formaciones
    if formation_stats:
        sorted_formations = sorted(formation_stats.items(), key=lambda x: x[1]["count"], reverse=True)
        if sorted_formations:
            most_used = sorted_formations[0]
            formation = most_used[0]
            usage_pct = (most_used[1]["count"] / sum(s["count"] for _, s in formation_stats.items())) * 100
            if usage_pct >= 60:
                recommendations.append(f"**Formación esperada:** {formation} (usada en {usage_pct:.0f}% de partidos). Preparar tácticas específicas para esta formación.")
    
    # Recomendaciones basadas en patrones temporales
    if timeline_stats["total_goals_for"] > 0:
        second_half_pct = (sum(timeline_stats["goals_for"][p] for p in ["46-60", "61-75", "76-90", "90+"]) / timeline_stats["total_goals_for"]) * 100
        if second_half_pct >= 60:
            recommendations.append(f"**Concentración en segunda parte:** Marcan {second_half_pct:.0f}% de goles después del minuto 45. Mantener intensidad defensiva todo el partido.")
    
    # Recomendaciones basadas en set pieces
    if set_pieces_stats["matches"] > 0:
        corners_avg = set_pieces_stats["corners"].get("avg_won", 0)
        if corners_avg > 6:
            recommendations.append(f"**Atención a corners:** Obtienen {corners_avg:.1f} corners por partido. Trabajar defensa de balón parado y transiciones rápidas.")
    
    # Recomendaciones basadas en vulnerabilidades
    if vulnerabilities:
        recommendations.extend([f"**Explotar:** {v}" for v in vulnerabilities[:3]])  # Top 3 vulnerabilidades
    
    # Recomendaciones generales basadas en comparación
    opp_goals = opponent_metrics.get("goals", 0)
    cibao_goals = cibao_metrics.get("goals", 0)
    if opp_goals < cibao_goals * 0.8:
        recommendations.append(f"**Ventaja ofensiva:** Cibao marca más goles ({cibao_goals:.2f} vs {opp_goals:.2f}). Mantener presión ofensiva.")
    
    opp_possession = opponent_metrics.get("possessionPercentage", 0)
    cibao_possession = cibao_metrics.get("possessionPercentage", 0)
    if opp_possession < cibao_possession - 10:
        recommendations.append(f"**Control del juego:** Cibao tiene ventaja en posesión ({cibao_possession:.1f}% vs {opp_possession:.1f}%). Dominar el ritmo del partido.")
    
    return recommendations


def display_key_players_analysis(player_stats: Dict, team_name: str):
    """Muestra análisis de jugadores clave."""
    if not player_stats:
        st.info("No hay datos de jugadores disponibles para este equipo.")
        return
    
    # Convertir a lista y ordenar
    players_list = list(player_stats.values())
    
    # Top Scorers
    top_scorers = sorted(players_list, key=lambda x: x["goals"], reverse=True)[:10]
    
    # Top Assists
    top_assists = sorted(players_list, key=lambda x: x["assists"], reverse=True)[:10]
    
    # Most Regular Starters (by matches started)
    regular_starters = sorted(players_list, key=lambda x: x["matches_started"], reverse=True)[:11]
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Top Goleadores</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if top_scorers and any(p["goals"] > 0 for p in top_scorers):
        scorers_data = []
        for i, player in enumerate(top_scorers, 1):
            if player["goals"] > 0:
                scorers_data.append({
                    "#": i,
                    "Jugador": player["name"],
                    "Posición": player["position"],
                    "Goles": player["goals"],
                    "Asistencias": player["assists"],
                    "Partidos": player["matches_played"],
                    "Minutos": player["total_minutes"]
                })
        
        if scorers_data:
            df_scorers = pd.DataFrame(scorers_data)
            st.dataframe(df_scorers, use_container_width=True, hide_index=True)
        else:
            st.info("No hay goleadores registrados.")
    else:
        st.info("No hay goleadores registrados.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Top Asistentes</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if top_assists and any(p["assists"] > 0 for p in top_assists):
        assists_data = []
        for i, player in enumerate(top_assists, 1):
            if player["assists"] > 0:
                assists_data.append({
                    "#": i,
                    "Jugador": player["name"],
                    "Posición": player["position"],
                    "Asistencias": player["assists"],
                    "Goles": player["goals"],
                    "Partidos": player["matches_played"]
                })
        
        if assists_data:
            df_assists = pd.DataFrame(assists_data)
            st.dataframe(df_assists, use_container_width=True, hide_index=True)
        else:
            st.info("No hay asistencias registradas.")
    else:
        st.info("No hay asistencias registradas.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Jugadores Más Regulares (Alineación Inicial)</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if regular_starters:
        starters_data = []
        for i, player in enumerate(regular_starters, 1):
            starters_data.append({
                "#": i,
                "Jugador": player["name"],
                "Posición": player["position"],
                "Partidos Iniciados": player["matches_started"],
                "Partidos Totales": player["matches_played"],
                "Minutos Totales": player["total_minutes"],
                "Goles": player["goals"],
                "Asistencias": player["assists"]
            })
        
        df_starters = pd.DataFrame(starters_data)
        st.dataframe(df_starters, use_container_width=True, hide_index=True)
    
    # Gráfico de goles y asistencias
    if top_scorers and (any(p["goals"] > 0 for p in top_scorers) or any(p["assists"] > 0 for p in top_scorers)):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <h3 style='color:#ff8c00; margin-top:20px;'>Goles y Asistencias por Jugador</h3>
        """, unsafe_allow_html=True)
        
        # Preparar datos para el gráfico
        chart_players = [p for p in players_list if p["goals"] > 0 or p["assists"] > 0]
        chart_players = sorted(chart_players, key=lambda x: x["goals"] + x["assists"], reverse=True)[:10]
        
        if chart_players:
            player_names = [p["name"] for p in chart_players]
            goals = [p["goals"] for p in chart_players]
            assists = [p["assists"] for p in chart_players]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name="Goles",
                x=player_names,
                y=goals,
                marker_color='#EF4444',
                text=goals,
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name="Asistencias",
                x=player_names,
                y=assists,
                marker_color='#10B981',
                text=assists,
                textposition='outside'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500,
                xaxis_title="Jugador",
                yaxis_title="Cantidad",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                barmode='group',
                xaxis=dict(tickangle=-45)
            )
            
            st.plotly_chart(fig, use_container_width=True)


def display_formation_analysis(formation_stats: Dict, team_name: str):
    """Muestra el análisis de formaciones."""
    if not formation_stats:
        st.info("No hay datos de formaciones disponibles para este equipo.")
        return
    
    # Ordenar por frecuencia
    sorted_formations = sorted(
        formation_stats.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )
    
    st.markdown("""
    <h3 style='color:#ff8c00; margin-top:20px;'>Formaciones Más Utilizadas</h3>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Crear DataFrame para mostrar
    formation_data = []
    for formation, stats in sorted_formations:
        formation_data.append({
            "Formación": formation,
            "Partidos": stats["count"],
            "Victorias": stats["wins"],
            "Empates": stats["draws"],
            "Derrotas": stats["losses"],
            "% Victorias": f"{stats['win_rate']:.1f}%",
            "Goles a Favor": f"{stats['avg_goals_for']:.2f}",
            "Goles en Contra": f"{stats['avg_goals_against']:.2f}",
            "Diferencia": f"{stats['avg_goal_difference']:+.2f}"
        })
    
    df_formations = pd.DataFrame(formation_data)
    st.dataframe(df_formations, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráfico de barras: frecuencia de formaciones
    if len(sorted_formations) > 0:
        formations = [f[0] for f in sorted_formations]
        counts = [f[1]["count"] for f in sorted_formations]
        win_rates = [f[1]["win_rate"] for f in sorted_formations]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name="Partidos",
            x=formations,
            y=counts,
            marker_color='#EF4444',
            text=counts,
            textposition='outside',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            name="% Victorias",
            x=formations,
            y=win_rates,
            mode='lines+markers',
            line=dict(color='#10B981', width=3),
            marker=dict(size=10, color='#10B981'),
            yaxis='y2',
            text=[f"{wr:.1f}%" for wr in win_rates],
            textposition='top center'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            xaxis_title="Formación",
            yaxis=dict(title="Partidos", side='left'),
            yaxis2=dict(title="% Victorias", side='right', overlaying='y', range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            title=dict(
                text="Frecuencia y Efectividad de Formaciones",
                font=dict(size=16, color='#FFFFFF'),
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar detalles de la formación más usada
        if sorted_formations:
            most_used = sorted_formations[0]
            st.markdown(f"""
            <h3 style='color:#ff8c00; margin-top:20px;'>Formación Principal: <strong>{most_used[0]}</strong></h3>
            """, unsafe_allow_html=True)
            st.markdown(f"**Utilizada en {most_used[1]['count']} partidos** ({most_used[1]['count']/sum(s['count'] for _, s in sorted_formations)*100:.1f}% del total)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Victorias", most_used[1]["wins"], delta=f"{most_used[1]['win_rate']:.1f}%")
            with col2:
                st.metric("Goles a Favor", f"{most_used[1]['avg_goals_for']:.2f}", delta="Por partido")
            with col3:
                st.metric("Diferencia de Goles", f"{most_used[1]['avg_goal_difference']:+.2f}", delta="Por partido")


def display_comparison_charts(opponent_metrics: Dict[str, float], cibao_metrics: Dict[str, float], opponent_name: str):
    """Muestra gráficos de comparación lado a lado."""
    
    # Métricas para comparar
    comparison_metrics = [
        ("Goles", "goals", "", "Por partido"),
        ("Goles Recibidos", "goalsConceded", "", "Por partido"),
        ("Disparos", "totalScoringAtt", "", "Por partido"),
        ("Posesión", "possessionPercentage", "", "%"),
        ("Precisión Pases", "passAccuracy", "", "%"),
        ("Corners Ganados", "wonCorners", "", "Por partido"),
    ]
    
    # Crear gráfico de barras comparativo
    categories = [m[0] for m in comparison_metrics]
    opponent_vals = [opponent_metrics.get(m[1], 0) for m in comparison_metrics]
    cibao_vals = [cibao_metrics.get(m[1], 0) for m in comparison_metrics]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=opponent_name,
        x=categories,
        y=opponent_vals,
        marker_color='#EF4444',
        text=[f"{v:.2f}" for v in opponent_vals],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Cibao',
        x=categories,
        y=cibao_vals,
        marker_color='#FF8C00',
        text=[f"{v:.2f}" for v in cibao_vals],
        textposition='outside'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis_title="Métricas",
        yaxis_title="Valor",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        barmode='group',
        xaxis=dict(tickangle=-45)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ===========================================
# INTERFAZ PRINCIPAL
# ===========================================

def main():
    # Título
    st.markdown("""
    <h1 style='text-align:center; color:#FF9900; text-shadow: 0 0 15px rgba(255,153,0,0.65); font-weight:900;'>
        Análisis del Rival — Copa Concacaf
    </h1>
    <p style='text-align:center; color:#D1D5DB; font-size:17px;'>
        Análisis detallado de oponentes para preparación táctica y estratégica
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner("Cargando datos de partidos..."):
        all_matches = load_all_matches()
        cibao_matches = get_cibao_matches(all_matches)
    
    if not cibao_matches:
        st.error("No se encontraron partidos de Cibao. Verifique que los archivos JSON estén en la carpeta correcta.")
        return
    
    # Sidebar: Selector de equipo
    with st.sidebar:
        st.markdown("""
        <h3 style='margin-top:0; color:#ff7b00;'>Análisis Copa</h3>
        <hr style='margin-top:6px; margin-bottom:20px; opacity:0.3;'>
        """, unsafe_allow_html=True)
        
        # Obtener todos los equipos de todos los partidos
        all_teams_list = get_all_teams_from_matches(all_matches)
        
        # Obtener oponentes de Cibao para marcar próximos
        upcoming_opponents = get_upcoming_opponents(cibao_matches)
        upcoming_opponent_names = {name for name, _ in upcoming_opponents}
        
        # Selector de equipo
        if upcoming_opponents:
            # Crear opciones con próximos oponentes marcados
            opponent_options = []
            opponent_map = {}
            
            # Agregar próximos oponentes primero
            for name, match_info in upcoming_opponents:
                display_name = f"{name} (Próximo)"
                opponent_options.append(display_name)
                opponent_map[display_name] = name
            
            # Agregar otros equipos
            for name in all_teams_list:
                if name not in upcoming_opponent_names and name != CIBAO_TEAM_NAME:
                    opponent_options.append(name)
                    opponent_map[name] = name
            
            # Agregar Cibao al final si no está en la lista
            if CIBAO_TEAM_NAME not in [opponent_map.get(opt, opt) for opt in opponent_options]:
                opponent_options.append(CIBAO_TEAM_NAME)
                opponent_map[CIBAO_TEAM_NAME] = CIBAO_TEAM_NAME
            
            # Find default index for Defence Force (check both display name and mapped name)
            default_index = 0
            for i, opt in enumerate(opponent_options):
                mapped_name = opponent_map.get(opt, opt)
                if "Defence Force" in opt or mapped_name == "Defence Force":
                    default_index = i
                    break
            
            # Use session state to maintain selection, but default to Defence Force on first load
            if "opponent_selector_index" not in st.session_state:
                st.session_state.opponent_selector_index = default_index
            
            selected_display = st.selectbox(
                "Seleccionar Equipo",
                options=opponent_options,
                index=st.session_state.opponent_selector_index,
                key="opponent_selector",
                help="Selecciona el equipo que deseas analizar"
            )
            
            # Update session state with current selection
            current_index = opponent_options.index(selected_display)
            st.session_state.opponent_selector_index = current_index
            
            selected_opponent = opponent_map[selected_display]
        else:
            # Si no hay próximos, mostrar todos los equipos
            # Find default index for Defence Force
            default_index = 0
            for i, team in enumerate(all_teams_list):
                if team == "Defence Force":
                    default_index = i
                    break
            
            # Use session state to maintain selection, but default to Defence Force on first load
            if "opponent_selector_index" not in st.session_state:
                st.session_state.opponent_selector_index = default_index
            
            selected_opponent = st.selectbox(
                "Seleccionar Equipo",
                options=all_teams_list,
                index=st.session_state.opponent_selector_index,
                key="opponent_selector",
                help="Selecciona el equipo que deseas analizar"
            )
            
            # Update session state with current selection
            current_index = all_teams_list.index(selected_opponent)
            st.session_state.opponent_selector_index = current_index
        
        st.markdown("---")
        
        # Información del equipo seleccionado
        st.subheader("Información")
        
        # Encontrar partidos con este equipo (contra Cibao si es oponente, o todos si es otro equipo)
        if selected_opponent == CIBAO_TEAM_NAME:
            # Si es Cibao, mostrar partidos de Cibao
            team_matches = cibao_matches
            is_cibao = True
        else:
            # Si es otro equipo, buscar partidos contra Cibao
            team_matches = [m for m in cibao_matches if m.get("opponent") == selected_opponent]
            is_cibao = False
        
        if team_matches:
            # Ordenar por fecha
            team_matches.sort(key=lambda x: x.get("date") or datetime.min)
            
            # Último partido
            last_match = team_matches[-1]
            next_match = None
            
            # Buscar próximo partido (no jugado)
            for match in team_matches:
                status_lower = match.get("status", "").lower()
                if status_lower not in ["played", "finished", "ft", "jugado", "finalizado"]:
                    next_match = match
                    break
            
            if next_match:
                st.info(f"**Próximo partido:**\n{next_match.get('date_str', 'Por definir')}")
                if not is_cibao:
                    st.info(f"**Lugar:** {'Casa' if next_match.get('is_home') else 'Fuera'}")
            elif last_match:
                st.info(f"**Último encuentro:**\n{last_match.get('date_str', 'N/D')}")
                if not is_cibao:
                    st.info(f"**Lugar:** {'Casa' if last_match.get('is_home') else 'Fuera'}")
            
            if is_cibao:
                st.info(f"**Partidos totales:** {len(team_matches)}")
            else:
                st.info(f"**Partidos vs Cibao:** {len(team_matches)}")
    
    # Contenido principal
    st.markdown("---")
    
    # Mostrar información del equipo seleccionado
    # ---------- PAGE TITLE ----------
    titulo_naranja(f"Análisis del Rival — {selected_opponent}")
    
    st.markdown("""
    <p style='text-align:center; color:#D1D5DB; font-size:17px;'>
    Análisis completo del <b>rendimiento</b>, <b>tendencias</b> y <b>características tácticas</b> del equipo seleccionado.<br>
    Diseñado para soporte táctico del staff técnico — decisiones claras, con contexto.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Obtener todos los partidos del equipo seleccionado y métricas
    with st.spinner(f"Calculando métricas de {selected_opponent} y Cibao..."):
        if selected_opponent == CIBAO_TEAM_NAME:
            # Si es Cibao, usar función específica
            team_all_matches = get_opponent_matches_data(all_matches, CIBAO_TEAM_NAME)
            team_averages = calculate_average_metrics(team_all_matches)
        else:
            # Si es otro equipo, obtener todos sus partidos
            team_all_matches = get_opponent_matches_data(all_matches, selected_opponent)
            team_averages = calculate_average_metrics(team_all_matches)
        
        cibao_averages = get_cibao_average_metrics(all_matches)
        competition_averages = get_all_teams_average_metrics(all_matches)
    
    # Preparar datos adicionales para análisis táctico
    matches_with_data = []
    for match_info in team_all_matches:
        match_id = match_info.get("match_id", "")
        for match_data in all_matches:
            match_info_check = extract_match_info(match_data)
            if match_info_check and match_info_check.get("match_id") == match_id:
                matches_with_data.append({
                    **match_info,
                    "match_data": match_data
                })
                break
    
    
    # Crear pestañas principales (agrega Jugadores Clave aquí)
    tab_resumen, tab_comparacion, tab_jugadores = st.tabs([
        "Resumen",
        "Comparación",
        "Jugadores Clave"
    ])
    
    # TAB 1: RESUMEN (Métricas clave + Radar)
    with tab1:
        if team_averages:
            # Calcular datos iniciales sin filtro (para Forma Reciente)
            filtered_matches = team_all_matches
            filtered_averages = team_averages
            display_averages = team_averages
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Forma Reciente (movido arriba, antes de las métricas clave)
            st.markdown("""
            <h2 style='color:#FF9900; text-align:center; margin-top:20px;'>Forma Reciente</h2>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_matches:
                # Selector de número de partidos a mostrar
                num_matches_option = st.radio(
                    "Mostrar:",
                    options=["Todos los partidos", "Últimos 3 partidos", "Últimos 5 partidos"],
                    horizontal=True,
                    key="recent_form_num_matches"
                )
                
                # Determinar número de partidos
                if num_matches_option == "Todos los partidos":
                    num_matches = None  # None significa todos
                elif num_matches_option == "Últimos 3 partidos":
                    num_matches = 3
                else:
                    num_matches = 5
                
                # Obtener partidos recientes (de partidos filtrados)
                recent_form = get_recent_form(filtered_matches, selected_opponent, num_matches=num_matches)
                
                if recent_form:
                    display_recent_form(recent_form, selected_opponent)
                else:
                    st.info("No hay suficientes partidos jugados para mostrar el formulario reciente.")
            else:
                st.info("No hay partidos disponibles para este equipo.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Mostrar resumen de partidos (movido directamente arriba de Métricas Clave - 12 KPI cards)
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                # Contar partidos jugados - verificar status o si tiene score data
                played_count = 0
                for m in filtered_matches:
                    status = m.get("status", "")
                    # Verificar status
                    if isinstance(status, str) and status.lower() in ["played", "finished", "ft", "jugado", "finalizado"]:
                        played_count += 1
                    # Si no tiene status válido, verificar si tiene score (indica que fue jugado)
                    elif m.get("match_data"):
                        match_data = m.get("match_data", {})
                        live_data = match_data.get("liveData", {})
                        match_details = live_data.get("matchDetails", {})
                        scores = match_details.get("scores", {})
                        if scores and (scores.get("ft") or scores.get("total")):
                            played_count += 1
                        # También verificar por fecha pasada (si no hay score pero la fecha pasó, probablemente fue jugado)
                        elif m.get("date"):
                            from datetime import datetime
                            match_date = m.get("date")
                            if isinstance(match_date, str):
                                try:
                                    match_date = datetime.strptime(match_date, '%Y-%m-%d')
                                except:
                                    pass
                            if isinstance(match_date, datetime):
                                today = datetime.now()
                                if match_date < today:
                                    played_count += 1
                st.metric("Partidos Jugados", played_count)
            with col_info2:
                if selected_opponent != CIBAO_TEAM_NAME:
                    # Contar partidos donde ambos equipos jugaron (head-to-head) - solo partidos jugados
                    h2h_count = 0
                    seen_match_ids = set()  # Para evitar duplicados
                    cibao_name_lower = CIBAO_TEAM_NAME.lower().strip()
                    cibao_base = cibao_name_lower.replace(' fc', '').strip()
                    opponent_name_lower = selected_opponent.lower().strip()
                    opponent_base = opponent_name_lower.replace(' fc', '').strip()
                    
                    for match_data in all_matches:
                        match_info = extract_match_info(match_data)
                        if not match_info:
                            continue
                        
                        match_id = match_info.get("match_id", "")
                        # Evitar duplicados
                        if match_id in seen_match_ids:
                            continue
                        
                        # Solo contar partidos jugados (no futuros)
                        status = match_info.get("status", "").lower()
                        date_str = match_info.get("date", "")
                        is_played = status in ["played", "finished", "ft", "jugado", "finalizado"]
                        
                        # También verificar por fecha si no hay status
                        if not is_played and date_str:
                            try:
                                from datetime import datetime
                                match_date = datetime.strptime(date_str, '%Y-%m-%d')
                                today = datetime.now()
                                if match_date > today:
                                    continue  # Es un partido futuro
                            except:
                                pass
                        
                        if not is_played:
                            continue  # Saltar partidos no jugados
                        
                        home = match_info.get("home_team", "").lower().strip() if match_info.get("home_team") else ""
                        away = match_info.get("away_team", "").lower().strip() if match_info.get("away_team") else ""
                        
                        # Verificar si ambos equipos están en el partido
                        home_match_cibao = (cibao_name_lower in home or home in cibao_name_lower or
                                           cibao_base in home.replace(' fc', '').strip() or
                                           home.replace(' fc', '').strip() in cibao_base)
                        away_match_cibao = (cibao_name_lower in away or away in cibao_name_lower or
                                           cibao_base in away.replace(' fc', '').strip() or
                                           away.replace(' fc', '').strip() in cibao_base)
                        
                        home_match_opponent = (opponent_name_lower in home or home in opponent_name_lower or
                                              opponent_base in home.replace(' fc', '').strip() or
                                              home.replace(' fc', '').strip() in opponent_base)
                        away_match_opponent = (opponent_name_lower in away or away in opponent_name_lower or
                                              opponent_base in away.replace(' fc', '').strip() or
                                              away.replace(' fc', '').strip() in opponent_base)
                        
                        if (home_match_cibao or away_match_cibao) and (home_match_opponent or away_match_opponent):
                            h2h_count += 1
                            seen_match_ids.add(match_id)
                    
                    st.metric("Partidos vs Cibao", h2h_count)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Filtro de partidos (UI movido aquí para estar junto a Métricas Clave)
            filter_options_ui = {
                "Todos los Partidos": "all",
                "Partidos en Casa": "home",
                "Partidos Fuera": "away",
            }
            if selected_opponent != CIBAO_TEAM_NAME:
                filter_options_ui["Partidos vs Cibao"] = "vs_cibao"
            
            # Obtener el índice del filtro actual para mantener la selección
            current_filter_keys = list(filter_options_ui.keys())
            try:
                current_index = current_filter_keys.index(selected_filter)
            except:
                current_index = 0
            
            selected_filter_ui = st.radio(
                "Filtrar por:",
                options=current_filter_keys,
                horizontal=True,
                key="match_filter_ui",
                index=current_index
            )
            filter_type_ui = filter_options_ui[selected_filter_ui]
            
            # Recalcular con el filtro seleccionado
            filtered_matches_ui = filter_matches_by_type(team_all_matches, selected_opponent, filter_type_ui, all_matches)
            filtered_averages_ui = calculate_average_metrics(filtered_matches_ui) if filtered_matches_ui else {}
            display_averages_ui = filtered_averages_ui if filtered_averages_ui else team_averages
            
            # Calcular promedios filtrados de competencia y Cibao
            filtered_competition_averages = get_all_teams_average_metrics(all_matches, filter_type_ui, selected_opponent)
            filtered_cibao_averages = get_cibao_average_metrics_filtered(all_matches, filter_type_ui, selected_opponent)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Mostrar resumen de partidos (directamente arriba de Métricas Clave - 12 KPI cards)
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                # Contar partidos jugados - verificar status o si tiene score data
                played_count = 0
                for m in filtered_matches_ui:
                    status = m.get("status", "")
                    # Verificar status
                    if isinstance(status, str) and status.lower() in ["played", "finished", "ft", "jugado", "finalizado"]:
                        played_count += 1
                    # Si no tiene status válido, verificar si tiene score (indica que fue jugado)
                    elif m.get("match_data"):
                        match_data = m.get("match_data", {})
                        live_data = match_data.get("liveData", {})
                        match_details = live_data.get("matchDetails", {})
                        scores = match_details.get("scores", {})
                        if scores and (scores.get("ft") or scores.get("total")):
                            played_count += 1
                        # También verificar por fecha pasada (si no hay score pero la fecha pasó, probablemente fue jugado)
                        elif m.get("date"):
                            from datetime import datetime
                            match_date = m.get("date")
                            if isinstance(match_date, str):
                                try:
                                    match_date = datetime.strptime(match_date, '%Y-%m-%d')
                                except:
                                    pass
                            if isinstance(match_date, datetime):
                                today = datetime.now()
                                if match_date < today:
                                    played_count += 1
                st.metric("Partidos Jugados", played_count)
            with col_info2:
                if selected_opponent != CIBAO_TEAM_NAME:
                    # Contar partidos donde ambos equipos jugaron (head-to-head) - solo partidos jugados
                    h2h_count = 0
                    seen_match_ids = set()  # Para evitar duplicados
                    cibao_name_lower = CIBAO_TEAM_NAME.lower().strip()
                    cibao_base = cibao_name_lower.replace(' fc', '').strip()
                    opponent_name_lower = selected_opponent.lower().strip()
                    opponent_base = opponent_name_lower.replace(' fc', '').strip()
                    
                    for match_data in all_matches:
                        match_info = extract_match_info(match_data)
                        if not match_info:
                            continue
                        
                        match_id = match_info.get("match_id", "")
                        # Evitar duplicados
                        if match_id in seen_match_ids:
                            continue
                        
                        # Solo contar partidos jugados (no futuros)
                        status = match_info.get("status", "").lower()
                        date_str = match_info.get("date", "")
                        is_played = status in ["played", "finished", "ft", "jugado", "finalizado"]
                        
                        # También verificar por fecha si no hay status
                        if not is_played and date_str:
                            try:
                                from datetime import datetime
                                match_date = datetime.strptime(date_str, '%Y-%m-%d')
                                today = datetime.now()
                                if match_date > today:
                                    continue  # Es un partido futuro
                            except:
                                pass
                        
                        if not is_played:
                            continue  # Saltar partidos no jugados
                        
                        home = match_info.get("home_team", "").lower().strip() if match_info.get("home_team") else ""
                        away = match_info.get("away_team", "").lower().strip() if match_info.get("away_team") else ""
                        
                        # Verificar si ambos equipos están en el partido
                        home_match_cibao = (cibao_name_lower in home or home in cibao_name_lower or
                                           cibao_base in home.replace(' fc', '').strip() or
                                           home.replace(' fc', '').strip() in cibao_base)
                        away_match_cibao = (cibao_name_lower in away or away in cibao_name_lower or
                                           cibao_base in away.replace(' fc', '').strip() or
                                           away.replace(' fc', '').strip() in cibao_base)
                        home_match_opponent = (opponent_name_lower in home or home in opponent_name_lower or
                                              opponent_base in home.replace(' fc', '').strip() or
                                              home.replace(' fc', '').strip() in opponent_base)
                        away_match_opponent = (opponent_name_lower in away or away in opponent_name_lower or
                                              opponent_base in away.replace(' fc', '').strip() or
                                              away.replace(' fc', '').strip() in opponent_base)
                        
                        if (home_match_cibao or away_match_cibao) and (home_match_opponent or away_match_opponent):
                            h2h_count += 1
                            seen_match_ids.add(match_id)
                    
                    st.metric("Partidos vs Cibao", h2h_count)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <h2 style='color:#FF9900; text-align:center; margin-top:20px;'>Métricas Clave</h2>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fila 1: Ofensivas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                goals = display_averages_ui.get("goals", 0)
                comp_goals = filtered_competition_averages.get("goals", 0) if filtered_competition_averages else 0
                cibao_goals = filtered_cibao_averages.get("goals", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Goles por Partido",
                    f"{goals:.2f}",
                    "",
                    f"Promedio en {len(filtered_matches_ui)} partidos",
                    competition_avg=f"{comp_goals:.2f}",
                    cibao_avg=f"{cibao_goals:.2f}"
                )
            
            with col2:
                shots = display_averages_ui.get("totalScoringAtt", 0)
                shots_on_target = display_averages_ui.get("ontargetScoringAtt", 0)
                shot_accuracy = (shots_on_target / shots * 100) if shots > 0 else 0
                comp_shots = filtered_competition_averages.get("totalScoringAtt", 0) if filtered_competition_averages else 0
                cibao_shots = filtered_cibao_averages.get("totalScoringAtt", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Disparos por Partido",
                    f"{shots:.1f}",
                    "",
                    f"{shot_accuracy:.1f}% precisión",
                    competition_avg=f"{comp_shots:.1f}",
                    cibao_avg=f"{cibao_shots:.1f}"
                )
            
            with col3:
                shots_on_target = display_averages_ui.get("ontargetScoringAtt", 0)
                comp_sot = filtered_competition_averages.get("ontargetScoringAtt", 0) if filtered_competition_averages else 0
                cibao_sot = filtered_cibao_averages.get("ontargetScoringAtt", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Disparos al Arco",
                    f"{shots_on_target:.1f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_sot:.1f}",
                    cibao_avg=f"{cibao_sot:.1f}"
                )
            
            with col4:
                possession = display_averages_ui.get("possessionPercentage", 0)
                comp_poss = filtered_competition_averages.get("possessionPercentage", 0) if filtered_competition_averages else 0
                cibao_poss = filtered_cibao_averages.get("possessionPercentage", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Posesión %",
                    f"{possession:.1f}%",
                    "",
                    f"Promedio",
                    competition_avg=f"{comp_poss:.1f}%",
                    cibao_avg=f"{cibao_poss:.1f}%"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fila 2: Defensivas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                goals_conceded = display_averages_ui.get("goalsConceded", 0)
                comp_gc = filtered_competition_averages.get("goalsConceded", 0) if filtered_competition_averages else 0
                cibao_gc = filtered_cibao_averages.get("goalsConceded", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Goles Recibidos",
                    f"{goals_conceded:.2f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_gc:.2f}",
                    cibao_avg=f"{cibao_gc:.2f}",
                    higher_is_better=False  # Lower is better for goals conceded
                )
            
            with col2:
                saves = display_averages_ui.get("saves", 0)
                comp_saves = filtered_competition_averages.get("saves", 0) if filtered_competition_averages else 0
                cibao_saves = filtered_cibao_averages.get("saves", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Atajadas",
                    f"{saves:.1f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_saves:.1f}",
                    cibao_avg=f"{cibao_saves:.1f}"
                )
            
            with col3:
                clearances = display_averages_ui.get("totalClearance", 0)
                comp_clear = filtered_competition_averages.get("totalClearance", 0) if filtered_competition_averages else 0
                cibao_clear = filtered_cibao_averages.get("totalClearance", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Despejes",
                    f"{clearances:.1f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_clear:.1f}",
                    cibao_avg=f"{cibao_clear:.1f}"
                )
            
            with col4:
                tackles_won = display_averages_ui.get("wonTackle", 0)
                tackle_success = display_averages_ui.get("tackleSuccess", 0)
                comp_tackles = filtered_competition_averages.get("wonTackle", 0) if filtered_competition_averages else 0
                cibao_tackles = filtered_cibao_averages.get("wonTackle", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Tackles Exitosos",
                    f"{tackles_won:.1f}",
                    "",
                    f"{tackle_success:.1f}% efectividad",
                    competition_avg=f"{comp_tackles:.1f}",
                    cibao_avg=f"{cibao_tackles:.1f}"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fila 3: Set Pieces y Disciplina
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                corners_won = display_averages_ui.get("wonCorners", 0)
                comp_corners = filtered_competition_averages.get("wonCorners", 0) if filtered_competition_averages else 0
                cibao_corners = filtered_cibao_averages.get("wonCorners", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Corners Ganados",
                    f"{corners_won:.1f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_corners:.1f}",
                    cibao_avg=f"{cibao_corners:.1f}"
                )
            
            with col2:
                pass_accuracy = display_averages_ui.get("passAccuracy", 0)
                comp_pass_acc = filtered_competition_averages.get("passAccuracy", 0) if filtered_competition_averages else 0
                cibao_pass_acc = filtered_cibao_averages.get("passAccuracy", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Precisión de Pases",
                    f"{pass_accuracy:.1f}%",
                    "",
                    f"Promedio",
                    competition_avg=f"{comp_pass_acc:.1f}%",
                    cibao_avg=f"{cibao_pass_acc:.1f}%"
                )
            
            with col3:
                fouls = display_averages_ui.get("fkFoulLost", 0)
                comp_fouls = filtered_competition_averages.get("fkFoulLost", 0) if filtered_competition_averages else 0
                cibao_fouls = filtered_cibao_averages.get("fkFoulLost", 0) if filtered_cibao_averages else 0
                display_metric_card(
                    "Faltas Cometidas",
                    f"{fouls:.1f}",
                    "",
                    f"Por partido",
                    competition_avg=f"{comp_fouls:.1f}",
                    cibao_avg=f"{cibao_fouls:.1f}",
                    higher_is_better=False  # Lower is better for fouls
                )
            
            with col4:
                yellow_cards = display_averages_ui.get("totalYellowCard", 0)
                red_cards = display_averages_ui.get("totalRedCard", 0)
                total_cards = yellow_cards + red_cards
                comp_yellow = filtered_competition_averages.get("totalYellowCard", 0) if filtered_competition_averages else 0
                comp_red = filtered_competition_averages.get("totalRedCard", 0) if filtered_competition_averages else 0
                comp_total = comp_yellow + comp_red
                cibao_yellow = filtered_cibao_averages.get("totalYellowCard", 0) if filtered_cibao_averages else 0
                cibao_red = filtered_cibao_averages.get("totalRedCard", 0) if filtered_cibao_averages else 0
                cibao_total = cibao_yellow + cibao_red
                display_metric_card(
                    "Tarjetas",
                    f"{total_cards:.1f}",
                    "",
                    f"{yellow_cards:.1f}A, {red_cards:.1f}R",
                    competition_avg=f"{comp_total:.1f}",
                    cibao_avg=f"{cibao_total:.1f}",
                    higher_is_better=False  # Lower is better for cards
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No se pudieron calcular las métricas del equipo.")
    
    # TAB 2: COMPARACIÓN (Gráficos comparativos + Radar Chart)
    with tab2:
        if team_averages and cibao_averages and selected_opponent != CIBAO_TEAM_NAME:
            st.markdown(f"### Comparación Directa: {selected_opponent} vs Cibao")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Radar Chart: Fortalezas y Debilidades (movido desde Resumen)
            st.markdown("""
            <h2 style='color:#FF9900; text-align:center; margin-top:20px;'>Comparación de Fortalezas y Debilidades</h2>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Selector de métricas para el radar chart
            all_available_metrics = [
                "Goles", "Goles Recibidos", "Disparos", "Disparos al Arco",
                "Posesión", "Precisión Pases", "Pases Totales", "Pases Precisos",
                "Corners", "Tackles Exitosos", "Tackles Totales", "Despejes",
                "Intercepciones", "Atajadas", "Faltas", "Tarjetas Amarillas"
            ]
            
            default_metrics = [
                "Goles", "Goles Recibidos", "Disparos", "Posesión",
                "Precisión Pases", "Corners", "Tackles Exitosos", "Despejes"
            ]
            
            selected_radar_metrics = st.multiselect(
                "Seleccionar métricas para comparar:",
                options=all_available_metrics,
                default=default_metrics,
                key="radar_metrics_selector",
                help="Selecciona las métricas que deseas comparar en el gráfico de radar"
            )
            
            if selected_radar_metrics:
                # Usar métricas del equipo para el radar chart
                radar_fig = create_radar_chart(team_averages, cibao_averages, selected_opponent, selected_radar_metrics)
                st.plotly_chart(radar_fig, use_container_width=True)
            else:
                st.info("Selecciona al menos una métrica para mostrar el gráfico de radar.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de tendencia de goles (movido desde Resumen)
            st.markdown("""
            <h2 style='color:#FF9900; text-align:center; margin-top:20px;'>Tendencia de Goles</h2>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Obtener partidos recientes del equipo seleccionado
            team_recent_matches = get_recent_form(team_all_matches, selected_opponent, num_matches=None)
            
            if team_recent_matches and len(team_recent_matches) > 1:
                dates = [m["date"] for m in reversed(team_recent_matches)]
                goals_for = [m["team_goals"] for m in reversed(team_recent_matches)]
                goals_against = [m["opponent_goals"] for m in reversed(team_recent_matches)]
                
                fig = go.Figure()
                
                # Línea de goles a favor
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=goals_for,
                    mode='lines+markers',
                    name=f'Goles a Favor - {selected_opponent}',
                    line=dict(color='#10B981', width=3),
                    marker=dict(size=10, color='#10B981')
                ))
                
                # Línea de goles en contra
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=goals_against,
                    mode='lines+markers',
                    name=f'Goles en Contra - {selected_opponent}',
                    line=dict(color='#EF4444', width=3),
                    marker=dict(size=10, color='#EF4444')
                ))
                
                # Si no es Cibao, agregar líneas de Cibao para comparación
                if selected_opponent != CIBAO_TEAM_NAME:
                    # Obtener partidos de Cibao para comparación
                    cibao_all_matches = get_opponent_matches_data(all_matches, CIBAO_TEAM_NAME)
                    cibao_recent_matches = get_recent_form(cibao_all_matches, CIBAO_TEAM_NAME, num_matches=None)
                    if cibao_recent_matches and len(cibao_recent_matches) > 1:
                        cibao_dates = [m["date"] for m in reversed(cibao_recent_matches)]
                        cibao_goals_for = [m["team_goals"] for m in reversed(cibao_recent_matches)]
                        cibao_goals_against = [m["opponent_goals"] for m in reversed(cibao_recent_matches)]
                        
                        fig.add_trace(go.Scatter(
                            x=cibao_dates,
                            y=cibao_goals_for,
                            mode='lines+markers',
                            name='Goles a Favor - Cibao',
                            line=dict(color='#FF9900', width=3, dash='dash'),
                            marker=dict(size=10, color='#FF9900')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=cibao_dates,
                            y=cibao_goals_against,
                            mode='lines+markers',
                            name='Goles en Contra - Cibao',
                            line=dict(color='#F97316', width=3, dash='dash'),
                            marker=dict(size=10, color='#F97316')
                        ))
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    xaxis_title="Fecha",
                    yaxis_title="Goles",
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=18)
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=18)
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=18)
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay suficientes partidos para mostrar la tendencia de goles.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos comparativos
            display_comparison_charts(team_averages, cibao_averages, selected_opponent)
        elif selected_opponent == CIBAO_TEAM_NAME:
            st.info("Selecciona otro equipo para ver comparación con Cibao")
        else:
            st.warning("⚠No se pudieron calcular las métricas para la comparación.")
    
    # Tabs ocultos por ahora - se trabajarán más adelante
    # TAB 3: FORMA RECIENTE
    # TAB 4: CARA A CARA
    
    # TAB 5: Jugadores Clave y Comparativa
    tab_jugadores = st.tabs(["Jugadores Clave"])[0]

    with tab_jugadores:
        st.markdown(f"### Jugadores Clave de {selected_opponent}")
        st.markdown("<br>", unsafe_allow_html=True)

        if matches_with_data:
            with st.spinner("Analizando jugadores..."):
                player_stats = extract_player_stats_from_matches(
                    matches_with_data,
                    selected_opponent
                )
                display_key_players_analysis(player_stats, selected_opponent)
        else:
            st.info("No hay datos de jugadores disponibles.")
    # TAB 6: ANÁLISIS TÁCTICO
    # TAB 7: RECOMENDACIONES
    
    # Tabs 3-7 ocultos temporalmente - se trabajarán más adelante
    # El código de estos tabs está comentado y se restaurará cuando se trabaje en ellos


if __name__ == "__main__":
    main()
