import streamlit as st

def sidebar_menu():
    st.sidebar.markdown("## 🟠 Análisis Liga")

    if st.sidebar.button("Rendimiento Colectivo", use_container_width=True):
        st.switch_page("pages/1_Rendimiento_Colectivo.py")

    if st.sidebar.button("Análisis del Rival", use_container_width=True):
        st.switch_page("pages/2_Analisis_del_Rival.py")

    if st.sidebar.button("Rendimiento Individual", use_container_width=True):
        st.switch_page("pages/3_Rendimiento_Individual.py")

    st.sidebar.markdown("---")

    st.sidebar.markdown("## 🟠 Análisis Copa")

    if st.sidebar.button("Rendimiento Colectivo", use_container_width=True):
        st.switch_page("pages/4_RC_Copa.py")

    if st.sidebar.button("Análisis del Rival", use_container_width=True):
        st.switch_page("pages/5_AR_Copa.py")

    if st.sidebar.button("Rendimiento Individual", use_container_width=True):
        st.switch_page("pages/6_RI_Copa.py")
