# ===========================================
# 0_Upload_Wyscout_Data.py — Upload & Process Wyscout Data
# ===========================================
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import unicodedata

from src.utils.global_dark_theme import inject_dark_theme, titulo_naranja

# ===========================================
# CONFIGURACIÓN
# ===========================================
st.set_page_config(
    page_title="Upload Wyscout Data | Cibao FC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_dark_theme()

# ===========================================
# CUSTOM FONT SIZES
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
RAW_WYSCOUT_DIR = REPO_ROOT / "data" / "raw" / "wyscout" / "Global"
PROCESSED_WYSCOUT_DIR = REPO_ROOT / "data" / "processed" / "Wyscout"
RAW_WYSCOUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_WYSCOUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================
# IMPORTAR FUNCIONES DE LIMPIEZA DE HEADERS
# ===========================================
import sys
from pathlib import Path

# Add src directory to path to import fix_wyscout_headers
src_path = Path(__file__).parents[1] / "src" / "data_processing"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from fix_wyscout_headers import fix_team_headers, fix_player_headers
    HEADER_CLEANING_AVAILABLE = True
except ImportError as e:
    HEADER_CLEANING_AVAILABLE = False
    # Don't show warning on page load, only when processing files
    pass

try:
    from convert_to_per90_stats import convert_df_to_per90
    PER90_CONVERSION_AVAILABLE = True
except ImportError as e:
    PER90_CONVERSION_AVAILABLE = False
    # Don't show warning on page load, only when processing files
    pass

# ===========================================
# FUNCIONES DE PROCESAMIENTO
# ===========================================
def normalize_string(s: str) -> str:
    """Normaliza strings para nombres de archivos."""
    if pd.isna(s):
        return ""
    s = str(s)
    # Normalizar unicode
    s = unicodedata.normalize('NFKD', s)
    # Reemplazar espacios y caracteres especiales
    s = s.replace(" ", "_").replace("/", "_").replace("\\", "_")
    s = "".join(c for c in s if c.isalnum() or c in ('_', '-'))
    return s

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia los nombres de columnas del DataFrame."""
    df = df.copy()
    # Limpiar nombres de columnas
    df.columns = [col.strip().replace("\n", " ").replace("  ", " ") for col in df.columns]
    return df

def extract_team_from_match_str(match_str: str, is_home: bool = True) -> str:
    """Extrae el nombre del equipo desde la columna Match."""
    if pd.isna(match_str) or not match_str:
        return ""
    
    import re
    match_str = str(match_str)
    # Formato típico: "Cibao - Universidad O&M 2:1" o "Atlántico - Cibao 0:5"
    # Separar por " - " o " vs "
    parts = match_str.replace(" vs ", " - ").split(" - ")
    if len(parts) >= 2:
        # Remover el resultado (formato como "2:1" o "0:5")
        # El resultado está en la última parte
        team_part = parts[0].strip() if is_home else parts[1].strip()
        # Remover resultado si está al final (formato "Team 2:1")
        team_part = re.sub(r'\s+\d+:\d+$', '', team_part).strip()
        return team_part
    return ""

def process_wyscout_csv(uploaded_file, save_raw: bool = True) -> dict:
    """
    Procesa un archivo CSV de Wyscout y lo convierte al formato esperado.
    
    Returns:
        dict: Información sobre el procesamiento
    """
    results = {
        "success": False,
        "teams_processed": 0,
        "files_created": [],
        "errors": [],
        "warnings": []
    }
    
    try:
        # Leer el archivo CSV
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        if df.empty:
            results["errors"].append("El archivo CSV está vacío.")
            return results
        
        # Guardar archivo raw si se solicita (overwrite existing, don't create timestamped copies)
        if save_raw:
            # Overwrite the main raw file instead of creating timestamped copies
            raw_file_path = RAW_WYSCOUT_DIR / "Wyscout_Data.csv"
            with open(raw_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            results["files_created"].append(f"Raw file: {raw_file_path.name} (overwritten)")
        
        # Limpiar nombres de columnas básicos primero
        df = clean_column_names(df)
        
        # Aplicar fix_wyscout_headers para limpiar headers complejos
        if HEADER_CLEANING_AVAILABLE:
            try:
                # Determinar si es team stats o player stats
                is_team_stats = "Match" in df.columns or "Competition" in df.columns
                
                # Check if we have OLD format columns before applying fix
                has_old_format = any(" / " in str(col) for col in df.columns)
                
                if has_old_format:
                    if is_team_stats:
                        df_before = df.copy()
                        df = fix_team_headers(df)
                        # Verify the fix worked
                        has_new_format = "Passes" in df.columns or "Passes Accurate" in df.columns
                        if has_new_format:
                            results["warnings"].append("✅ Headers limpiados (Team Stats) - OLD → NEW format")
                        else:
                            results["warnings"].append("⚠️ Headers limpiados (Team Stats) pero aún tiene formato OLD")
                    else:
                        df = fix_player_headers(df)
                        results["warnings"].append("✅ Headers limpiados (Player Stats)")
                else:
                    results["warnings"].append("ℹ️ CSV ya tiene formato NEW (no necesita limpieza)")
            except Exception as header_error:
                results["errors"].append(f"❌ Error al limpiar headers: {str(header_error)}")
                # Continue without cleaning headers if there's an error
                import traceback
                results["errors"].append(f"Traceback: {traceback.format_exc()}")
        
        # Asegurar que hay columna Team
        if "Team" not in df.columns and "team" in df.columns:
            df["Team"] = df["team"]
        elif "Team" not in df.columns:
            results["warnings"].append("No se encontró columna 'Team'. Se intentará inferir del archivo.")
        
        # Limpiar y convertir fechas
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        elif "date" in df.columns:
            df["Date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.rename(columns={"date": "Date"})
        
        # Limpiar datos
        df = df.dropna(subset=["Team"])
        
        # Convertir a per 90 si está disponible y hay columna Duration
        if PER90_CONVERSION_AVAILABLE and "Duration" in df.columns:
            try:
                df_before_per90 = df.copy()
                df = convert_df_to_per90(df)
                # Verify conversion worked (check if we have per 90 columns)
                has_per90 = any("Per 90" in str(col) or "per 90" in str(col).lower() for col in df.columns)
                if has_per90:
                    results["warnings"].append("✅ Métricas convertidas a per 90")
                else:
                    results["warnings"].append("⚠️ Conversión a per 90 aplicada pero no se detectaron columnas 'Per 90'")
            except Exception as per90_error:
                results["errors"].append(f"❌ Error al convertir a per 90: {str(per90_error)}")
                # Continue without conversion if there's an error
                import traceback
                results["errors"].append(f"Traceback: {traceback.format_exc()}")
        
        # Agrupar por equipo si hay múltiples filas
        if "Team" in df.columns:
            teams = df["Team"].unique()
            processed_data = {}
            
            for team in teams:
                team_df = df[df["Team"] == team].copy()
                team_name_normalized = normalize_string(str(team))
                processed_data[team] = team_df
                
                # Create individual JSON file per team (after headers cleaned and per90 conversion)
                # This ensures each team has its own JSON file with NEW format data
                json_file_path = PROCESSED_WYSCOUT_DIR / f"{team_name_normalized}_per_90.json"
                df_dict = team_df.to_dict(orient="records")
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(df_dict, f, indent=2, ensure_ascii=False, default=str)
                results["files_created"].append(f"JSON: {json_file_path.name}")
                results["teams_processed"] += 1
        else:
            # Si no hay columna Team, tratar todo como un solo conjunto (overwrite existing)
            json_file_path = PROCESSED_WYSCOUT_DIR / "Wyscout_Data.json"
            df_dict = df.to_dict(orient="records")
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(df_dict, f, indent=2, ensure_ascii=False, default=str)
            results["files_created"].append(f"JSON: {json_file_path.name} (overwritten)")
            results["teams_processed"] = 1
        
        # Crear archivo consolidado (overwrite existing, don't create timestamped copies)
        json_consolidated_path = PROCESSED_WYSCOUT_DIR / "Wyscout_Data_Consolidated.json"
        df_dict = df.to_dict(orient="records")
        with open(json_consolidated_path, "w", encoding="utf-8") as f:
            json.dump(df_dict, f, indent=2, ensure_ascii=False, default=str)
        results["files_created"].append(f"Consolidated: {json_consolidated_path.name} (overwritten)")
        
        results["success"] = True
        
    except Exception as e:
        results["errors"].append(f"Error procesando CSV: {str(e)}")
        st.error(f"Error procesando archivo CSV: {str(e)}")
    
    return results

def process_wyscout_pdf(uploaded_file, save_raw: bool = True) -> dict:
    """
    Procesa un archivo PDF de Wyscout (guarda el archivo pero no extrae datos automáticamente).
    
    Returns:
        dict: Información sobre el procesamiento
    """
    results = {
        "success": False,
        "teams_processed": 0,
        "files_created": [],
        "errors": [],
        "warnings": ["Los archivos PDF requieren procesamiento manual. El archivo ha sido guardado."]
    }
    
    try:
        # Guardar archivo raw (overwrite existing, don't create timestamped copies)
        if save_raw:
            # Overwrite the main raw file instead of creating timestamped copies
            raw_file_path = RAW_WYSCOUT_DIR / "Wyscout_Data.pdf"
            with open(raw_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            results["files_created"].append(f"PDF saved: {raw_file_path.name} (overwritten)")
            results["success"] = True
        else:
            results["errors"].append("No se guardó el archivo PDF.")
        
    except Exception as e:
        results["errors"].append(f"Error guardando PDF: {str(e)}")
        st.error(f"Error guardando archivo PDF: {str(e)}")
    
    return results

def extract_team_name_from_filename(filename: str) -> str:
    """Extract team name from filename like 'Team Stats Delfines Del Este.xlsx'"""
    if not filename:
        return ""
    # Remove extension
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    # Remove "Team Stats" prefix if present
    if name_without_ext.startswith("Team Stats "):
        return name_without_ext.replace("Team Stats ", "").strip()
    return name_without_ext.strip()

def process_wyscout_excel(uploaded_file, save_raw: bool = True) -> dict:
    """
    Procesa un archivo Excel de Wyscout y lo convierte al formato esperado.
    
    Returns:
        dict: Información sobre el procesamiento
    """
    results = {
        "success": False,
        "teams_processed": 0,
        "files_created": [],
        "errors": [],
        "warnings": []
    }
    
    try:
        # Extract team name from filename (for single-team files)
        filename_team_name = extract_team_name_from_filename(uploaded_file.name)
        
        # Leer el archivo Excel
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        if not sheet_names:
            results["errors"].append("El archivo Excel no contiene hojas.")
            return results
        
        # Guardar archivo raw si se solicita (overwrite existing, don't create timestamped copies)
        if save_raw:
            # Overwrite the main raw file instead of creating timestamped copies
            raw_file_path = RAW_WYSCOUT_DIR / "Liga_Mayor_Clean_Per_90.xlsx"
            # Guardar el archivo subido (overwrites existing)
            with open(raw_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            results["files_created"].append(f"Raw file: {raw_file_path.name} (overwritten)")
        
        # Detectar si el archivo tiene formato TeamStats (consolidado)
        has_teamstats_sheet = "TeamStats" in sheet_names
        
        # Procesar cada hoja (equipo)
        processed_data = {}
        consolidated_data = []
        all_teams_found = set()
        
        for sheet_name in sheet_names:
            try:
                # Leer la hoja
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                if df.empty:
                    results["warnings"].append(f"La hoja '{sheet_name}' está vacía.")
                    continue
                
                # Limpiar nombres de columnas básicos primero
                df = clean_column_names(df)
                
                # Aplicar fix_wyscout_headers para limpiar headers complejos
                if HEADER_CLEANING_AVAILABLE:
                    try:
                        # Determinar si es team stats o player stats basado en columnas
                        # Team stats generalmente tienen "Match" o "Competition"
                        is_team_stats = "Match" in df.columns or "Competition" in df.columns
                        
                        # Check if we have OLD format columns before applying fix
                        has_old_format = any(" / " in str(col) for col in df.columns)
                        
                        if has_old_format:
                            if is_team_stats:
                                df_before = df.copy()
                                df = fix_team_headers(df)
                                # Verify the fix worked
                                has_new_format = "Passes" in df.columns or "Passes Accurate" in df.columns
                                if has_new_format:
                                    results["warnings"].append(f"✅ Headers limpiados para hoja '{sheet_name}' (Team Stats) - OLD → NEW format")
                                else:
                                    results["warnings"].append(f"⚠️ Headers limpiados para hoja '{sheet_name}' (Team Stats) pero aún tiene formato OLD")
                            else:
                                df = fix_player_headers(df)
                                results["warnings"].append(f"✅ Headers limpiados para hoja '{sheet_name}' (Player Stats)")
                        else:
                            results["warnings"].append(f"ℹ️ Hoja '{sheet_name}' ya tiene formato NEW (no necesita limpieza)")
                    except Exception as header_error:
                        results["errors"].append(f"❌ Error al limpiar headers en '{sheet_name}': {str(header_error)}")
                        # Continue without cleaning headers if there's an error
                        import traceback
                        results["errors"].append(f"Traceback: {traceback.format_exc()}")
                
                # Manejar formato TeamStats (consolidado)
                if has_teamstats_sheet and sheet_name == "TeamStats":
                    # Si la columna Team contiene "TeamStats" o está vacía, extraer de Match
                    if "Match" in df.columns:
                        if "Team" not in df.columns or (df["Team"].iloc[0] if len(df) > 0 else "") == "TeamStats":
                            # Crear dos filas por partido (una para cada equipo)
                            all_rows = []
                            for idx, row in df.iterrows():
                                match_str = row.get("Match", "")
                                if pd.notna(match_str) and match_str:
                                    # Home team
                                    home_team = extract_team_from_match_str(match_str, is_home=True)
                                    if home_team:
                                        row_copy = row.copy()
                                        row_copy["Team"] = home_team
                                        row_copy["is_home"] = True
                                        all_rows.append(row_copy)
                                        all_teams_found.add(home_team)
                                    
                                    # Away team
                                    away_team = extract_team_from_match_str(match_str, is_home=False)
                                    if away_team:
                                        row_copy = row.copy()
                                        row_copy["Team"] = away_team
                                        row_copy["is_home"] = False
                                        all_rows.append(row_copy)
                                        all_teams_found.add(away_team)
                            
                            if all_rows:
                                df = pd.DataFrame(all_rows)
                            elif "Team" in df.columns:
                                # Si Team column existe pero tiene valores incorrectos, filtrar
                                df = df[df["Team"] != "TeamStats"].copy()
                                if "Team" in df.columns:
                                    all_teams_found.update(df["Team"].unique())
                    else:
                        # Si no hay columna Match, usar Team directamente
                        if "Team" in df.columns:
                            df = df[df["Team"] != "TeamStats"].copy()
                            all_teams_found.update(df["Team"].unique())
                
                # Asegurar que hay columnas esenciales
                if "Team" not in df.columns:
                    # Try to extract team name from filename first (for single-team files)
                    if filename_team_name and filename_team_name != uploaded_file.name:
                        df["Team"] = filename_team_name
                        all_teams_found.add(filename_team_name)
                    else:
                        # Fallback to sheet name
                        df["Team"] = sheet_name
                        all_teams_found.add(sheet_name)
                
                # Handle single-team files where first row might be team name in Date column
                # Check if first row has team name in Date or Match column
                if len(df) > 0 and "Date" in df.columns:
                    first_row_date = str(df.iloc[0]["Date"]) if pd.notna(df.iloc[0]["Date"]) else ""
                    # If first row Date contains a team name (not a date), remove it
                    if first_row_date and not any(char.isdigit() for char in first_row_date[:4]):
                        # Likely a header row with team name, remove it
                        df = df.iloc[1:].copy()
                        results["warnings"].append(f"Removed header row from sheet '{sheet_name}'")
                
                # Also check Match column for header rows
                if len(df) > 0 and "Match" in df.columns:
                    first_row_match = str(df.iloc[0]["Match"]) if pd.notna(df.iloc[0]["Match"]) else ""
                    # If first row Match is the team name (not a match string), remove it
                    if first_row_match and " - " not in first_row_match and first_row_match == filename_team_name:
                        df = df.iloc[1:].copy()
                        results["warnings"].append(f"Removed team name header row from sheet '{sheet_name}'")
                
                # Limpiar y convertir fechas
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                elif "date" in df.columns:
                    df["Date"] = pd.to_datetime(df["date"], errors="coerce")
                    df = df.rename(columns={"date": "Date"})
                
                # Limpiar datos
                df = df.dropna(subset=["Team"])
                
                # Convertir a per 90 si está disponible y hay columna Duration
                if PER90_CONVERSION_AVAILABLE and "Duration" in df.columns:
                    try:
                        df_before_per90 = df.copy()
                        df = convert_df_to_per90(df)
                        # Verify conversion worked (check if we have per 90 columns)
                        has_per90 = any("Per 90" in str(col) or "per 90" in str(col).lower() for col in df.columns)
                        if has_per90:
                            results["warnings"].append(f"✅ Métricas convertidas a per 90 para hoja '{sheet_name}'")
                        else:
                            results["warnings"].append(f"⚠️ Conversión a per 90 aplicada pero no se detectaron columnas 'Per 90'")
                    except Exception as per90_error:
                        results["errors"].append(f"❌ Error al convertir a per 90 en '{sheet_name}': {str(per90_error)}")
                        # Continue without conversion if there's an error
                        import traceback
                        results["errors"].append(f"Traceback: {traceback.format_exc()}")
                
                # Si es formato TeamStats, guardar como una sola hoja consolidada
                if has_teamstats_sheet and sheet_name == "TeamStats":
                    processed_data["TeamStats"] = df
                    consolidated_data.append(df)
                else:
                    # Formato individual por equipo
                    team_name_normalized = normalize_string(sheet_name)
                    processed_data[sheet_name] = df
                    consolidated_data.append(df)
                    
                    # Create individual JSON file per team (after headers cleaned and per90 conversion)
                    # This ensures each team has its own JSON file with NEW format data
                    json_file_path = PROCESSED_WYSCOUT_DIR / f"{team_name_normalized}_per_90.json"
                    df_dict = df.to_dict(orient="records")
                    with open(json_file_path, "w", encoding="utf-8") as f:
                        json.dump(df_dict, f, indent=2, ensure_ascii=False, default=str)
                    results["files_created"].append(f"JSON: {json_file_path.name}")
                    results["teams_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error procesando hoja '{sheet_name}': {str(e)}"
                results["errors"].append(error_msg)
                st.error(error_msg)
                continue
        
        # Si es formato TeamStats, crear archivos JSON individuales por equipo
        # After headers cleaned and per90 conversion, create individual JSON files
        if has_teamstats_sheet and "TeamStats" in processed_data:
            df_teamstats = processed_data["TeamStats"]
            for team in all_teams_found:
                team_df = df_teamstats[df_teamstats["Team"] == team].copy()
                if not team_df.empty:
                    team_name_normalized = normalize_string(team)
                    json_file_path = PROCESSED_WYSCOUT_DIR / f"{team_name_normalized}_per_90.json"
                    df_dict = team_df.to_dict(orient="records")
                    with open(json_file_path, "w", encoding="utf-8") as f:
                        json.dump(df_dict, f, indent=2, ensure_ascii=False, default=str)
                    results["files_created"].append(f"JSON: {json_file_path.name}")
                    results["teams_processed"] += 1
        
        # Crear archivo consolidado
        if consolidated_data:
            df_consolidated = pd.concat(consolidated_data, ignore_index=True)
            json_consolidated_path = PROCESSED_WYSCOUT_DIR / "Liga_Mayor_Clean_Per_90_Consolidated.json"
            df_consolidated_dict = df_consolidated.to_dict(orient="records")
            with open(json_consolidated_path, "w", encoding="utf-8") as f:
                json.dump(df_consolidated_dict, f, indent=2, ensure_ascii=False, default=str)
            results["files_created"].append(f"Consolidated: {json_consolidated_path.name}")
        
        # Guardar archivo Excel procesado (reemplazar el existente)
        excel_output_path = RAW_WYSCOUT_DIR / "Liga_Mayor_Clean_Per_90.xlsx"
        with pd.ExcelWriter(excel_output_path, engine="openpyxl") as writer:
            # Si es formato TeamStats, preservar como una sola hoja consolidada
            if has_teamstats_sheet and "TeamStats" in processed_data:
                df_teamstats = processed_data["TeamStats"]
                df_teamstats.to_excel(writer, sheet_name="TeamStats", index=False)
            else:
                # Formato individual: una hoja por equipo
                for sheet_name, df in processed_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        results["files_created"].append(f"Excel processed: {excel_output_path.name}")
        
        # Crear resumen de exportación
        export_summary = {
            "export_date": datetime.now().isoformat(),
            "input_file": uploaded_file.name,
            "output_directory": str(PROCESSED_WYSCOUT_DIR),
            "teams_processed": results["teams_processed"],
            "total_teams": len(sheet_names),
            "individual_json_files": results["teams_processed"],
            "consolidated_json_file": 1 if consolidated_data else 0,
            "files_created": results["files_created"]
        }
        
        summary_path = PROCESSED_WYSCOUT_DIR / "export_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(export_summary, f, indent=2, ensure_ascii=False)
        
        results["success"] = True
        
    except Exception as e:
        results["errors"].append(f"Error general: {str(e)}")
        st.error(f"Error procesando archivo: {str(e)}")
    
    return results

# ===========================================
# INTERFAZ PRINCIPAL
# ===========================================
def main():
    # Initialize session state for processing results
    if "processing_results" not in st.session_state:
        st.session_state.processing_results = None
    if "show_processing_results" not in st.session_state:
        st.session_state.show_processing_results = False
    
    # Home button
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("🏠", help="Volver al Inicio", use_container_width=True, key="home_btn_upload"):
            st.switch_page("app.py")
    
    # Título
    titulo_naranja("📊 Upload & Process Wyscout Data")
    st.markdown("""
    <p style='text-align:center; color:#D1D5DB; font-size:17px;'>
        Sube archivos Excel exportados desde Wyscout para procesarlos y actualizar los datos de la aplicación.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Instrucciones
    with st.expander("📋 Instrucciones", expanded=True):
        st.markdown("""
        **Cómo usar esta herramienta:**
        
        1. **Exporta desde Wyscout:**
           - Ve a Wyscout y exporta los datos del equipo (Team Stats)
           - Formatos soportados: Excel (`.xlsx`, `.xls`), CSV (`.csv`), o PDF (`.pdf`)
           - Puedes subir archivos sin procesar directamente desde Wyscout
        
        2. **Sube el archivo:**
           - Haz clic en "Browse files" y selecciona tu archivo
           - Puedes subir múltiples archivos a la vez
           - Formatos aceptados: `.xlsx`, `.xls`, `.csv`, `.pdf`
        
        3. **Procesamiento automático (todo se hace por ti):**
           - ✅ **Limpieza de headers**: Convierte columnas "Unnamed" a nombres claros
           - ✅ **Conversión a per 90**: Normaliza todas las estadísticas a 90 minutos
           - ✅ **Extracción por equipo**: Organiza los datos por equipo automáticamente
           - ✅ **Archivos JSON**: Crea archivos individuales y consolidados
           - ✅ **Listo para usar**: Los datos están disponibles inmediatamente
        
        4. **Resultados:**
           - Los datos procesados estarán disponibles en las páginas de análisis
           - No necesitas hacer nada más - todo está automatizado
           - Los archivos se guardan automáticamente en las carpetas correctas
        """)
    
    st.markdown("---")
    
    # Show processing results if available (after rerun)
    if st.session_state.show_processing_results and st.session_state.processing_results:
        all_results = st.session_state.processing_results
        st.success(f"✅ {all_results['successful']} archivo(s) procesado(s) exitosamente!")
        st.info("💡 Los datos están ahora disponibles en las páginas de análisis. El cache ha sido limpiado automáticamente.")
        
        # Show summary
        st.markdown("### 📊 Resumen del Procesamiento")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Archivos Totales", all_results["total_files"])
        with col2:
            st.metric("✅ Exitosos", all_results["successful"], delta=f"{all_results['failed']} fallidos" if all_results["failed"] > 0 else None)
        with col3:
            st.metric("Equipos Procesados", all_results["total_teams_processed"])
        with col4:
            st.metric("Archivos Creados", len(all_results["all_files_created"]))
        
        # Archivos creados
        if all_results["all_files_created"]:
            with st.expander("📁 Ver Archivos Creados", expanded=False):
                for file_name in all_results["all_files_created"]:
                    st.markdown(f"- `{file_name}`")
        
        # Advertencias
        if all_results["all_warnings"]:
            with st.expander("⚠️ Advertencias", expanded=False):
                for warning in all_results["all_warnings"]:
                    st.markdown(f"- {warning}")
        
        # Errores
        if all_results["all_errors"]:
            with st.expander("❌ Errores Encontrados", expanded=all_results["failed"] > 0):
                for error in all_results["all_errors"]:
                    st.markdown(f"- {error}")
        
        # Clear button to reset
        if st.button("🔄 Procesar Otros Archivos", use_container_width=True):
            st.session_state.processing_results = None
            st.session_state.show_processing_results = False
            st.rerun()
        
        st.markdown("---")
    
    # Upload section
    st.subheader("📤 Subir Archivos de Wyscout")
    
    uploaded_files = st.file_uploader(
        "Selecciona uno o más archivos exportados desde Wyscout",
        type=["xlsx", "xls", "csv", "pdf", "json"],
        help="Puedes seleccionar múltiples archivos a la vez. Formatos soportados: Excel (.xlsx, .xls), CSV (.csv), PDF (.pdf) o JSON (.json) ya procesados",
        accept_multiple_files=True
    )
    
    # Handle both single file (backward compatibility) and multiple files
    if uploaded_files:
        # Convert single file to list for consistency
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        if len(uploaded_files) == 1:
            # Single file - use existing UI
            uploaded_file = uploaded_files[0]
            
            # Mostrar información del archivo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre del archivo", uploaded_file.name)
            with col2:
                st.metric("Tamaño", f"{uploaded_file.size / 1024:.2f} KB")
            with col3:
                st.metric("Tipo", uploaded_file.type)
            
            # Opciones de procesamiento
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                save_raw = st.checkbox(
                    "Guardar archivo original",
                    value=False,
                    help="Guarda el archivo original (sobrescribe el existente, no crea copias con timestamp)"
                )
            
            # Botón de procesamiento
            if st.button("🔄 Procesar Archivo", type="primary", use_container_width=True):
                with st.spinner("Procesando archivo..."):
                    # Determinar tipo de archivo y procesar según corresponda
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    
                    if file_extension in ['xlsx', 'xls']:
                        results = process_wyscout_excel(uploaded_file, save_raw=save_raw)
                    elif file_extension == 'csv':
                        results = process_wyscout_csv(uploaded_file, save_raw=save_raw)
                    elif file_extension == 'pdf':
                        results = process_wyscout_pdf(uploaded_file, save_raw=save_raw)
                    elif file_extension == 'json':
                        results = process_wyscout_json(uploaded_file, save_raw=save_raw)
                    else:
                        results = {
                            "success": False,
                            "teams_processed": 0,
                            "files_created": [],
                            "errors": [f"Tipo de archivo no soportado: {file_extension}"],
                            "warnings": []
                        }
                
                # Mostrar resultados
                # Store results in session state
                all_results = {
                    "total_files": 1,
                    "successful": 1 if results["success"] else 0,
                    "failed": 0 if results["success"] else 1,
                    "total_teams_processed": results["teams_processed"],
                    "all_files_created": results["files_created"],
                    "all_errors": results["errors"],
                    "all_warnings": results["warnings"]
                }
                st.session_state.processing_results = all_results
                st.session_state.show_processing_results = True
                
                if results["success"]:
                    # Limpiar cache automáticamente
                    st.cache_data.clear()
                    # Automatically rerun to refresh the app with new data
                    st.rerun()
                else:
                    st.error("❌ Error procesando el archivo. Revisa los errores arriba.")
        
        else:
            # Multiple files - show batch processing UI
            st.markdown(f"### 📋 Archivos Seleccionados ({len(uploaded_files)})")
            
            # Display files info
            files_info = []
            for uploaded_file in uploaded_files:
                file_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else "unknown"
                files_info.append({
                "Nombre": uploaded_file.name,
                "Tamaño (KB)": f"{uploaded_file.size / 1024:.2f}",
                "Tipo": file_extension.upper()
            })
            
            df_files = pd.DataFrame(files_info)
            st.dataframe(df_files, use_container_width=True, hide_index=True)
            
            # Opciones de procesamiento
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                save_raw = st.checkbox(
                    "Guardar archivos originales",
                    value=False,
                    help="Guarda los archivos originales (sobrescribe los existentes, no crea copias con timestamp)"
                )
            
            # Botón de procesamiento
            if st.button("🔄 Procesar Todos los Archivos", type="primary", use_container_width=True):
                all_results = {
                    "total_files": len(uploaded_files),
                    "successful": 0,
                    "failed": 0,
                    "total_teams_processed": 0,
                    "all_files_created": [],
                    "all_errors": [],
                    "all_warnings": []
                }
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    file_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else "unknown"
                    
                    status_text.text(f"Procesando {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}...")
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    try:
                        # Determinar tipo de archivo y procesar según corresponda
                        if file_extension in ['xlsx', 'xls']:
                            results = process_wyscout_excel(uploaded_file, save_raw=save_raw)
                        elif file_extension == 'csv':
                            results = process_wyscout_csv(uploaded_file, save_raw=save_raw)
                        elif file_extension == 'pdf':
                            results = process_wyscout_pdf(uploaded_file, save_raw=save_raw)
                        elif file_extension == 'json':
                            results = process_wyscout_json(uploaded_file, save_raw=save_raw)
                        else:
                            results = {
                                "success": False,
                                "teams_processed": 0,
                                "files_created": [],
                                "errors": [f"Tipo de archivo no soportado: {file_extension}"],
                                "warnings": []
                            }
                        
                        # Aggregate results
                        if results["success"]:
                            all_results["successful"] += 1
                            all_results["total_teams_processed"] += results["teams_processed"]
                        else:
                            all_results["failed"] += 1
                        
                        all_results["all_files_created"].extend(results["files_created"])
                        all_results["all_errors"].extend([f"[{uploaded_file.name}] {e}" for e in results["errors"]])
                        all_results["all_warnings"].extend([f"[{uploaded_file.name}] {w}" for w in results["warnings"]])
                        
                    except Exception as e:
                        all_results["failed"] += 1
                        all_results["all_errors"].append(f"[{uploaded_file.name}] Error inesperado: {str(e)}")
                
                progress_bar.empty()
                status_text.empty()
                
                # Store results in session state and show after rerun
                st.session_state.processing_results = all_results
                st.session_state.show_processing_results = True
                
                if all_results["successful"] > 0:
                    # Limpiar cache automáticamente
                    st.cache_data.clear()
                    # Automatically rerun to refresh the app with new data
                    st.rerun()
                else:
                    st.error("❌ No se pudo procesar ningún archivo. Revisa los errores arriba.")
    
    else:
        # Mostrar información sobre archivos existentes
        st.info("👆 Sube uno o más archivos (Excel, CSV o PDF) para comenzar el procesamiento.")
        
        # Botón permanente para limpiar cache (siempre disponible)
        st.markdown("---")
        col_clear1, col_clear2, col_clear3 = st.columns([1, 2, 1])
        with col_clear2:
            if st.button("🔄 Limpiar Cache (Siempre Disponible)", use_container_width=True, key="clear_cache_permanent"):
                st.cache_data.clear()
                st.success("✅ **Cache limpiado exitosamente!**")
                st.info("💡 Los datos se recargarán automáticamente cuando visites las páginas de análisis.")
        
        # Botón para eliminar archivos JSON antiguos (con formato OLD)
        st.markdown("---")
        st.markdown("### 🗑️ Limpieza de Archivos Antiguos")
        st.markdown("""
        **⚠️ Importante:** Si has subido nuevos archivos pero los gráficos aún muestran datos antiguos, 
        es posible que el app esté cargando archivos JSON antiguos con formato OLD (columnas como "Passes / accurate").
        
        **Solución:** Elimina los archivos JSON antiguos y vuelve a subir tus archivos Excel para crear nuevos JSON con formato NEW.
        """)
        col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
        with col_del2:
            if st.button("🗑️ Eliminar Archivos JSON Antiguos", use_container_width=True, key="delete_old_json", 
                        help="Elimina todos los archivos JSON en data/processed/Wyscout/ para forzar regeneración"):
                import shutil
                deleted_count = 0
                deleted_files = []
                try:
                    if PROCESSED_WYSCOUT_DIR.exists():
                        for json_file in PROCESSED_WYSCOUT_DIR.glob("*.json"):
                            # Skip export_summary.json (it's just metadata)
                            if json_file.name != "export_summary.json":
                                json_file.unlink()
                                deleted_count += 1
                                deleted_files.append(json_file.name)
                    if deleted_count > 0:
                        st.success(f"✅ **{deleted_count} archivo(s) JSON eliminado(s)!**")
                        with st.expander("Ver archivos eliminados", expanded=False):
                            for filename in deleted_files:
                                st.markdown(f"- `{filename}`")
                        st.info("💡 Ahora sube tus archivos Excel nuevamente para crear nuevos JSON con formato NEW.")
                        st.cache_data.clear()
                    else:
                        st.info("ℹ️ No se encontraron archivos JSON para eliminar (excepto export_summary.json).")
                except Exception as e:
                    st.error(f"❌ Error eliminando archivos: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        st.markdown("---")
        
        # Mostrar archivos existentes
        st.markdown("### 📂 Archivos Existentes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Archivos Raw")
            if RAW_WYSCOUT_DIR.exists():
                raw_files = list(RAW_WYSCOUT_DIR.glob("*.*"))
                # Filtrar solo archivos relevantes
                raw_files = [f for f in raw_files if f.suffix.lower() in ['.xlsx', '.xls', '.csv', '.pdf']]
                if raw_files:
                    for file in sorted(raw_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                        st.markdown(f"- `{file.name}`")
                else:
                    st.markdown("*No hay archivos raw*")
            else:
                st.markdown("*Directorio no existe*")
        
        with col2:
            st.markdown("#### Archivos Procesados (JSON)")
            if PROCESSED_WYSCOUT_DIR.exists():
                json_files = list(PROCESSED_WYSCOUT_DIR.glob("*.json"))
                # Filter out export_summary.json from display (it's just metadata)
                json_files = [f for f in json_files if f.name != "export_summary.json"]
                if json_files:
                    # Sort by modification time (newest first) and show only recent ones
                    sorted_files = sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)
                    for file in sorted_files[:5]:
                        st.markdown(f"- `{file.name}`")
                    if len(sorted_files) > 5:
                        st.markdown(f"*... y {len(sorted_files) - 5} más*")
                else:
                    st.markdown("*No hay archivos JSON*")
            else:
                st.markdown("*Directorio no existe*")

if __name__ == "__main__":
    main()

