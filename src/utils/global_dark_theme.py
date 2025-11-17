# ===========================================
# CONFIGURACIÓN GLOBAL – MODO OSCURO CIBAO FC (VERSIÓN FINAL)
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro (base)
pio.templates.default = "plotly_dark"


def inject_dark_theme():
    """
    Tema oscuro global para toda la app – compatible con Chrome/Edge,
    con fixes para todos los widgets (Selectbox, Multiselect, Plotly, tablas, etc.)
    """

    st.markdown(
        """
        <style>

        /* ============================================ */
        /* QUITAR HEADER Y TOOLBAR                       */
        /* ============================================ */
        header[data-testid="stHeader"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}

        /* ============================================ */
        /* FONDO GLOBAL SIN ROMPER GRÁFICAS             */
        /* ============================================ */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: #ffffff !important;
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
        /* TITULOS                                      */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55);
        }

        /* ============================================ */
        /* MULTISELECT – FIX COMPLETO PARA CHROME        */
        /* ============================================ */

        /* Contenedor base del select (Chrome pone blanco aquí) */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Wrapper que Chrome mete automáticamente */
        div[aria-expanded], div[data-baseweb="popover"] {
            background-color: #111 !important;
            color: white !important;
        }

        /* Items del menú */
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

        /* Contenedor del multiselect (Chrome deja blanco) */
        .stMultiSelect > div {
            background-color: #111 !important;
            border: 1px solid #ff7b00 !important;
        }

        /* Tags naranjas */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color: white !important;
            border-radius: 6px !important;
        }

        /* Icono X del tag */
        [data-baseweb="tag"] svg {
            color: white !important;
        }

        /* ============================================ */
        /* SELECTBOX (igual estilo que multiselect)      */
        /* ============================================ */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #111 !important;
            color: white !important;
            border: 1px solid #ff7b00 !important;
        }

        .stSelectbox svg {
            color: #ff7b00 !important;
        }

        /* ============================================ */
        /* TABLAS – MODO OSCURO                         */
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
        /* PLOTLY – Fondo realmente oscuro               */
        /* ============================================ */
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
    """Título principal institucional."""
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
