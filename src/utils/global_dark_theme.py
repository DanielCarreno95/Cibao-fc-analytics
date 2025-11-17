# ===========================================
# CONFIGURACIÓN INICIAL – MODO OSCURO GLOBAL
# ===========================================
import streamlit as st
import plotly.io as pio

# Tema Plotly oscuro por defecto
pio.templates.default = "plotly_dark"

# ----- CSS GLOBAL -----
st.markdown("""
<style>

/* ============================================== */
/*      ELIMINAR MARGEN SUPERIOR Y TOOLBAR        */
/* ============================================== */
header[data-testid="stHeader"] {
    display: none !important;
}
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

/* Evitar que Chrome fuerce tema claro */
:root {
    color-scheme: dark !important;
}
html {
    forced-color-adjust: none !important;
}

/* ============================================== */
/*                  SIDEBAR OSCURO                */
/* ============================================== */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #222 !important;
    color: #fff !important;
}

[data-testid="stSidebar"] * {
    color: #fff !important;
}

/* ============================================== */
/*              MULTISELECT NARANJA               */
/* ============================================== */
.css-1n76uvr, .stMultiSelect div, .stMultiSelect textarea {
    background-color: #111 !important;
    color: #fff !important;
    border: 1px solid #ff7b00 !important;
}

/* Tag naranja */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #ff7b00 !important;
    color: white !important;
    border-radius: 6px !important;
}

/* Icono X del tag */
.stMultiSelect [data-baseweb="tag"] svg {
    color: white !important;
}

/* ============================================== */
/*                TABLAS EN OSCURO                */
/* ============================================== */
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

/* Borde de celdas */
.dataframe td, .dataframe th {
    border-color: #333 !important;
}

/* ============================================== */
/*           SELECTBOX / DROPDOWN OSCURO          */
/* ============================================== */
.stSelectbox div[data-baseweb="select"] {
    background-color: #111 !important;
    border-color: #ff7b00 !important;
    color: white !important;
}

.stSelectbox svg {
    color: #ff7b00 !important;
}

/* ============================================== */
/*     TITULOS PRINCIPALES EN NARANJA CIBAO FC    */
/* ============================================== */
h1, h2, h3 {
    color: #ff8c00 !important;
    text-shadow: 0 0 15px rgba(255,140,0,0.55) !important;
}

/* Pequeños detalles */
hr {
    border-color: #222 !important;
}

</style>
""", unsafe_allow_html=True)



# 👉 OPCIONAL: TÍTULO PRINCIPAL AUTOMÁTICO EN NARANJA
def titulo_naranja(texto):
    st.markdown(f"""
    <h1 style="
        text-align:center;
        font-weight:900;
        color:#ff8c00;
        text-shadow: 0 0 14px rgba(255,140,0,0.65);
    ">{texto}</h1>
    """, unsafe_allow_html=True)
