# ======== TEMA OSCURO GLOBAL Y FIXES ========
import plotly.io as pio
pio.templates.default = "plotly_dark"   # <<--- FORZAMOS OSCURO

st.markdown("""
<style>

/* ======================================== */
/*    ELIMINAR MARGEN SUPERIOR STREAMLIT    */
/* ======================================== */
header[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}

/* ======================================== */
/*         FONDO NEGRO GLOBAL REAL          */
/* ======================================== */
html, body, [data-testid="stAppViewContainer"], .main, section, div {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* ======================================== */
/*               SIDEBAR DARK               */
/* ======================================== */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    color: #ffffff !important;
    border-right: 1px solid #222 !important;
}

/* ======================================== */
/*        MULTISELECT NARANJA CUSTOM        */
/* ======================================== */
.css-1n76uvr, .stMultiSelect div, .stMultiSelect textarea {
    background-color: #111 !important;
    color: #fff !important;
    border: 1px solid #ff7b00 !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #ff7b00 !important;
    color: white !important;
    border-radius: 6px !important;
}

/* Botón de borrar tag (la X) */
.stMultiSelect [data-baseweb="tag"] svg {
    color: white !important;
}

/* ======================================== */
/*             TABLAS EN OSCURO             */
/* ======================================== */
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

/* ======================================== */
/*    EVITAR QUE CHROME IMPONGA TEMA CLARO  */
/* ======================================== */
:root {
    color-scheme: dark !important;
}
html {
    forced-color-adjust: none !important;
}

</style>
""", unsafe_allow_html=True)
