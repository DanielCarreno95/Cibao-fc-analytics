# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """Tema oscuro completo, compatible con Chrome/Edge."""

    st.markdown(
        """
        <style>

        /* ============================================ */
        /* OCULTAR HEADER Y TOOLBAR                     */
        /* ============================================ */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* ============================================ */
        /* FONDO GLOBAL                                 */
        /* ============================================ */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #fff !important;
        }

        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }

        /* ============================================ */
        /* SIDEBAR                                      */
        /* ============================================ */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }

        [data-testid="stSidebar"] * { 
            color: white !important; 
        }

        /* ============================================ */
        /* TITULOS                                       */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55);
        }

        /* ============================================ */
        /* SELECTBOX & MULTISELECT – FIX COMPLETO        */
        /* ============================================ */

        /* Caja del select */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Naranja constante en borde */
        div[data-baseweb="select"] > div {
            border-color: #ff7b00 !important;
        }

        /* Flecha */
        .stSelectbox svg { 
            color: #ff7b00 !important; 
        }

        /* Tags Multiselect */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tag"] svg { color: white !important; }

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
            color: black !important;
        }

        /* ============================================ */
        /* TABLAS – ESTILO OSCURO                       */
        /* ============================================ */
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

        /* ============================================ */
        /* PLOTLY – FIX PARA QUE LAS GRÁFICAS SE VEAN   */
        /* ============================================ */

        /* Evita que Streamlit tape la gráfica */
        [data-testid="stElementContainer"] {
            background-color: transparent !important;
        }

        /* Fondo transparente del canvas */
        .js-plotly-plot .plot-container {
            background-color: transparent !important;
        }

        .js-plotly-plot .main-svg {
            background-color: transparent !important;
        }

        .js-plotly-plot .plotly {
            background-color: transparent !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_naranja(texto):
    """Título institucional centrado."""
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
