# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """Tema oscuro completo, compatible con Chrome/Edge y arreglando todos los contenedores internos de selectbox/multiselect."""

    st.markdown(
        """
        <style>

        /* Quitar header y toolbar */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* Fondo global */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #fff !important;
        }

        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }
        [data-testid="stSidebar"] * { color: white !important; }


        /* ------------------------------- */
        /* 🔥 FIX REAL PARA SELECTBOX Y MULTISELECT */
        /* ------------------------------- */

        /* Contenedor principal del select */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* MENÚ desplegable */
        ul[data-baseweb="menu"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
        }

        ul[data-baseweb="menu"] li {
            background-color: #111 !important;
            color: white !important;
        }
        ul[data-baseweb="menu"] li:hover {
            background-color: #ff8c00 !important;
            color: #000 !important;
        }

        /* FIX DE LAS CAPAS INTERNAS DINÁMICAS DE STREAMLIT (Chrome) */
        div[class*="st-ae"],
        div[class*="st-am"],
        div[class*="st-as"] {
            background-color: #111 !important;
            color: white !important;
            border-color: #ff7b00 !important;
        }

        /* Tags en multiselect */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tag"] svg { color: white !important; }


        /* Selectbox flechas */
        .stSelectbox svg { color: #ff7b00 !important; }


        /* ---------------------- */
        /* Tablas */
        /* ---------------------- */
        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color: white !important;
        }

        .dataframe thead tr th {
            background-color: #222 !important;
            color: #ff8c00 !important;
        }
        .dataframe tbody tr td {
            background-color: #111 !important;
            color: white !important;
        }
        .dataframe td, .dataframe th {
            border-color: #333 !important;
        }

        /* ---------------------- */
        /* Plotly fondo oscuro REAL */
        /* ---------------------- */
        .js-plotly-plot .plotly,
        .js-plotly-plot .main-svg,
        .js-plotly-plot .plot-container {
            background-color: #111 !important;
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
