import streamlit as st
import plotly.io as pio

def inject_dark_theme():
    """
    Inyecta tema global oscuro que funciona en Chrome, Edge y Firefox.
    Aplica también tema oscuro por defecto a todas las gráficas Plotly.
    """

    # ===========================
    #   TEMA OSCURO PARA PLOTLY
    # ===========================
    pio.templates.default = "plotly_dark"
    pio.templates["plotly_dark"].layout.paper_bgcolor = "rgba(0,0,0,0)"
    pio.templates["plotly_dark"].layout.plot_bgcolor = "rgba(0,0,0,0)"
    pio.templates["plotly_dark"].layout.font.color = "#FFFFFF"

    # ===========================
    #   CSS GLOBAL OSCURO
    # ===========================
    st.markdown("""
    <style>

    /* =====================================
       FORZAR TEMA OSCURO EN TODA LA APP
       ===================================== */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #000000 !important;
        color: #f0f0f0 !important;
    }

    :root {
        color-scheme: dark !important;
    }
    html {
        forced-color-adjust: none !important;
    }

    /* =====================================
       SIDEBAR OSCURO
       ===================================== */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        color: white !important;
        border-right: 1px solid #222 !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background-color: #111111 !important;
    }

    /* =====================================
       SELECTBOX Y MULTISELECT (COLOR NARANJA)
       ===================================== */

    /* Caja principal */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        border: 2px solid #ff7b00 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* Texto interno */
    div[data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Flecha del select */
    div[data-baseweb="select"] svg {
        fill: #ff7b00 !important;
    }

    /* Menú desplegable */
    ul[role="listbox"] {
        background-color: #1a1a1a !important;
        border: 1px solid #ff7b00 !important;
    }

    /* Items del menú */
    ul[role="listbox"] li {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Hover del item */
    ul[role="listbox"] li:hover {
        background-color: #ff7b00 !important;
        color: #000 !important;
    }

    /* TAGS DEL MULTISELECT — COLOR NARANJA */
    .css-1gtu0rj, .css-1n7v3ny, .css-12a3c0m {
        background-color: #ff7b00 !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 6px !important;
    }

    /* Icono "X" dentro del tag */
    .css-1gtu0rj svg, .css-1n7v3ny svg, .css-12a3c0m svg {
        fill: #000 !important;
    }

    /* =====================================
       BOTONES SECUNDARIOS (BORRAR FILTROS)
       ===================================== */
    button[kind="secondary"] {
        background-color: #222 !important;
        color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    button[kind="secondary"]:hover {
        background-color: #ff7b00 !important;
        color: black !important;
        border: 1px solid #ff7b00 !important;
    }

    /* =====================================
       LIMPIAR FONDOS BLANCOS RESIDUALES
       ===================================== */
    div, section, article {
        background: transparent !important;
    }

    </style>
    """, unsafe_allow_html=True)
