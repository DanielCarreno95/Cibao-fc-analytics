# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

def inject_dark_theme():
    st.markdown(
        """
        <style>

        /* -------------------------------------------- */
        /* QUITAR HEADER / TOOLBAR */
        /* -------------------------------------------- */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* -------------------------------------------- */
        /* FONDO GENERAL OSCURO (SIN ROMPER GRÁFICAS)   */
        /* -------------------------------------------- */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #fff !important;
        }

        /* NO aplicar a TODOS los <div> → esto rompía todo */
        /* Evitar tema claro automático */
        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }

        /* -------------------------------------------- */
        /* SIDEBAR */
        /* -------------------------------------------- */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }
        [data-testid="stSidebar"] * {
            color: #fff !important;
        }

        /* -------------------------------------------- */
        /* TITULOS */
        /* -------------------------------------------- */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55) !important;
        }

        /* -------------------------------------------- */
        /* MULTISELECT NARANJA */
        /* -------------------------------------------- */
        .stMultiSelect div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Tags */
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
        }

        /* -------------------------------------------- */
        /* SELECTBOX */
        /* -------------------------------------------- */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }
        .stSelectbox svg {
            color: #ff7b00 !important;
        }

        /* -------------------------------------------- */
        /* TABLAS – MODO OSCURO */
        /* -------------------------------------------- */
        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color: #fff !important;
        }

        .dataframe tbody tr td {
            background-color: #111 !important;
            color: #fff !important;
        }

        .dataframe thead tr th {
            background-color: #222 !important;
            color: #ff8c00 !important;
        }

        .dataframe td, .dataframe th {
            border-color: #333 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

def titulo_naranja(texto):
    st.markdown(
        f"""
        <h1 style="
            text-align:center;
            font-weight:900;
            color:#ff8c00;
            text-shadow:0 0 14px rgba(255,140,0,0.65);
        ">{texto}</h1>
        """,
        unsafe_allow_html=True,
    )
