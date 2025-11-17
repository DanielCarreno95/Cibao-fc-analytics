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
    incluyendo:
    - Selectbox oscuro
    - Multiselect oscuro
    - Botones naranja
    - Fondos de widgets negros
    - Plotly oscuro real
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
        /* FONDO GLOBAL                                   */
        /* ============================================ */
        html, body, [data-testid="stAppViewContainer"], .main {
            background-color: #000 !important;
            color: white !important;
        }

        :root { color-scheme: dark !important; }
        html { forced-color-adjust: none !important; }

        /* ============================================ */
        /* SIDEBAR                                        */
        /* ============================================ */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* ============================================ */
        /* TITULOS                                        */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            text-shadow: 0 0 15px rgba(255,140,0,0.55);
        }

        /* ============================================ */
        /* BOTONES – NARANJA CIBAO FC                     */
        /* ============================================ */
        button[kind="secondary"], button[kind="primary"], .stButton > button {
            background-color: #ff8c00 !important;
            color: black !important;
            border: 1px solid #ff8c00 !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }

        button[kind="secondary"]:hover,
        button[kind="primary"]:hover,
        .stButton > button:hover {
            background-color: #ffa64d !important;
            color: black !important;
            border-color: #ffa64d !important;
        }

        /* ============================================ */
        /* SELECTBOX / MULTISELECT – FIX COMPLETO        */
        /* ============================================ */

        /* Contenedor principal */
        div[data-baseweb="select"] {
            background-color: #111 !important;
            border: 1px solid #ff8c00 !important;
            color: white !important;
        }

        /* Label del dropdown */
        .stSelectbox label, .stMultiSelect label {
            color: #ddd !important;
        }

        /* Items del menú */
        ul[data-baseweb="menu"] {
            background-color: #111 !important;
            border: 1px solid #ff8c00 !important;
        }

        ul[data-baseweb="menu"] li {
            background-color: #111 !important;
            color: white !important;
        }

        ul[data-baseweb="menu"] li:hover {
            background-color: #ff8c00 !important;
            color: black !important;
        }

        /* Tags naranjas */
        [data-baseweb="tag"] {
            background-color: #ff8c00 !important;
            color: black !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
        }

        [data-baseweb="tag"] svg {
            color: black !important;
        }

        /* ============================================ */
        /* INPUTS TEXTO / NUMBER / DATE                  */
        /* ============================================ */
        input, textarea {
            background-color: #111 !important;
            color: white !important;
            border: 1px solid #ff8c00 !important;
        }

        /* ============================================ */
        /* TABLAS                                         */
        /* ============================================ */
        .dataframe, .stDataFrame, .stTable {
            background-color: #000 !important;
            color: white !important;
        }

        .dataframe thead tr th {
            background-color: #222 !important;
            color: #ff8c00 !important;
            font-weight: 700 !important;
        }

        .dataframe tbody tr td {
            background-color: #111 !important;
            color: white !important;
        }

        .dataframe td, .dataframe th {
            border-color: #333 !important;
        }

        /* ============================================ */
        /* PLOTLY – FONDO REAL OSCURO                    */
        /* ============================================ */
        .js-plotly-plot .plotly, 
        .js-plotly-plot .main-svg,
        .js-plotly-plot .plot-container {
            background-color: #111 !important;
        }

        /* También el panel de tools */
        .modebar-container {
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
