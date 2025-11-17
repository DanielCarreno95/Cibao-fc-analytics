# ============================================
#  global_dark_theme.py — Tema oscuro global
# ============================================

import streamlit as st

def inject_dark_theme():
    """Inyecta CSS global para forzar modo oscuro en toda la app."""
    st.markdown("""
    <style>

        /* ======== FONDO GENERAL ======== */
        [data-testid="stAppViewContainer"] {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* ======== SIDEBAR ======== */
        [data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #222222 !important;
        }

        /* Títulos del sidebar */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #ff8c00 !important;
        }

        /* Texto del menú lateral (páginas) */
        section[data-testid="stSidebar"] button {
            color: #ffffff !important;
        }

        .st-emotion-cache-6qob1r,
        .st-emotion-cache-1aumxhk,
        .st-emotion-cache-q16mip {
            color: #ffffff !important;
        }

        /* Hover del menú */
        section[data-testid="stSidebar"] button:hover {
            background-color: #ff8c0022 !important;
            color: #ff8c00 !important;
        }

        /* ======== MULTISELECT ======== */

        /* Chips (tags) */
        div[data-baseweb="tag"] {
            background: #222222 !important;
            color: #ff8c00 !important;
            border: 1px solid #ff8c00 !important;
        }

        /* Icono X de cada chip */
        div[data-baseweb="tag"] svg {
            fill: #ff8c00 !important;
        }

        /* Caja del multiselect */
        .stMultiSelect > div {
            background-color: #111111 !important;
            border: 1px solid #444444 !important;
            color: #ffffff !important;
        }

        /* Dropdown */
        .stMultiSelect div[data-baseweb="popover"] {
            background-color: #111111 !important;
            color: #ffffff !important;
        }

        /* Hover de opciones */
        .stMultiSelect li:hover {
            background-color: #333333 !important;
        }

        /* Texto del input del multiselect */
        .stMultiSelect input {
            color: #ffffff !important;
        }

        /* ======== BOTONES ======== */
        .stButton>button {
            background-color: #111111 !important;
            border: 1px solid #ff8c00 !important;
            color: white !important;
            font-weight: 700 !important;
        }

        .stButton>button:hover {
            background-color: #ff8c00 !important;
            color: #000000 !important;
        }

        /* Botones secundarios */
        button[kind="secondary"] {
            background-color: #111111 !important;
            border: 1px solid #ff8c00 !important;
            color: white !important;
        }

        /* Inputs, selects, sliders */
        .stTextInput > div > div,
        .stSelectbox > div,
        .stNumberInput > div,
        .stSlider > div,
        textarea {
            background-color: #111111 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
        }

        /* Placeholder */
        ::placeholder {
            color: #cccccc !important;
        }

    </style>
    """, unsafe_allow_html=True)
