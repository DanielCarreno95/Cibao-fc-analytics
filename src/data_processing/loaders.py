import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path


# ==============================
# CONFIGURACIÓN DE RUTAS
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ==============================
# FUNCIÓN: OBTENER CACHE KEY BASADO EN MODIFICACIÓN DE ARCHIVOS
# ==============================
def get_data_cache_key() -> int:
    """
    Genera una clave de cache basada en el tiempo de modificación de los archivos JSON.
    Cuando los archivos cambian, la clave cambia, invalidando automáticamente el cache.
    """
    folder = Path(DATA_DIR) / "processed" / "Wyscout"
    if not folder.exists():
        return 0
    
    # Use individual JSON files (no consolidated file)
    consolidated_files = [
        "Liga_Mayor_Clean_Per_90_Consolidated.json",
        "Wyscout_Data_Consolidated.json",
        "export_summary.json"
    ]
    
    # Find the most recent individual JSON file
    max_mtime = 0
    for json_file in folder.glob("*.json"):
        if json_file.name not in consolidated_files:
            max_mtime = max(max_mtime, json_file.stat().st_mtime)
    
    # Convertir a int para usar como cache key
    return int(max_mtime * 1000)  # Multiply by 1000 to preserve precision


# ==============================
# FUNCIONES AUXILIARES
# ==============================
def load_json(path: str) -> pd.DataFrame:
    """Carga un archivo JSON y devuelve un DataFrame normalizado."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "data" in data:
        return pd.json_normalize(data["data"])
    return pd.DataFrame(data)


def load_excel(path: str) -> pd.DataFrame:
    """Carga un archivo Excel."""
    return pd.read_excel(path)


# ==============================
# FUNCIÓN: CARGAR ARCHIVOS PER90
# ==============================
@st.cache_data(ttl=60)  # Short TTL - cache invalidates when files change
def load_per90_data(_cache_key: int = None) -> pd.DataFrame:
    """
    Carga todos los archivos JSON de rendimiento (per90)
    desde data/processed/Wyscout/
    
    Prioriza el archivo consolidado si existe, sino carga archivos individuales.
    
    Args:
        _cache_key: Internal cache key based on file modification time.
                    Changing this invalidates the cache automatically.
    """
    folder = os.path.join(DATA_DIR, "processed", "Wyscout")

    if not os.path.exists(folder):
        raise FileNotFoundError(f"La carpeta no existe: {folder}")

    # Load individual JSON files per team (no consolidated file - removed to prevent stale data issues)
    consolidated_files = [
        "Liga_Mayor_Clean_Per_90_Consolidated.json",
        "Wyscout_Data_Consolidated.json",
        "export_summary.json"  # Also exclude summary file
    ]
    all_data = []
    skipped_old_format = []
    for file in os.listdir(folder):
        # Excluir archivos consolidados ya intentados y archivos temporales
        if file.endswith(".json") and not any(cf in file for cf in consolidated_files):
            path = os.path.join(folder, file)
            try:
                df = load_json(path)
                
                # Skip OLD format files - they cause data inconsistencies
                # Check if file has OLD format columns (e.g., "Passes / accurate")
                has_old_format = any(" / " in str(col) or " /accurate" in str(col) or " /on target" in str(col) 
                                     for col in df.columns)
                
                # Check if file has NEW format columns (e.g., "Passes", "Shots")
                has_new_format = "Passes" in df.columns and "Shots" in df.columns
                
                if has_old_format and not has_new_format:
                    # This is an OLD format file - skip it
                    skipped_old_format.append(file)
                    print(f"⚠️ Skipping OLD format file: {file} (contains ' / ' columns)")
                    continue
                
                df["source_file"] = file
                all_data.append(df)
            except Exception as e:
                print(f"⚠️ Error cargando {file}: {e}")
    
    if skipped_old_format:
        print(f"⚠️ Skipped {len(skipped_old_format)} OLD format JSON files. Please delete them and re-upload Excel files to generate NEW format JSON files.")

    if not all_data:
        raise ValueError("No se encontraron archivos JSON en data/processed/Wyscout/")

    result = pd.concat(all_data, ignore_index=True)
    print(f"✓ Cargados {len(all_data)} archivos individuales ({len(result)} filas, {len(result.columns)} columnas)")
    return result


# ==============================
# FUNCIÓN: CARGAR ARCHIVOS DE EQUIPOS
# ==============================
@st.cache_data
def load_team_excels() -> dict:
    """Carga todos los archivos Excel de equipos desde data/raw/wyscout/teams/"""
    folder = os.path.join(DATA_DIR, "raw", "wyscout", "teams")
    team_files = {}

    if not os.path.exists(folder):
        raise FileNotFoundError(f"La carpeta no existe: {folder}")

    for file in os.listdir(folder):
        if file.endswith(".xlsx"):
            path = os.path.join(folder, file)
            try:
                df = load_excel(path)
                team_name = os.path.splitext(file)[0].replace("Team Stats ", "")
                team_files[team_name] = df
            except Exception as e:
                print(f"⚠️ Error cargando {file}: {e}")

    return team_files


# ==============================
# FUNCIÓN: CARGAR RESÚMENES GLOBALES
# ==============================
@st.cache_data
def load_global_summary() -> dict:
    """Carga archivos JSON o Excel desde data/raw/wyscout/global/"""
    folder = os.path.join(DATA_DIR, "raw", "wyscout", "global")
    summary_files = {}

    if not os.path.exists(folder):
        raise FileNotFoundError(f"La carpeta no existe: {folder}")

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if file.endswith(".json"):
            summary_files[file] = load_json(path)
        elif file.endswith(".xlsx"):
            summary_files[file] = load_excel(path)

    return summary_files
