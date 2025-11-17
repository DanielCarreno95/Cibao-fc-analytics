# ===========================================
#  GLOBAL DARK THEME – CIBAO FC DATA HUB
# ===========================================
import streamlit as st
import plotly.io as pio

def inject_dark_theme():
    """Aplica el modo oscuro global unificado para Chrome, Edge, Firefox y Safari."""

    # ---------- Plotly dark global ----------
    pio.templates.default = "plotly_dark"
    pio.templates["plotly_dark"].layout.paper_bgcolor = "rgba(0,0,0,0)"
    pio.templates["plotly_dark"].layout.plot_bgcolor = "rgba(0,0,0,0)"
    pio.templates["plotly_dark"].layout.font.color = "#ffffff"

    # ---------- CSS Global ----------
    st.markdown("""
    <style>

    /* ============================================== */
    /*   ELIMINAR BORDE SUPERIOR / TOOLBAR STREAMLIT  */
    /* ============================================== */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* ============================================== */
    /*            FONDO NEGRO GLOBAL REAL             */
    /* ============================================== */
    html, body, [data-testid="stAppViewContainer"], .main, section, div {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Evitar tema claro forzado por Chrome */
    :root { color-scheme: dark !important; }
    html   { forced-color-adjust: none !important; }

    /* ============================================== */
    /*                SIDEBAR OSCURO                  */
    /* ============================================== */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* ============================================== */
    /*      SELECTBOX + MULTISELECT — CIBAO ORANGE    */
    /* ============================================== */

    /* Contenedor */
    div[data-baseweb="select"] > div {
        background-color: #111 !important;
        border: 1px solid #ff7b00 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }

    /* Texto */
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Flecha */
    div[data-baseweb="select"] svg {
        fill: #ff7b00 !important;
    }

    /* Tags del MultiSelect */
    [data-baseweb="tag"] {
        background-color: #ff7b00 !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
    }

    [data-baseweb="tag"] svg {
        fill: #000 !important;
    }

    /* ============================================== */
    /*                 TABLAS EN OSCURO               */
    /* ============================================== */

    .dataframe, .stDataFrame, .stTable {
        background-color: #000 !important;
        color: #ffffff !important;
    }

    .dataframe tbody tr td {
        background-color: #111 !important;
        color: #ffffff !important;
    }

    .dataframe thead tr th {
        background-color: #222 !important;
        color: #ff8c00 !important;
    }

    .dataframe td, .dataframe th {
        border-color: #333 !important;
    }

    /* ============================================== */
    /*       TITULOS PRINCIPALES EN NARANJA           */
    /* ============================================== */
    h1, h2, h3 {
        color: #ff8c00 !important;
        text-shadow: 0 0 15px rgba(255,140,0,0.55) !important;
    }

    hr {
        border-color: #222 !important;
    }

    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------
#      FUNCIÓN PARA TÍTULO PRINCIPAL ESTILIZADO
# ---------------------------------------------------
def titulo_naranja(texto: str):
    st.markdown(f"""
    <h1 style="
        text-align:center;
        font-weight:900;
        color:#ff8c00;
        text-shadow: 0 0 14px rgba(255,140,0,0.65);
    ">{texto}</h1>
    """, unsafe_allow_html=True)
