# ===========================================
# 8_Analisis_Tactico_y_Fases.py — Análisis Táctico y Fases del Partido
# ===========================================
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import csv

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

# === IMPORTA EL TEMA OSCURO GLOBAL + TÍTULOS NARANJA ===
from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja

# ===========================================
# CONFIGURACIÓN
# ===========================================
st.set_page_config(
    page_title="Análisis Táctico y Fases del Partido | Cibao FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ACTIVAR TEMA OSCURO GLOBAL ----------
inject_dark_theme()

# ===========================================
# CONSTANTES
# ===========================================
CIBAO_TEAM_NAME = "Cibao"
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "concacaf"
MATCHSTATS_DIR = DATA_DIR / "matchstats"

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

# ===========================================
# FUNCIONES DE CARGA DE DATOS
# ===========================================
def load_all_matches() -> List[Dict]:
    """Carga todos los partidos desde los archivos JSON."""
    matches = []
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
        
        match_status_raw = match_details.get("matchStatus", "Scheduled")
        status_translation = {
            "Scheduled": "Programado",
            "Played": "Jugado",
            "Finished": "Finalizado",
            "FT": "Finalizado",
            "Not Started": "No Iniciado"
        }
        match_status = status_translation.get(match_status_raw, match_status_raw)
        
        if not match_status or match_status == "Unknown" or match_status == {}:
            scores = match_details.get("scores", {})
            if scores and (scores.get("ft") or scores.get("total")):
                match_status = "Jugado"
        
        return {
            "match_id": match_info.get("id", ""),
            "date": match_date,
            "date_str": match_date_str,
            "home_team": home_team,
            "away_team": away_team,
            "status": match_status,
            "description": match_info.get("description", f"{home_team} vs {away_team}"),
            "match_data": match_data
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
        
        home = match_info["home_team"] or ""
        away = match_info["away_team"] or ""
        
        if CIBAO_TEAM_NAME.lower() in home.lower() or CIBAO_TEAM_NAME.lower() in away.lower():
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

def extract_match_result(match_data: Dict, team_name: str) -> Optional[Dict]:
    """Extrae el resultado de un partido para un equipo específico."""
    try:
        live_data = match_data.get("liveData", {})
        match_details = live_data.get("matchDetails", {})
        match_info = match_data.get("matchInfo", {})
        
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
        
        if not home_team and contestants:
            home_team = contestants[0].get("name") or contestants[0].get("shortName", "")
        if not away_team and len(contestants) > 1:
            away_team = contestants[1].get("name") or contestants[1].get("shortName", "")
        
        if team_name.lower() in (home_team or "").lower():
            team_is_home = True
            opponent_name = away_team
        elif team_name.lower() in (away_team or "").lower():
            team_is_home = False
            opponent_name = home_team
        else:
            return None
        
        scores = match_details.get("scores", {})
        total_scores = scores.get("total", {})
        home_goals = total_scores.get("home", 0)
        away_goals = total_scores.get("away", 0)
        
        if team_is_home:
            team_goals = home_goals
            opponent_goals = away_goals
        else:
            team_goals = away_goals
            opponent_goals = home_goals
        
        if team_goals > opponent_goals:
            result = "W"
        elif team_goals < opponent_goals:
            result = "L"
        else:
            result = "D"
        
        return {
            "opponent": opponent_name,
            "team_goals": team_goals,
            "opponent_goals": opponent_goals,
            "result": result,
            "is_home": team_is_home,
            "score": f"{team_goals}-{opponent_goals}"
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

# ===========================================
# FUNCIONES DE ANÁLISIS TÁCTICO
# ===========================================
def extract_formation_from_match(match_data: Dict, team_name: str) -> Optional[str]:
    """Extrae la formación utilizada por un equipo en un partido."""
    try:
        live_data = match_data.get("liveData", {})
        lineups = live_data.get("lineUp", [])
        
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
        
        stats_list = team_lineup.get("stat", [])
        for stat in stats_list:
            if stat.get("type") == "formationUsed":
                return stat.get("value", "")
        
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
    
    for formation, stats in formation_stats.items():
        total = stats["count"]
        if total > 0:
            stats["win_rate"] = (stats["wins"] / total) * 100
            stats["avg_goals_for"] = stats["goals_for"] / total
            stats["avg_goals_against"] = stats["goals_against"] / total
            stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]
            stats["avg_goal_difference"] = stats["goal_difference"] / total
    
    return formation_stats

def extract_match_events(match_data: Dict, team_name: str, opponent_name: str) -> List[Dict]:
    """Extrae todos los eventos del partido ordenados cronológicamente."""
    if not match_data:
        return []
    
    live_data = match_data.get("liveData", {})
    if not live_data:
        return []
    
    events = []
    match_info_data = match_data.get("matchInfo", {})
    contestants = match_info_data.get("contestant", [])
    
    contestant_to_team = {}
    for contestant in contestants:
        contestant_id = contestant.get("id", "")
        team_name_from_contestant = contestant.get("name") or contestant.get("shortName", "")
        contestant_to_team[contestant_id] = team_name_from_contestant
    
    goals = live_data.get("goal", [])
    for goal in goals:
        contestant_id = goal.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        home_score = goal.get("homeScore", 0)
        away_score = goal.get("awayScore", 0)
        
        events.append({
            "type": "goal",
            "time": goal.get("timeMin", 0),
            "team": team_name if is_team_event else opponent_name,
            "is_team": is_team_event,
            "score_after": f"{home_score}-{away_score}"
        })
    
    cards = live_data.get("card", [])
    for card in cards:
        contestant_id = card.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        events.append({
            "type": "card",
            "time": card.get("timeMin", 0),
            "team": team_name if is_team_event else opponent_name,
            "is_team": is_team_event,
            "card_type": card.get("type", "")
        })
    
    substitutions = live_data.get("substitute", [])
    for sub in substitutions:
        contestant_id = sub.get("contestantId", "")
        event_team = contestant_to_team.get(contestant_id, "")
        is_team_event = (event_team == team_name)
        
        events.append({
            "type": "substitution",
            "time": sub.get("timeMin", 0),
            "team": team_name if is_team_event else opponent_name,
            "is_team": is_team_event
        })
    
    events.sort(key=lambda x: x["time"])
    return events

def analyze_match_phases(matches: List[Dict], team_name: str) -> Dict:
    """Analiza el rendimiento por fases del partido."""
    phase_stats = {
        "first_15": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "16_30": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "31_45": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "46_60": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "61_75": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "76_90": {"goals_for": 0, "goals_against": 0, "matches": 0},
        "90_plus": {"goals_for": 0, "goals_against": 0, "matches": 0}
    }
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        match_info = extract_match_info(match_data)
        opponent = match_info.get("opponent", "") if match_info else ""
        
        events = extract_match_events(match_data, team_name, opponent)
        
        phase_stats["first_15"]["matches"] += 1
        phase_stats["16_30"]["matches"] += 1
        phase_stats["31_45"]["matches"] += 1
        phase_stats["46_60"]["matches"] += 1
        phase_stats["61_75"]["matches"] += 1
        phase_stats["76_90"]["matches"] += 1
        phase_stats["90_plus"]["matches"] += 1
        
        for event in events:
            if event["type"] != "goal":
                continue
            
            time = event["time"]
            is_team = event["is_team"]
            
            if time <= 15:
                if is_team:
                    phase_stats["first_15"]["goals_for"] += 1
                else:
                    phase_stats["first_15"]["goals_against"] += 1
            elif time <= 30:
                if is_team:
                    phase_stats["16_30"]["goals_for"] += 1
                else:
                    phase_stats["16_30"]["goals_against"] += 1
            elif time <= 45:
                if is_team:
                    phase_stats["31_45"]["goals_for"] += 1
                else:
                    phase_stats["31_45"]["goals_against"] += 1
            elif time <= 60:
                if is_team:
                    phase_stats["46_60"]["goals_for"] += 1
                else:
                    phase_stats["46_60"]["goals_against"] += 1
            elif time <= 75:
                if is_team:
                    phase_stats["61_75"]["goals_for"] += 1
                else:
                    phase_stats["61_75"]["goals_against"] += 1
            elif time <= 90:
                if is_team:
                    phase_stats["76_90"]["goals_for"] += 1
                else:
                    phase_stats["76_90"]["goals_against"] += 1
            else:
                if is_team:
                    phase_stats["90_plus"]["goals_for"] += 1
                else:
                    phase_stats["90_plus"]["goals_against"] += 1
    
    # Calcular promedios
    for phase in phase_stats.values():
        if phase["matches"] > 0:
            phase["avg_goals_for"] = phase["goals_for"] / phase["matches"]
            phase["avg_goals_against"] = phase["goals_against"] / phase["matches"]
    
    return phase_stats

def analyze_event_patterns(matches: List[Dict], team_name: str) -> Dict:
    """Analiza patrones de eventos (cuándo ocurren goles, tarjetas, sustituciones)."""
    patterns = {
        "goal_times": [],
        "card_times": [],
        "substitution_times": [],
        "goals_after_scoring": {"for": 0, "against": 0},
        "goals_after_conceding": {"for": 0, "against": 0}
    }
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        match_info = extract_match_info(match_data)
        opponent = match_info.get("opponent", "") if match_info else ""
        
        events = extract_match_events(match_data, team_name, opponent)
        
        last_goal_time = None
        last_goal_team = None
        
        for event in events:
            if event["type"] == "goal":
                time = event["time"]
                is_team = event["is_team"]
                patterns["goal_times"].append({"time": time, "is_team": is_team})
                
                if last_goal_time is not None:
                    time_diff = time - last_goal_time
                    if time_diff <= 10:  # Gol dentro de 10 minutos
                        if last_goal_team == team_name and is_team:
                            patterns["goals_after_scoring"]["for"] += 1
                        elif last_goal_team == team_name and not is_team:
                            patterns["goals_after_scoring"]["against"] += 1
                        elif last_goal_team != team_name and is_team:
                            patterns["goals_after_conceding"]["for"] += 1
                        elif last_goal_team != team_name and not is_team:
                            patterns["goals_after_conceding"]["against"] += 1
                
                last_goal_time = time
                last_goal_team = team_name if is_team else opponent
            
            elif event["type"] == "card":
                patterns["card_times"].append(event["time"])
            
            elif event["type"] == "substitution":
                patterns["substitution_times"].append(event["time"])
    
    return patterns

def analyze_momentum(matches: List[Dict], team_name: str) -> Dict:
    """Analiza cambios de momentum durante los partidos."""
    momentum_data = {
        "comebacks": 0,
        "blown_leads": 0,
        "comeback_wins": 0,
        "comeback_draws": 0,
        "comeback_losses": 0
    }
    
    for match in matches:
        match_data = match.get("match_data")
        if not match_data:
            continue
        
        match_info = extract_match_info(match_data)
        opponent = match_info.get("opponent", "") if match_info else ""
        
        events = extract_match_events(match_data, team_name, opponent)
        goals = [e for e in events if e["type"] == "goal"]
        
        if len(goals) < 2:
            continue
        
        # Calcular score en cada momento
        team_score = 0
        opp_score = 0
        was_leading = False
        was_trailing = False
        came_back = False
        blew_lead = False
        
        for goal in goals:
            if goal["is_team"]:
                team_score += 1
            else:
                opp_score += 1
            
            if team_score > opp_score:
                if was_trailing:
                    came_back = True
                was_leading = True
                was_trailing = False
            elif team_score < opp_score:
                if was_leading:
                    blew_lead = True
                was_trailing = True
                was_leading = False
            else:
                was_leading = False
                was_trailing = False
        
        if came_back:
            momentum_data["comebacks"] += 1
            result = extract_match_result(match_data, team_name)
            if result:
                if result["result"] == "W":
                    momentum_data["comeback_wins"] += 1
                elif result["result"] == "D":
                    momentum_data["comeback_draws"] += 1
                else:
                    momentum_data["comeback_losses"] += 1
        
        if blew_lead:
            momentum_data["blown_leads"] += 1
    
    return momentum_data

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
        
        stats = extract_team_stats_from_match(match_data, team_name)
        if not stats:
            continue
        
        set_pieces_stats["matches"] += 1
        
        corners_won = stats.get("wonCorners", 0) or stats.get("cornersWon", 0) or 0
        corners_lost = stats.get("lostCorners", 0) or stats.get("cornersLost", 0) or 0
        set_pieces_stats["corners"]["won"] += corners_won
        set_pieces_stats["corners"]["lost"] += corners_lost
        set_pieces_stats["corners"]["total"] += (corners_won + corners_lost)
        
        fk_won = stats.get("fkFoulWon", 0) or stats.get("foulsWon", 0) or 0
        fk_lost = stats.get("fkFoulLost", 0) or stats.get("foulsConceded", 0) or 0
        set_pieces_stats["free_kicks"]["won"] += fk_won
        set_pieces_stats["free_kicks"]["lost"] += fk_lost
        set_pieces_stats["free_kicks"]["total"] += (fk_won + fk_lost)
        
        # Buscar penales en eventos
        match_info = extract_match_info(match_data)
        opponent = match_info.get("opponent", "") if match_info else ""
        events = extract_match_events(match_data, team_name, opponent)
        
        for event in events:
            if event["type"] == "goal" and "penalty" in str(event).lower():
                if event["is_team"]:
                    set_pieces_stats["penalties"]["taken"] += 1
                    set_pieces_stats["penalties"]["scored"] += 1
    
    if set_pieces_stats["matches"] > 0:
        matches_count = set_pieces_stats["matches"]
        set_pieces_stats["corners"]["avg_won"] = set_pieces_stats["corners"]["won"] / matches_count
        set_pieces_stats["corners"]["avg_lost"] = set_pieces_stats["corners"]["lost"] / matches_count
        set_pieces_stats["free_kicks"]["avg_won"] = set_pieces_stats["free_kicks"]["won"] / matches_count
        set_pieces_stats["free_kicks"]["avg_lost"] = set_pieces_stats["free_kicks"]["lost"] / matches_count
    
    return set_pieces_stats

# ===========================================
# FUNCIONES DE VISUALIZACIÓN
# ===========================================
def create_formation_chart(formation_stats: Dict):
    """Crea gráfico de formaciones."""
    if not formation_stats:
        return None
    
    formations = list(formation_stats.keys())
    win_rates = [formation_stats[f].get("win_rate", 0) for f in formations]
    counts = [formation_stats[f].get("count", 0) for f in formations]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=formations,
        y=win_rates,
        marker_color=CIBAO_COLOR,
        text=[f"{wr:.1f}%" for wr in win_rates],
        textposition='outside',
        name="Tasa de Victoria",
        hovertemplate="<b>%{x}</b><br>Tasa de Victoria: %{y:.1f}%<br>Partidos: %{customdata}<extra></extra>",
        customdata=counts
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Formación",
        yaxis_title="Tasa de Victoria (%)",
        showlegend=False,
        font=dict(color='white')
    )
    
    return fig

def create_phase_chart(phase_stats: Dict):
    """Crea gráfico de fases del partido."""
    phases = ["0-15'", "16-30'", "31-45'", "46-60'", "61-75'", "76-90'", "90+'"]
    phase_keys = ["first_15", "16_30", "31_45", "46_60", "61_75", "76_90", "90_plus"]
    
    goals_for = [phase_stats[key].get("avg_goals_for", 0) for key in phase_keys]
    goals_against = [phase_stats[key].get("avg_goals_against", 0) for key in phase_keys]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=phases,
        y=goals_for,
        name="Goles a Favor",
        marker_color=CIBAO_COLOR,
        text=[f"{g:.2f}" for g in goals_for],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=phases,
        y=goals_against,
        name="Goles en Contra",
        marker_color="#FFFFFF",
        text=[f"{g:.2f}" for g in goals_against],
        textposition='outside'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Fase del Partido",
        yaxis_title="Promedio de Goles",
        barmode='group',
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_goal_timing_chart(patterns: Dict):
    """Crea gráfico de distribución temporal de goles."""
    goal_times = patterns.get("goal_times", [])
    if not goal_times:
        return None
    
    team_goals = [g["time"] for g in goal_times if g["is_team"]]
    opp_goals = [g["time"] for g in goal_times if not g["is_team"]]
    
    fig = go.Figure()
    
    if team_goals:
        fig.add_trace(go.Histogram(
            x=team_goals,
            name="Goles a Favor",
            marker_color=CIBAO_COLOR,
            nbinsx=18,
            opacity=0.7
        ))
    
    if opp_goals:
        fig.add_trace(go.Histogram(
            x=opp_goals,
            name="Goles en Contra",
            marker_color="#FFFFFF",
            nbinsx=18,
            opacity=0.7
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Minuto del Partido",
        yaxis_title="Cantidad de Goles",
        barmode='overlay',
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# ===========================================
# INTERFAZ PRINCIPAL
# ===========================================
def main():
    titulo_naranja("⚽ Análisis Táctico y Fases del Partido")
    
    # Cargar datos
    all_matches = load_all_matches()
    cibao_matches = get_cibao_matches(all_matches)
    
    if not cibao_matches:
        st.warning("No se encontraron partidos de Cibao.")
        return
    
    # Filtros
    st.sidebar.markdown("### 🔍 Filtros")
    
    filter_type = st.sidebar.radio(
        "Filtrar partidos:",
        ["Todos los partidos", "Últimos 3 partidos", "Últimos 5 partidos", "En Casa", "Fuera"],
        key="tactical_filter"
    )
    
    # Aplicar filtros
    filtered_matches = cibao_matches.copy()
    
    if filter_type == "Últimos 3 partidos":
        filtered_matches = sorted(filtered_matches, key=lambda x: x.get("date") or datetime.min, reverse=True)[:3]
    elif filter_type == "Últimos 5 partidos":
        filtered_matches = sorted(filtered_matches, key=lambda x: x.get("date") or datetime.min, reverse=True)[:5]
    elif filter_type == "En Casa":
        filtered_matches = [m for m in filtered_matches if m.get("is_home", False)]
    elif filter_type == "Fuera":
        filtered_matches = [m for m in filtered_matches if not m.get("is_home", False)]
    
    # Solo partidos jugados
    played_matches = [m for m in filtered_matches if m.get("status", "").lower() in ["played", "finished", "ft", "jugado", "finalizado"]]
    
    if not played_matches:
        st.info("No hay partidos jugados con los filtros seleccionados.")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📐 Formaciones",
        "⏱️ Fases del Partido",
        "📊 Patrones de Eventos",
        "⚡ Momentum",
        "🎯 Set Pieces"
    ])
    
    # TAB 1: FORMACIONES
    with tab1:
        st.markdown("### 📐 Análisis de Formaciones")
        
        formation_stats = analyze_formations(played_matches, CIBAO_TEAM_NAME)
        
        if not formation_stats:
            st.info("No hay datos de formaciones disponibles.")
        else:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            total_matches = sum([s["count"] for s in formation_stats.values()])
            most_used = max(formation_stats.items(), key=lambda x: x[1]["count"])
            best_formation = max([(f, s) for f, s in formation_stats.items() if s["count"] >= 2], 
                               key=lambda x: x[1].get("win_rate", 0), default=(None, None))
            
            with col1:
                st.metric("Total de Formaciones", len(formation_stats))
            with col2:
                st.metric("Partidos Analizados", total_matches)
            with col3:
                st.metric("Formación Más Usada", most_used[0] if most_used else "N/A")
            with col4:
                if best_formation[0]:
                    st.metric("Mejor Formación", f"{best_formation[0]} ({best_formation[1].get('win_rate', 0):.1f}%)")
                else:
                    st.metric("Mejor Formación", "N/A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico
            fig = create_formation_chart(formation_stats)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada
            st.markdown("### 📋 Detalle por Formación")
            formation_data = []
            for formation, stats in sorted(formation_stats.items(), key=lambda x: x[1]["count"], reverse=True):
                formation_data.append({
                    "Formación": formation,
                    "Partidos": stats["count"],
                    "Victorias": stats["wins"],
                    "Empates": stats["draws"],
                    "Derrotas": stats["losses"],
                    "Tasa Victoria": f"{stats.get('win_rate', 0):.1f}%",
                    "Goles a Favor": f"{stats.get('avg_goals_for', 0):.2f}",
                    "Goles en Contra": f"{stats.get('avg_goals_against', 0):.2f}",
                    "Diferencia": f"{stats.get('avg_goal_difference', 0):.2f}"
                })
            
            df = pd.DataFrame(formation_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # TAB 2: FASES DEL PARTIDO
    with tab2:
        st.markdown("### ⏱️ Análisis por Fases del Partido")
        
        phase_stats = analyze_match_phases(played_matches, CIBAO_TEAM_NAME)
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        total_goals_for = sum([p["goals_for"] for p in phase_stats.values()])
        total_goals_against = sum([p["goals_against"] for p in phase_stats.values()])
        best_phase = max(phase_stats.items(), key=lambda x: x[1]["goals_for"] - x[1]["goals_against"])
        
        with col1:
            st.metric("Goles a Favor (Total)", total_goals_for)
        with col2:
            st.metric("Goles en Contra (Total)", total_goals_against)
        with col3:
            phase_names = {"first_15": "0-15'", "16_30": "16-30'", "31_45": "31-45'", 
                          "46_60": "46-60'", "61_75": "61-75'", "76_90": "76-90'", "90_plus": "90+'"}
            st.metric("Mejor Fase", phase_names.get(best_phase[0], "N/A"))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico
        fig = create_phase_chart(phase_stats)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.markdown("### 📋 Detalle por Fase")
        phase_data = []
        phase_names = {"first_15": "0-15'", "16_30": "16-30'", "31_45": "31-45'", 
                      "46_60": "46-60'", "61_75": "61-75'", "76_90": "76-90'", "90_plus": "90+'"}
        
        for key, name in phase_names.items():
            stats = phase_stats[key]
            phase_data.append({
                "Fase": name,
                "Goles a Favor": stats["goals_for"],
                "Goles en Contra": stats["goals_against"],
                "Diferencia": stats["goals_for"] - stats["goals_against"],
                "Promedio GF": f"{stats.get('avg_goals_for', 0):.2f}",
                "Promedio GC": f"{stats.get('avg_goals_against', 0):.2f}"
            })
        
        df = pd.DataFrame(phase_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # TAB 3: PATRONES DE EVENTOS
    with tab3:
        st.markdown("### 📊 Patrones de Eventos")
        
        patterns = analyze_event_patterns(played_matches, CIBAO_TEAM_NAME)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Goles", len(patterns.get("goal_times", [])))
        with col2:
            st.metric("Total Tarjetas", len(patterns.get("card_times", [])))
        with col3:
            st.metric("Total Sustituciones", len(patterns.get("substitution_times", [])))
        with col4:
            goals_after = patterns.get("goals_after_scoring", {})
            st.metric("Goles Tras Marcar", goals_after.get("for", 0))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico de distribución de goles
        fig = create_goal_timing_chart(patterns)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de goles tras eventos
        st.markdown("### 🎯 Goles Tras Eventos Clave")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tras Marcar:**")
            after_scoring = patterns.get("goals_after_scoring", {})
            st.metric("Goles a Favor", after_scoring.get("for", 0))
            st.metric("Goles en Contra", after_scoring.get("against", 0))
        
        with col2:
            st.markdown("**Tras Recibir Gol:**")
            after_conceding = patterns.get("goals_after_conceding", {})
            st.metric("Goles a Favor", after_conceding.get("for", 0))
            st.metric("Goles en Contra", after_conceding.get("against", 0))
    
    # TAB 4: MOMENTUM
    with tab4:
        st.markdown("### ⚡ Análisis de Momentum")
        
        momentum_data = analyze_momentum(played_matches, CIBAO_TEAM_NAME)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Remontadas", momentum_data.get("comebacks", 0))
        with col2:
            st.metric("Ventajas Perdidas", momentum_data.get("blown_leads", 0))
        with col3:
            st.metric("Remontadas Ganadas", momentum_data.get("comeback_wins", 0))
        with col4:
            st.metric("Remontadas Empatadas", momentum_data.get("comeback_draws", 0))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico de momentum
        categories = ["Remontadas", "Ventajas Perdidas", "Remontadas Ganadas", "Remontadas Empatadas"]
        values = [
            momentum_data.get("comebacks", 0),
            momentum_data.get("blown_leads", 0),
            momentum_data.get("comeback_wins", 0),
            momentum_data.get("comeback_draws", 0)
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=[CIBAO_COLOR, "#EF4444", "#10B981", "#F59E0B"],
            text=values,
            textposition='outside'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            xaxis_title="Tipo de Evento",
            yaxis_title="Cantidad",
            showlegend=False,
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 5: SET PIECES
    with tab5:
        st.markdown("### 🎯 Análisis de Set Pieces")
        
        set_pieces_stats = analyze_set_pieces(played_matches, CIBAO_TEAM_NAME)
        
        if set_pieces_stats["matches"] == 0:
            st.info("No hay datos de set pieces disponibles.")
        else:
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### ⚽ Corners")
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
                st.markdown("#### 🦵 Tiros Libres")
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
                st.markdown("#### ⚖️ Penales")
                penalties_taken = set_pieces_stats["penalties"]["taken"]
                penalties_scored = set_pieces_stats["penalties"]["scored"]
                penalties_missed = set_pieces_stats["penalties"]["missed"]
                
                st.metric("Penales Ejecutados", f"{penalties_taken}", delta="Total")
                if penalties_taken > 0:
                    conversion_rate = (penalties_scored / penalties_taken) * 100
                    st.metric("Conversión", f"{conversion_rate:.1f}%", delta=f"{penalties_scored}/{penalties_taken}")
                else:
                    st.info("Sin datos de penales")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico comparativo
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
                marker_color=[CIBAO_COLOR, "#FFFFFF", CIBAO_COLOR, "#FFFFFF"],
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
                showlegend=False,
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()


