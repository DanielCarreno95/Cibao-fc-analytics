# ===========================================
# TEMA OSCURO GLOBAL + ESTILO CIBAO FC
# ===========================================

import streamlit as st
import plotly.io as pio


def inject_dark_theme():
    # Tema Plotly
    pio.templates.default = "plotly_dark"

    st.markdown("""
    <style>

    /* ============================
       ELIMINAR HEADER Y TOOLBAR
    ============================ */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }


    /* ============================
       FONDO GENERAL SEGURO
       (solo html y body — NO tocar contenedores)
    ============================ */
    html, body {
        background-color: #000 !important;
        color: #fff !important;
    }

    :root {
        color-scheme: dark !important;
    }


    /* ============================
       SIDEBAR OSCURO
    ============================ */
    [data-testid="stSidebar"] {
        background-color: #111 !important;
        border-right: 1px solid #222 !important;
    }
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }


    /* ============================
       MULTISELECT NARANJA
    ============================ */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #111 !important;
        border: 1px solid #ff7b00 !important;
        color: white !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #ff7b00 !important;
        color: #fff !important;
        border-radius: 6px !important;
    }
    .stMultiSelect [data-baseweb="tag"] svg {
        color: #fff !important;
    }


    /* ============================
       SELECTBOX NARANJA
    ============================ */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #111 !important;
        border-color: #ff7b00 !important;
        color: white !important;
    }
    .stSelectbox svg {
        color: #ff7b00 !important;
    }


    /* ============================
       TABLAS TEMA OSCURO
    ============================ */
    .dataframe, .stDataFrame, .stTable {
        background-color: #000 !important;
        color: #fff !important;
    }
    .dataframe tbody tr td {
        background-color: #111 !important;
        color: #fff !important;
    }
    .dataframe thead tr th {
        background-color: #222 !important;
        color: #ff8c00 !important;
    }
    .dataframe td, .dataframe th {
        border-color: #333 !important;
    }


    /* ============================
       TÍTULOS NARANJA CIBAO
    ============================ */
    h1, h2, h3 {
        color: #ff8c00 !important;
        text-shadow: 0 0 12px rgba(255,140,0,0.55) !important;
        font-weight: 900 !important;
    }

    </style>
    """, unsafe_allow_html=True)



def titulo_naranja(texto: str):
    st.markdown(f"""
    <h1 style="
        text-align:center;
        font-weight:900;
        color:#ff8c00;
        text-shadow: 0 0 14px rgba(255,140,0,0.65);
        margin-top: 8px;
    ">{texto}</h1>
    """, unsafe_allow_html=True)
