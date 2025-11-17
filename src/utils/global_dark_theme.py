# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """Tema oscuro completo y compatible con Chrome/Edge incluyendo selectbox/multiselect."""

    st.markdown(
        """
        <style>

        /* ------------------------------------------------ */
        /*  OCULTAR HEADER STREAMLIT                        */
        /* ------------------------------------------------ */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* ------------------------------------------------ */
        /*  FONDO GLOBAL NEGRO REAL                         */
        /* ------------------------------------------------ */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #fff !important;
        }

        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }


        /* ------------------------------------------------ */
        /*  SIDEBAR                                         */
        /* ------------------------------------------------ */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }
        [data-testid="stSidebar"] * {
            color: #fff !important;
        }


        /* ===================================================== */
        /* 🔥 SELECTBOX + MULTISELECT (FULL FIX PARA CHROME/EDGE) */
        /* ===================================================== */

        /* Contenedor visible */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Input interno */
        div[data-baseweb="input"] {
            background-color: #111 !important;
            color: white !important;
        }

        /* Desplegable */
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
            color: black !important;
        }

        /* TAG chips (multiselect) */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }
        [data-baseweb="tag"] svg {
            color: white !important;
        }

        /* Flecha */
        .stSelectbox svg {
            color: #ff7b00 !important;
        }

        /* CAPAS INTERNAS GENERADAS POR STREAMLIT */
        [class*="st-ae"], [class*="st-af"], [class*="st-ag"],
        [class*="st-ah"], [class*="st-ai"], [class*="st-aj"],
        [class*="st-ak"], [class*="st-al"], [class*="st-am"],
        [class*="st-an"], [class*="st-ao"], [class*="st-ap"],
        [class*="st-aq"], [class*="st-ar"], [class*="st-as"],
        [class*="st-at"], [class*="st-au"], [class*="st-av"],
        [class*="st-aw"], [class*="st-ax"] {
            background-color: #111 !important;
            color: white !important;
        }


        /* ------------------------------------------------ */
        /*  BOTONES                                         */
        /* ------------------------------------------------ */
        button[kind="primary"] {
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

        /* Botón genérico (algunos usan clases dinámicas) */
        button {
            background-color: #ff7b00 !important;
            color: black !important;
            border-radius: 6px !important;
        }


        /* ------------------------------------------------ */
        /*  TABLAS                                          */
        /* ------------------------------------------------ */
        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color: #fff !important;
        }

        .dataframe th {
            background-color: #222 !important;
            color: #ff8c00 !important;
        }

        .dataframe td {
            background-color: #111 !important;
            color: #fff !important;
        }


        /* ------------------------------------------------ */
        /*  PLOTLY - Fondo oscuro real                      */
        /* ------------------------------------------------ */
        .js-plotly-plot .plotly,
        .js-plotly-plot .main-svg,
        .js-plotly-plot .plot-container {
            background-color: #000 !important;
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
