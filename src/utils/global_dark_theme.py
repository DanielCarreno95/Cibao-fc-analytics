# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC (VERSIÓN FINAL REAL)
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro
pio.templates.default = "plotly_dark"


def inject_dark_theme():

    st.markdown(
        """
        <style>

        /* ============================================ */
        /* OCULTAR HEADER / TOOLBAR                     */
        /* ============================================ */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* ============================================ */
        /* FONDO GLOBAL                                  */
        /* ============================================ */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #ffffff !important;
        }

        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }

        /* ============================================ */
        /* SIDEBAR                                       */
        /* ============================================ */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* ============================================ */
        /* TEXTOS / TITULOS                              */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55);
        }

        /* ============================================ */
        /* SELECTBOX & MULTISELECT — FIX REAL CHROME     */
        /* ============================================ */

        /* Caja base */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Popover (Chrome lo deja blanco si no se fuerza) */
        div[data-baseweb="popover"],
        div[aria-expanded="true"] {
            background-color: #111 !important;
            color:#fff !important;
            border: 1px solid #ff7b00 !important;
        }

        /* Flechas */
        .stSelectbox svg, .stMultiSelect svg {
            color: #ff7b00 !important;
        }

        /* Menú del selector */
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

        /* Tags de los multiselect */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tag"] svg {
            color: white !important;
        }

        /* ============================================ */
        /* BOTONES                                       */
        /* ============================================ */

        .stButton button {
            background-color: #ff8c00 !important;
            color: black !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 700 !important;
        }

        .stButton button:hover {
            background-color: #ffa64d !important;
        }

        /* ============================================ */
        /* TABLAS                                        */
        /* ============================================ */
        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color:#fff !important;
        }

        .dataframe thead tr th {
            background-color:#222 !important;
            color:#ff8c00 !important;
        }

        .dataframe tbody tr td {
            background-color:#111 !important;
            color:#fff !important;
        }

        .dataframe td, .dataframe th {
            border-color:#333 !important;
        }

        /* ============================================ */
        /* PLOTLY — EL FIX QUE NECESITABAS               */
        /* ============================================ */

        /* NO TAPAR EL GRÁFICO (antes lo tapabas completo) */
        .js-plotly-plot .cartesianlayer {
            background: transparent !important;
        }

        /* Asegurar fondo oscuro detrás del gráfico sin cubrirlo */
        .js-plotly-plot .plot-container {
            background: transparent !important;
        }

        .js-plotly-plot .main-svg {
            background: transparent !important;
        }

        /* ============================================ */

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
