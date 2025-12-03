# ===========================================
# app.py — Cibao FC Data Hub
# ===========================================

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import time

# ===========================================
# CONFIGURACIÓN GLOBAL
# ===========================================
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

st.set_page_config(
    page_title="Cibao FC - Data Hub",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------
# Router: navegación rápida entre módulos (Cibao FC Hub)
# -------------------------------------------
def _handle_go_param():
    try:
        qp = st.query_params
        go = qp.get("go", None)
    except Exception:
        qp = st.experimental_get_query_params()
        go = qp.get("go", [None])[0] if isinstance(qp.get("go"), list) else qp.get("go")

    if not go:
        return

    # === Mapeo actualizado según nombres renombrados ===
    mapping = {
        # LIGA
        "colectivo": "pages/1_Rendimiento_Colectivo_-_Liga.py",
        "rival": "pages/2_Analisis_del_Rival_-_Liga.py",
        "individual": "pages/3_Rendimiento_Individual_-_Liga.py",

        # COPA
        "colectivo_copa": "pages/4_Rendimiento_Colectivo_-_Copa.py",
        "rival_copa": "pages/5_Analisis_del_Rival_-_Copa.py",
        "individual_copa": "pages/6_Rendimiento_Individual_-_Copa.py",
    }

    page = mapping.get(str(go).lower())
    if page:
        try:
            st.query_params.clear()
        except Exception:
            st.experimental_set_query_params()
        st.switch_page(page)

# Llamar al router lo antes posible
_handle_go_param()


# ===========================================
# LOGIN PAGE
# ===========================================
def login_page():
    st.markdown("""
        <style>
        [data-testid="stSidebar"], [data-testid="stToolbar"], header[data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            background:
              linear-gradient(rgba(10,10,10,0.65), rgba(10,10,10,0.8)),
              url("https://www.presidencia.gob.do/sites/default/files/inline-images/00449e09-428b-4cf5-9264-c9204705de13.jpeg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        div.block-container > div:first-child:empty {
            background: rgba(20, 20, 25, 0.82);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.45);
            backdrop-filter: blur(12px);
            width: 520px;
            padding: 3rem 3rem;
            margin: auto;
            display: flex !important;
            flex-direction: column;
            justify-content: center;
            align-items: stretch;
            transform: translateY(20vh);
        }
        div.block-container {
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            height: 100vh !important;
            padding-top: 0 !important;
        }
        .login-title {
            font-size: 2.2rem;
            font-weight: 900;
            color: #ff7b00;
            margin-bottom: .4rem;
            text-align: center;
            text-shadow: 0 0 12px rgba(255,123,0,0.5);
        }
        .login-sub {
            text-align: center;
            color: #f0f2f5;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        label { color: #d7dee8 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
        input[type="text"], input[type="password"] {
            background-color: #0f1625 !important;
            color: #e8eef7 !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-size: 0.95rem !important;
        }
        button[kind="primary"] {
            background-color: #1a1f2b !important;
            border-radius: 10px !important;
            color: white !important;
            height: 48px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            transition: all 0.3s ease !important;
        }
        button[kind="primary"]:hover {
            background: linear-gradient(90deg,#ff7b00,#ff9a2c) !important;
            border: none !important;
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(255,123,0,0.4);
        }
        @keyframes fadein {
            from { opacity: 0; transform: translateY(-15px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; animation: fadein 1.8s ease;">
            <img src="https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png" width="140">
        </div>
    """, unsafe_allow_html=True)

    placeholder = st.empty()
    with placeholder.container():
        st.markdown('<div class="login-title">Cibao FC - Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Centro de análisis de rendimiento colectivo e individual basado en datos 📊</div>', unsafe_allow_html=True)

        user = st.text_input("Usuario", placeholder="Introduce tu usuario")
        pwd = st.text_input("Contraseña", placeholder="Introduce tu contraseña", type="password")

        if st.button("Iniciar sesión", use_container_width=True):
            if user == USERNAME and pwd == PASSWORD:
                st.session_state["auth"] = True
                st.session_state["page"] = "hub"
                st.success("Inicio de sesión correcto ✅")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("Credenciales incorrectas ❌")


# ===========================================
# HUB PAGE (CENTRO DE NAVEGACIÓN)
# ===========================================
def main_hub():
    import streamlit.components.v1 as components

    # ======== CSS ========
    st.markdown("""
        <style>
        [data-testid="stSidebar"], [data-testid="stToolbar"], header[data-testid="stHeader"] {
            display: none !important;
        }

        /* Fondo del estadio */
        [data-testid="stAppViewContainer"] {
            background:
              linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.85)),
              url("https://www.presidencia.gob.do/sites/default/files/inline-images/00449e09-428b-4cf5-9264-c9204705de13.jpeg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        /* TITULOS */
        .hub-title {
            font-size: 2.8rem;
            font-weight: 900;
            color: #ff7b00;
            text-align: center;
            margin-top: 6vh;
            margin-bottom: 0.4rem;
            text-shadow: 0 0 10px rgba(255,123,0,0.5);
        }

        .hub-subtitle {
            text-align: center;
            color: #f0f0f0;
            font-size: 1.05rem;
            margin-bottom: 3rem;
        }

        /* TARJETAS DESCRIPTIVAS */
        .module-desc {
            font-size: 0.92rem;
            color: #f0f0f0;
            line-height: 1.4;
            text-align: center;
            margin-top: 0.8rem;
            font-weight: 400;
        }

        /* BOTONES STREAMLIT PERSONALIZADOS */
        div[data-testid="stButton"] > button {
            background-color: rgba(20,20,20,0.85) !important;
            border: 1.5px solid rgba(255,123,0,0.6) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 0.91rem !important;
            border-radius: 14px !important;
            height: 65px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.25) !important;
        }

        div[data-testid="stButton"] > button:hover {
            background-color: rgba(255,123,0,0.15) !important;
            border-color: #ff9b25 !important;
            color: #ff9b25 !important;
            box-shadow: 0 0 20px rgba(255,123,0,0.4) !important;
            transform: translateY(-3px);
        }

        </style>
    """, unsafe_allow_html=True)

    # ======== LOGO + TITULOS ========
    st.markdown("""
        <div style="text-align:center; margin-top:2vh;">
            <img src="https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png" width="120">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='hub-title'>Cibao FC - Data Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='hub-subtitle'>Centro integral de análisis táctico y rendimiento basado en datos ⚽</div>", unsafe_allow_html=True)

    # ======== 2x1 LAYOUT: Liga y Copa ========
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### Liga")
        if st.button("Rendimiento Colectivo (Liga)", use_container_width=True):
            st.switch_page("pages/1_Rendimiento_Colectivo.py")  # Asegúrate que esta página sepa que es "liga"
        if st.button("Análisis del Rival (Liga)", use_container_width=True):
            st.switch_page("pages/2_Análisis_del_Rival.py")  # Asegúrate que esta página sepa que es "liga"

    with col2:
        st.markdown("### Copa")
        if st.button("Rendimiento Colectivo (Copa)", use_container_width=True):
            st.switch_page("pages/1_Rendimiento_Colectivo.py")  # Asegúrate que esta página sepa que es "copa"
        if st.button("Análisis del Rival (Copa)", use_container_width=True):
            st.switch_page("pages/2_Análisis_del_Rival.py")  # Asegúrate que esta página sepa que es "copa"
    
            
# ===========================================
# CONTROL DE AUTENTICACIÓN
# ===========================================
if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["page"] = "login"

if not st.session_state["auth"]:
    login_page()
else:
    if st.session_state.get("page") != "hub":
        st.session_state["page"] = "hub"
    main_hub()
