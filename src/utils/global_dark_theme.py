# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """Tema oscuro completo, compatible con Chrome y Edge."""

    st.markdown(
        """
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

        /* Menú desplegable */
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

        /* Chips naranjas (multiselect) */
        .stMultiSelect [data-baseweb="tag"],
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        .stMultiSelect [data-baseweb="tag"] svg,
        [data-baseweb="tag"] svg {
            color: white !important;
        }

        /* Flechita de los select */
        .stSelectbox svg {
            color: #ff7b00 !important;
        }

        /* ======================================================= */
        /*  BOTONES                                                */
        /* ======================================================= */

        /* Botones primarios (incluye el de borrar filtros) */
        button[kind="primary"],
        button[data-baseweb="button"],
        button {
            background-color: #ff7b00 !important;
            color: black !important;
            border-radius: 6px !important;
            border: 1px solid #ff7b00 !important;
        }

        /* Botón secundario (si lo usas en algún sitio) */
        button[kind="secondary"] {
            background-color: #222 !important;
            color: white !important;
            border-radius: 6px !important;
            border: 1px solid #555 !important;
        }

        /* Home button - standardized size across all pages */
        button[key="home_btn_1"],
        button[key="home_btn_2"],
        button[key="home_btn_3"],
        button[key="home_btn_4"],
        button[key="home_btn_5"],
        button[key="home_btn_6"] {
            font-size: 24px !important;
            height: 50px !important;
            line-height: 50px !important;
            padding: 0 !important;
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
        /*  PLOTLY – FONDO OSCURO PERO GRÁFICA VISIBLE             */
        /* ======================================================= */
        .js-plotly-plot .plotly,
        .js-plotly-plot .plot-container {
            background-color:#000 !important;
        }

        .js-plotly-plot .main-svg {
            background-color:#111 !important;
        }

        /* ======================================================= */
        /*  FIX FINAL PARA QUE LA GRÁFICA SEA VISIBLE              */
        /* ======================================================= */
        
        /* Fondo transparente del contenedor SVG */
        .js-plotly-plot .main-svg {
        background-color: transparent !important;
        }
        
        /* Fondo transparente de la capa principal */
        .js-plotly-plot rect.bg {
        fill: transparent !important;
        }
        
        /* Fondo interno que Plotly dibuja automáticamente */
        .plotly .main-svg[style] {
        background: transparent !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_naranja(texto: str):
    """Título principal institucional en naranja con glow."""
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
