import os
import json
import pandas as pd
import streamlit as st


# ==============================
# CONFIGURACIÓN DE RUTAS
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


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

    # PRIORIDAD 1: Buscar archivo consolidado (tiene todos los datos en un solo archivo)
    consolidated_files = [
        "Liga_Mayor_Clean_Per_90_Consolidated.json",
        "Wyscout_Data_Consolidated.json"
    ]
    
    for consolidated_file in consolidated_files:
        consolidated_path = os.path.join(folder, consolidated_file)
        if os.path.exists(consolidated_path):
            try:
                df = load_json(consolidated_path)
                df["source_file"] = consolidated_file
                print(f"✓ Cargado archivo consolidado: {consolidated_file} ({len(df)} filas, {len(df.columns) if not df.empty else 0} columnas)")
                return df
            except Exception as e:
                print(f"⚠️ Error cargando archivo consolidado {consolidated_file}: {e}")
                # Continuar y buscar archivos individuales
    
    # PRIORIDAD 2: Cargar archivos individuales (fallback)
    all_data = []
    for file in os.listdir(folder):
        # Excluir archivos consolidados ya intentados y archivos temporales
        if file.endswith(".json") and not any(cf in file for cf in consolidated_files):
            path = os.path.join(folder, file)
            try:
                df = load_json(path)
                df["source_file"] = file
                all_data.append(df)
            except Exception as e:
                print(f"⚠️ Error cargando {file}: {e}")

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
