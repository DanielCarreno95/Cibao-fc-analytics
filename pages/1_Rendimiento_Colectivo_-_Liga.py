import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro seguro
pio.templates.default = "plotly_dark"


def inject_dark_theme():

    st.markdown(
        """
        <style>

        /* ============================================ */
        /* FONDO GLOBAL — SIN ROMPER CONTENEDORES        */
        /* ============================================ */
        html, body {
            background-color: #000 !important;
            color: #fff !important;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #000 !important;
        }

        [data-testid="stAppViewContainer"] * {
            color: #ddd !important;
        }

        /* ============================================ */
        /* SIDEBAR                                       */
        /* ============================================ */
        [data-testid="stSidebar"] {
            background-color: #111 !important;
            border-right: 1px solid #222 !important;
        }

        [data-testid="stSidebar"] * {
            color: #fff !important;
        }

        /* ============================================ */
        /* TITULOS NARANJA                               */
        /* ============================================ */
        h1, h2, h3 {
            color: #ff8c00 !important;
            font-weight: 900 !important;
        }

        /* ============================================ */
        /* SELECTBOX / MULTISELECT — FIX COMPLETO         */
        /* ============================================ */

        /* Caja principal */
        div[data-baseweb="select"] {
            background-color: #222 !important;
            border: 1px solid #ff7b00 !important;
            color: white !important;
        }

        /* Menú desplegable */
        div[data-baseweb="popover"] {
            background-color: #222 !important;
            border: 1px solid #ff7b00 !important;
            color:#fff !important;
        }

        ul[data-baseweb="menu"] {
            background-color: #222 !important;
        }

        ul[data-baseweb="menu"] li {
            background-color: #222 !important;
            color: #fff !important;
        }

        ul[data-baseweb="menu"] li:hover {
            background-color: #ff8c00 !important;
            color:#000 !important;
        }

        /* Tags de multiselect */
        [data-baseweb="tag"] {
            background-color: #ff7b00 !important;
            color:#fff !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tag"] svg {
            color:white !important;
        }

        /* Flechas */
        .stSelectbox svg, .stMultiSelect svg {
            color: #ff7b00 !important;
        }

        /* ============================================ */
        /* BOTONES                                       */
        /* ============================================ */
        .stButton button {
            background-color: #ff8c00 !important;
            color: black !important;
            border-radius: 8px !important;
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

        .dataframe thead th {
            background-color:#222 !important;
            color:#ff8c00 !important;
        }

        .dataframe tbody td {
            background-color:#111 !important;
        }

        /* ============================================ */
        /* PLOTLY — MODO OSCURO SIN TAPAR EL GRÁFICO     */
        /* ============================================ */
        .js-plotly-plot .plot-container,
        .js-plotly-plot .main-svg {
            background-color: transparent !important;
        }

        .js-plotly-plot .cartesianlayer {
            background-color: transparent !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_naranja(texto):
    st.markdown(
        f"""
        <h1 style="text-align:center;color:#ff8c00;font-weight:900;">
            {texto}
        </h1>
        """,
        unsafe_allow_html=True,
    )
