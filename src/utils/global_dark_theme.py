# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC (VERSION FINAL ESTABLE)
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro (base)
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """
    Tema oscuro global – 100% compatible con Chrome, Edge, Firefox y Safari.
    Arregla:
        ✔ multiselect blanco
        ✔ selectbox blanco
        ✔ popovers blancos
        ✔ menú de selección
        ✔ tablas blancas
        ✔ fondo de Plotly que tapa el gráfico en Chrome
    """

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
            color: #ffffff !important;
        }

        /* ============================================ */
        /* TITULOS                                        */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55);
        }

        /* ============================================ */
        /* MULTISELECT & SELECTBOX FIX CHROME/EDGE       */
        /* ============================================ */

        /* Caja principal */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Flechas */
        .stSelectbox svg, .stMultiSelect svg {
            color: #ff7b00 !important;
        }

        /* Menú desplegable */
        ul[data-baseweb="menu"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
        }

        ul[data-baseweb="menu"] li {
            background-color: #111 !important;
            color: white !important;
            border-radius: 4px;
        }

        ul[data-baseweb="menu"] li:hover {
            background-color: #ff8c00 !important;
            color: black !important;
        }

        /* Multiselect container */
        .stMultiSelect > div {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
        }

        /* Tags */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        /* Icono "X" */
        [data-baseweb="tag"] svg {
            color: white !important;
        }

        /* ============================================ */
        /* BOTONES                                       */
        /* ============================================ */

        button[kind="secondary"], button[kind="primary"],
        .stButton button {
            background-color: #ff8c00 !important;
            color: black !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 700 !important;
        }

        .stButton button:hover {
            background-color: #ffa64d !important;
            color: black !important;
        }

        /* ============================================ */
        /* TABLAS                                        */
        /* ============================================ */

        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color: #fff !important;
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
        /* PLOTLY — FIX REAL PARA QUE SE VEA EL GRÁFICO */
        /* ============================================ */

        /* Evitamos que Chrome ponga fondo blanco */
        .js-plotly-plot .plot-container {
            background: transparent !important;
        }

        /* Evitamos que Plotly sea ocultado por un div negro */
        .js-plotly-plot .main-svg {
            background: transparent !important;
        }

        /* Capa interna donde viven ejes/grid */
        .js-plotly-plot .cartesianlayer {
            background-color: #111 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_naranja(texto):
    """Título central institucional Cibao FC."""
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
