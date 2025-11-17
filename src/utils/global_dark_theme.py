# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"

def inject_dark_theme():
    st.markdown("""
    <style>

    /* ======================================================= */
    /*  OCULTAR HEADER STREAMLIT                               */
    /* ======================================================= */
    header[data-testid="stHeader"] {display:none !important;}
    [data-testid="stToolbar"] {display:none !important;}

    /* ======================================================= */
    /*  FONDO GLOBAL                                           */
    /* ======================================================= */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #000 !important;
        color: #fff !important;
    }

    :root { color-scheme: dark !important; }
    html { forced-color-adjust: none !important; }

    /* ======================================================= */
    /*  SIDEBAR                                                */
    /* ======================================================= */
    [data-testid="stSidebar"] {
        background-color: #111 !important;
        border-right: 1px solid #222 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* ======================================================= */
    /*  SELECTBOX + MULTISELECT                                */
    /* ======================================================= */

    div[data-baseweb="select"] {
        background-color: #111 !important;
        border: 1px solid #ff7b00 !important;
        color: white !important;
    }

    div[data-baseweb="input"] {
        background-color: #111 !important;
        color: white !important;
    }

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

    [data-baseweb="tag"] {
        background-color: #ff7b00 !important;
        color: white !important;
        border-radius: 6px !important;
    }

    [data-baseweb="tag"] svg {
        color: white !important;
    }

    .stSelectbox svg {
        color: #ff7b00 !important;
    }

    [class*="st-"] {
        background-color: transparent !important;
        color: white !important;
    }

    /* ======================================================= */
    /*  BOTONES                                                */
    /* ======================================================= */

    button[kind="primary"], button {
        background-color: #ff7b00 !important;
        color: black !important;
        border-radius: 6px !important;
        border: 1px solid #ff7b00 !important;
    }

    button[kind="secondary"] {
        background-color: #222 !important;
        color: white !important;
        border-radius: 6px !important;
        border: 1px solid #555 !important;
    }

    /* ======================================================= */
    /*  TABLAS                                                 */
    /* ======================================================= */
    .dataframe, .stDataFrame, .stTable {
        background-color:#000 !important;
        color:#fff !important;
    }

    .dataframe th {
        background-color:#222 !important;
        color:#ff8c00 !important;
    }

    .dataframe td {
        background-color:#111 !important;
        color:#fff !important;
    }

    /* ======================================================= */
    /*  PLOTLY                                                 */
    /* ======================================================= */
    .js-plotly-plot .plotly,
    .js-plotly-plot .main-svg,
    .js-plotly-plot .plot-container {
        background-color:#000 !important;
    }

    </style>
    """, unsafe_allow_html=True)

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
