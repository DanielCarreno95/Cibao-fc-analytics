from pathlib import Path
import pandas as pd
import streamlit as st

# =========================================================
# 📊 LOADER DE DATOS - CIBAO FC
# =========================================================
# Carga los datos de la hoja "Cibao" del archivo Excel principal.
# Devuelve:
#   - df_cibao: métricas del Cibao FC (por partido)
#   - df_rivales: métricas de los rivales emparejados
# =========================================================

@st.cache_data
def load_cibao_team_data(filepath: str = "data/raw/wyscout/Global/Liga_Mayor_Clean_Per_90.xlsx"):
    # --- Construir ruta absoluta desde la raíz del proyecto ---
    path = Path(__file__).parents[2] / filepath

    # --- Verificación de existencia ---
    # 🛠️ NO USAMOS st.error() dentro de una función cacheada → levantamos una excepción
    if not path.exists():
        raise FileNotFoundError(f"❌ No se encontró el archivo en: {path.resolve()}")

    # --- Cargar hoja específica ---
    try:
        df = pd.read_excel(path, sheet_name="Cibao")
    except Exception as e:
        # 🛠️ Igual aquí: no usamos st.error(), sino lanzamos la excepción
        raise RuntimeError(f"⚠️ Error al leer el Excel: {e}")

    # --- Limpieza básica ---
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Team", "Match"])

    # --- Separar filas del Cibao y de los rivales ---
    df_cibao = df[df["Team"].str.lower() == "cibao"].copy()
    df_rivales = df[df["Team"].str.lower() != "cibao"].copy()

    # --- Renombrar columnas de rivales para diferenciarlas ---
    df_rivales = df_rivales.rename(
        columns=lambda x: f"{x}_Rival" if x not in ["Match", "Date"] else x
    )

    # --- Combinar ambos conjuntos por Match y Date ---
    df_cibao = pd.merge(df_cibao, df_rivales, on=["Match", "Date"], how="left")

    # --- Ordenar por fecha ---
    df_cibao = df_cibao.sort_values("Date").reset_index(drop=True)

    # 🛠️ Eliminamos st.toast() (no permitido dentro del cache)
    # Devolvemos data limpia
    return df_cibao, df_rivales
