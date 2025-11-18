# ============================================================
# 🔶 BLOQUE 0 — ENCABEZADO GENERAL COPA + FUNCIÓN DE TÍTULO
# ============================================================

# Colores institucionales (asegúrate de que están definidos arriba)
CIBAO_ORANGE = "#FF8C00"
CIBAO_GRAY = "#D3D3D3"

# --- FUNCIÓN: TÍTULO NARANJA ---
def titulo_naranja(texto):
    st.markdown(
        f"""
        <h2 style='text-align:center; color:{CIBAO_ORANGE}; font-weight:900;'>
            Comparativa Copa — Cibao FC
        </h2>

        <p style='text-align:center; color:{CIBAO_GRAY}; font-size:15px;'>
            Análisis del rendimiento del Cibao FC en la Copa Concacaf: 
            ataque, construcción, defensa y comportamiento global por partido.
        </p>

        <h1 style="
            text-align:center;
            font-weight:900;
            color:{CIBAO_ORANGE};
            text-shadow:0 0 14px rgba(255,140,0,0.6);
            margin-top:15px;
        ">
            {texto}
        </h1>
        """,
        unsafe_allow_html=True,
    )
