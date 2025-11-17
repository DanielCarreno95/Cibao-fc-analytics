# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Plotly oscuro
pio.templates.default = "plotly_dark"

def inject_dark_theme():
    st.markdown(
        """
        <style>

        /* ========================================= */
        /*  OCULTAR HEADER Y TOOLBAR DE STREAMLIT     */
        /* ========================================= */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* ========================================= */
        /*  FONDO GENERAL NEGRO — SIN ROMPER GRÁFICAS */
        /* ========================================= */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color:#000 !important;
            color:#fff !important;
        }
        :root { color-scheme: dark !important; }
        html { forced-color-adjust:none !important; }

        /* ========================================= */
        /*  SIDEBAR                                   */
        /* ========================================= */
        [data-testid="stSidebar"] {
            background-color:#111 !important;
            border-right:1px solid #222 !important;
        }
        [data-testid="stSidebar"] * { color:#fff !important; }

        /* ========================================= */
        /*  TITULOS                                   */
        /* ========================================= */
        h1,h2,h3 {
            color:#ff8c00 !important;
            text-shadow:0 0 15px rgba(255,140,0,0.5) !important;
        }

        /* ========================================= */
        /*  BOTONES                                   */
        /* ========================================= */
        button[kind="primary"], .stButton>button {
            background-color:#ff8c00 !important;
            color:white !important;
            border:none !important;
            border-radius:6px !important;
        }
        .stButton>button:hover {
            background-color:#ffa64d !important;
            color:black !important;
        }

        /* ========================================= */
        /*  SELECTBOX UNIVERSAL (sidebar + main)      */
        /* ========================================= */
        div[data-baseweb="select"] {
            background-color:#111 !important;
            border:1px solid #ff8c00 !important;
            color:#fff !important;
        }

        /* texto dentro del select */
        div[data-baseweb="select"] * {
            color:#fff !important;
        }

        /* icono flecha selectbox */
        div[data-baseweb="select"] svg {
            color:#ff8c00 !important;
        }

        /* ========================================= */
        /*  MULTISELECT UNIVERSAL (sidebar + main)    */
        /* ========================================= */
        .stMultiSelect div[data-baseweb="select"] {
            background-color:#111 !important;
            border:1px solid #ff8c00 !important;
            color:#fff !important;
        }

        /* tags */
        [data-baseweb="tag"] {
            background-color:#ff8c00 !important;
            color:white !important;
            border-radius:6px !important;
        }
        [data-baseweb="tag"] svg {
            color:white !important;
        }

        /* ========================================= */
        /*  INPUTS / SLIDERS (por si los usas)        */
        /* ========================================= */
        .stSlider > div > div > div {
            background-color:#ff8c00 !important;
        }

        /* ========================================= */
        /*  TABLAS DARK                               */
        /* ========================================= */
        .dataframe, .stDataFrame, .stTable {
            background-color:#000 !important;
            color:#fff !important;
        }
        .dataframe tbody tr td {
            background-color:#111 !important;
            color:#fff !important;
        }
        .dataframe thead tr th {
            background-color:#222 !important;
            color:#ff8c00 !important;
        }
        .dataframe td, .dataframe th {
            border-color:#333 !important;
        }

        /* ========================================= */
        /*  CARDS Y CONTENEDORES (KPIs)               */
        /* ========================================= */
        div.block-container {
            padding-top:20px !important;
        }

        </style>
        """,
        unsafe_allow_html=True
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
        unsafe_allow_html=True
    )
