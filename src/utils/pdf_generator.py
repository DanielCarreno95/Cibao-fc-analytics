"""
Generador de PDF profesional para Reporte de Rendimiento Colectivo - Cibao FC
Usa fpdf2 para crear PDFs con gráficos Plotly convertidos a imágenes
"""

import io
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px  # ← AÑADE ESTA LÍNEA
import plotly.io as pio
from fpdf import FPDF
import requests  # ← QUITA PIL.Image, no se usa

# ... resto del código igual ...

# Colores Cibao FC
CIBAO_ORANGE = "#FF8C00"
CIBAO_ORANGE_LIGHT = "#FFC966"
CIBAO_BLACK = "#111111"
CIBAO_GRAY = "#D3D3D3"
CIBAO_WHITE = "#E8E8E8"

# URL del logo
LOGO_URL = "https://www.cibaofc.com/wp-content/uploads/2025/02/cropped-LOGO-CFC-5-NARANJA-BLANCO.png"

HEATMAP_COLORSCALE = [
    [0.0, "#2a2a2a"],
    [0.5, "#ff7b00"],
    [1.0, "#ffae42"]
]


def hex_to_rgb(hex_color: str) -> tuple:
    """Convierte color hex a RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def download_logo() -> Optional[bytes]:
    """Descarga el logo de Cibao FC"""
    try:
        response = requests.get(LOGO_URL, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None


def plotly_to_image(fig: go.Figure, width: int = 1200, height: int = 600, scale: float = 2.0) -> Optional[bytes]:
    """Convierte un gráfico Plotly a imagen PNG"""
    try:
        img_bytes = pio.to_image(
            fig,
            format="png",
            width=width,
            height=height,
            scale=scale,
            engine='kaleido'
        )
        return img_bytes
    except Exception as e:
        # Intentar sin especificar engine
        try:
            img_bytes = pio.to_image(
                fig,
                format="png",
                width=width,
                height=height,
                scale=scale
            )
            return img_bytes
        except:
            return None


def save_image_temp(img_bytes: bytes) -> Optional[str]:
    """Guarda imagen en archivo temporal y retorna la ruta"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(img_bytes)
            return tmp.name
    except Exception:
        return None


class CibaoPDF(FPDF):
    """PDF personalizado para Cibao FC con formato landscape"""
    
    def __init__(self):
        # Formato Super Landscape (420mm x 297mm)
        super().__init__(orientation='L', unit='mm', format=(420, 297))
        self.set_auto_page_break(auto=False, margin=10)
        self.orange_rgb = hex_to_rgb(CIBAO_ORANGE)
        self.gray_rgb = hex_to_rgb(CIBAO_GRAY)
        self.black_rgb = hex_to_rgb(CIBAO_BLACK)
    
    def footer(self):
        """Footer personalizado"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(*self.gray_rgb)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    def add_logo(self, logo_bytes: Optional[bytes], x: float = None, y: float = None, width: float = 40):
        """Agrega logo de Cibao FC"""
        if logo_bytes:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    tmp.write(logo_bytes)
                    tmp_path = tmp.name
                
                if x is None:
                    x = (self.w - width) / 2
                if y is None:
                    y = 15
                
                self.image(tmp_path, x=x, y=y, w=width)
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass


# ============================================================
# FUNCIONES PARA CREAR GRÁFICOS (MISMA LÓGICA QUE TU CÓDIGO)
# ============================================================

def create_plot_group_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, nombre_grupo, mapping):
    """Crea figura de barras horizontales - MISMA LÓGICA que plot_group"""
    columnas = [v for v in mapping.values() if v in df_filtrado.columns]
    etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if len(columnas) == 0:
        return None
    
    df_cibao_filtered = df_filtrado.copy()
    cibao_means = df_cibao_filtered[columnas].mean()
    
    comparison_data = []
    
    for col in columnas:
        comparison_data.append({
            "label": etiquetas[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    if mostrar_promedio_liga and not df_liga_mayor.empty:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        for col in columnas:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": etiquetas[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    df_plot = pd.DataFrame(comparison_data)
    
    cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=True)["label"].tolist()
    df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
    df_plot = df_plot.sort_values("label")
    
    color_map = {
        "Cibao FC": CIBAO_ORANGE,
        "Promedio Liga": CIBAO_ORANGE_LIGHT,
    }
    
    fig = px.bar(
        df_plot,
        x="valor",
        y="label",
        color="Equipo",
        orientation="h",
        text_auto=".2f",
        color_discrete_map=color_map,
        barmode="group",
    )
    
    fig.update_layout(
        height=350,
        template="plotly_dark",
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        font=dict(color=CIBAO_GRAY, size=12),
        title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        title_x=0.5,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(size=10)
        ),
    )
    
    return fig


def create_plot_group_vertical_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, nombre_grupo, mapping):
    """Crea figura de barras verticales - MISMA LÓGICA que plot_group_vertical"""
    columnas = [v for v in mapping.values() if v in df_filtrado.columns]
    etiquetas = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if len(columnas) == 0:
        return None
    
    df_cibao_filtered = df_filtrado.copy()
    cibao_means = df_cibao_filtered[columnas].mean()
    
    comparison_data = []
    
    for col in columnas:
        comparison_data.append({
            "label": etiquetas[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    if mostrar_promedio_liga and not df_liga_mayor.empty:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        for col in columnas:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": etiquetas[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    df_plot = pd.DataFrame(comparison_data)
    
    cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=False)["label"].tolist()
    df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
    df_plot = df_plot.sort_values("label")
    
    color_map = {
        "Cibao FC": CIBAO_ORANGE,
        "Promedio Liga": CIBAO_ORANGE_LIGHT,
    }
    
    fig = px.bar(
        df_plot,
        x="label",
        y="valor",
        color="Equipo",
        orientation="v",
        text_auto=".2f",
        color_discrete_map=color_map,
        barmode="group",
    )
    
    fig.update_layout(
        height=400,
        template="plotly_dark",
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="#D3D3D3", size=12),
        title=dict(text=f"<b>{nombre_grupo}</b>", font=dict(size=18, color="#FF8C00")),
        title_x=0.5,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickangle=-35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(size=10)
        ),
    )
    
    return fig


def create_plot_horizontal_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, nombre, mapping):
    """Crea figura horizontal - MISMA LÓGICA que plot_horizontal"""
    cols = [v for v in mapping.values() if v in df_filtrado.columns]
    labels = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if not cols:
        return None
    
    cibao_means = df_filtrado[cols].mean()
    
    comparison_data = []
    
    for col in cols:
        comparison_data.append({
            "label": labels[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    if mostrar_promedio_liga and not df_liga_mayor.empty:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        for col in cols:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": labels[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    df_plot = pd.DataFrame(comparison_data)
    
    cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=True)["label"].tolist()
    df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
    df_plot = df_plot.sort_values("label")
    
    color_map = {
        "Cibao FC": CIBAO_ORANGE,
        "Promedio Liga": CIBAO_ORANGE_LIGHT,
    }
    
    fig = px.bar(
        df_plot,
        x="valor",
        y="label",
        color="Equipo",
        orientation="h",
        text_auto=".2f",
        color_discrete_map=color_map,
        barmode="group",
    )
    
    fig.update_layout(
        height=350,
        template="plotly_dark",
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        margin=dict(l=30, r=20, t=50, b=20),
        font=dict(color=CIBAO_GRAY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(size=10)
        ),
    )
    
    return fig


def create_plot_vertical_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, nombre, mapping):
    """Crea figura vertical - MISMA LÓGICA que plot_vertical"""
    cols = [v for v in mapping.values() if v in df_filtrado.columns]
    labels = {v: k for k, v in mapping.items() if v in df_filtrado.columns}
    
    if not cols:
        return None
    
    cibao_means = df_filtrado[cols].mean()
    
    comparison_data = []
    
    for col in cols:
        comparison_data.append({
            "label": labels[col],
            "Equipo": "Cibao FC",
            "valor": cibao_means[col]
        })
    
    if mostrar_promedio_liga and not df_liga_mayor.empty:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        for col in cols:
            if col in df_liga_sin_cibao.columns:
                liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                comparison_data.append({
                    "label": labels[col],
                    "Equipo": "Promedio Liga",
                    "valor": liga_val if not pd.isna(liga_val) else 0
                })
    
    df_plot = pd.DataFrame(comparison_data)
    
    cibao_order = df_plot[df_plot["Equipo"] == "Cibao FC"].sort_values("valor", ascending=False)["label"].tolist()
    df_plot["label"] = pd.Categorical(df_plot["label"], categories=cibao_order, ordered=True)
    df_plot = df_plot.sort_values("label")
    
    color_map = {
        "Cibao FC": CIBAO_ORANGE,
        "Promedio Liga": CIBAO_ORANGE_LIGHT,
    }
    
    fig = px.bar(
        df_plot,
        x="label",
        y="valor",
        color="Equipo",
        orientation="v",
        text_auto=".2f",
        color_discrete_map=color_map,
        barmode="group",
    )
    
    fig.update_layout(
        height=400,
        template="plotly_dark",
        plot_bgcolor=CIBAO_BLACK,
        paper_bgcolor=CIBAO_BLACK,
        title=dict(text=f"<b>{nombre}</b>", font=dict(size=18, color=CIBAO_ORANGE)),
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(color=CIBAO_GRAY),
        xaxis=dict(tickangle=-35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(size=10)
        ),
    )
    
    return fig


def create_gauge_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, mapping):
    """Crea gauge - MISMA LÓGICA que plot_gauge"""
    col = list(mapping.values())[0]
    label = list(mapping.keys())[0]
    
    if col not in df_filtrado.columns:
        return None
    
    value = df_filtrado[col].mean()
    max_rango = max(40, value * 1.8)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{label}</b>", 'font': {'color': CIBAO_ORANGE, 'size': 18}},
        gauge={
            'axis': {'range': [0, max_rango]},
            'bar': {'color': CIBAO_ORANGE},
            'bgcolor': "#333",
            'borderwidth': 1,
            'bordercolor': "#555",
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=CIBAO_BLACK,
        plot_bgcolor=CIBAO_BLACK,
        height=260,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(color=CIBAO_GRAY)
    )
    
    return fig


def create_longitud_pase_figure(df_filtrado, df_liga_mayor, mostrar_promedio_liga, mapping):
    """Crea gauge longitud pase - MISMA LÓGICA que plot_longitud_pase"""
    col = list(mapping.values())[0]
    label = list(mapping.keys())[0]
    
    if col not in df_filtrado.columns:
        return None
    
    value_cibao = df_filtrado[col].mean()
    
    value_liga = None
    if mostrar_promedio_liga and not df_liga_mayor.empty and col in df_liga_mayor.columns:
        df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        value_liga = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value_cibao,
        title={'text': f"<b>{label}</b><br><span style='font-size:12px; color:#FFC966'>Cibao FC</span>", 
               'font': {'color': '#FF8C00', 'size': 18}},
        number={'font': {'color': '#FF8C00', 'size': 40}},
        gauge={
            'axis': {'range': [0, max(40, value_cibao * 1.5)]},
            'bar': {'color': "#FF8C00", 'thickness': 0.7},
            'bgcolor': "#333",
            'borderwidth': 1,
            'bordercolor': "#555",
            'steps': [
                {'range': [0, max(40, value_cibao * 1.5)], 'color': "#1a1a1a"}
            ],
            'threshold': {
                'line': {'color': "#FFC966", 'width': 3},
                'thickness': 0.8,
                'value': value_liga if value_liga and not pd.isna(value_liga) else 0
            } if value_liga and not pd.isna(value_liga) else None
        },
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="#111",
        font=dict(color="#D3D3D3")
    )
    
    return fig


def create_heatmap_figure(df_filtrado, nombre_grupo, mapping):
    """Crea heatmap - MISMA LÓGICA que plot_heatmap"""
    dfp = df_filtrado.copy()
    
    cols = [v for v in mapping.values() if v in dfp.columns]
    labels = [k for k, v in mapping.items() if v in dfp.columns]
    
    if len(cols) == 0:
        return None
    
    series_real = dfp[cols].mean().fillna(0)
    
    rank = series_real.rank(method="dense") - 1
    rank = rank.astype(int)
    
    z_vals = rank.to_numpy().reshape(1, -1)
    
    fig = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=labels,
            y=[""],
            colorscale=HEATMAP_COLORSCALE,
            showscale=True,
            colorbar=dict(
                thickness=10,
                tickvals=[0, 1, 2],
                ticktext=["Bajo", "Medio", "Alto"],
                bgcolor="#111",
                tickfont=dict(color=CIBAO_GRAY)
            )
        )
    )
    
    annotations = []
    for j, label in enumerate(labels):
        annotations.append(
            dict(
                x=label,
                y="",
                text=f"{series_real.iloc[j]:.2f}",
                font=dict(color="white", size=13),
                showarrow=False
            )
        )
    
    fig.update_layout(
        annotations=annotations,
        height=280,
        template="plotly_dark",
        title=dict(
            text=f"<b>{nombre_grupo}</b>",
            font=dict(size=18, color=CIBAO_ORANGE)
        ),
        title_x=0.5,
        paper_bgcolor="#111",
        plot_bgcolor="#111",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def generate_pdf_report(
    df_cibao: pd.DataFrame,
    df_filtrado: pd.DataFrame,
    df_liga_mayor: pd.DataFrame,
    partidos_seleccionados: List[str],
    mostrar_promedio_liga: bool = True,
    grupos: Dict = None,
    grupos_pases: Dict = None,
    grupos_def: Dict = None,
    grupos_tacticos: Dict = None,
    metrics_blocks: Dict = None,
    opponent_choice: str = None,
    x_metric: str = None,
    y_metric: str = None,
    x_label: str = None,
    y_label: str = None,
    make_team_scatter_func=None,
) -> bytes:
    """
    Genera un PDF completo con todas las páginas del reporte
    """
    
    pdf = CibaoPDF()
    logo_bytes = download_logo()
    temp_files = []
    
    # ============================================================
    # PÁGINA 1: PORTADA
    # ============================================================
    pdf.add_page()
    
    # Fondo negro
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    # Logo
    if logo_bytes:
        pdf.add_logo(logo_bytes, x=(pdf.w - 50) / 2, y=30, width=50)
        logo_y = 85
    else:
        logo_y = 50
    
    # Título principal
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(logo_y)
    pdf.cell(0, 15, 'REPORTE DE RENDIMIENTO COLECTIVO', 0, 1, 'C')
    
    # Subtítulo
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(*hex_to_rgb(CIBAO_WHITE))
    pdf.cell(0, 10, 'Cibao FC - Liga Dominicana', 0, 1, 'C')
    
    # Fecha
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(*pdf.gray_rgb)
    pdf.set_y(pdf.get_y() + 20)
    pdf.cell(0, 8, f'Fecha de generación: {fecha_actual}', 0, 1, 'C')
    
    # ============================================================
    # PÁGINA 2: KPIs Y GRÁFICO COMPARATIVO
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    # Título
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'INDICADORES DEL ÚLTIMO PARTIDO', 0, 1, 'C')
    
    # KPIs del último partido
    if not df_filtrado.empty:
        ultimo_partido = df_filtrado.sort_values("Date", ascending=False).iloc[0]
        
        fecha_str = "-"
        if pd.notna(ultimo_partido.get("Date", None)):
            try:
                fecha_str = pd.to_datetime(ultimo_partido["Date"]).strftime("%d-%m-%Y")
            except Exception:
                fecha_str = str(ultimo_partido.get("Date", ""))
        
        kpi_data = [
            ("Fecha", fecha_str),
            ("Jornada", str(ultimo_partido.get("Jornada", ""))),
            ("Partido", str(ultimo_partido.get("Match", ""))[:30]),
            ("Resultado", str(ultimo_partido.get("Final Result", ""))),
            ("xG", f"{ultimo_partido.get('xg', 0):.2f}" if pd.notna(ultimo_partido.get('xg')) else "-"),
            ("Posesión %", f"{ultimo_partido.get('possession_percent', 0):.1f}%" if pd.notna(ultimo_partido.get('possession_percent')) else "-"),
            ("Tarjetas A", str(int(ultimo_partido.get("yellow_cards", 0))) if pd.notna(ultimo_partido.get("yellow_cards")) else "-"),
            ("Tarjetas R", str(int(ultimo_partido.get("red_cards", 0))) if pd.notna(ultimo_partido.get("red_cards")) else "-"),
        ]
        
        # Dibujar KPIs en grid 3x3
        start_y = 35
        kpi_width = 120
        kpi_height = 18
        spacing = 5
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(*pdf.gray_rgb)
        
        for i, (label, value) in enumerate(kpi_data):
            row = i // 3
            col = i % 3
            x = 20 + col * (kpi_width + spacing)
            y = start_y + row * (kpi_height + spacing)
            
            # Caja con borde naranja
            pdf.set_draw_color(*pdf.orange_rgb)
            pdf.set_line_width(0.5)
            pdf.rect(x, y, kpi_width, kpi_height)
            
            # Valor
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*pdf.orange_rgb)
            pdf.set_xy(x + 2, y + 3)
            pdf.cell(kpi_width - 4, 8, str(value), 0, 0, 'C')
            
            # Label
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(*pdf.gray_rgb)
            pdf.set_xy(x + 2, y + 12)
            pdf.cell(kpi_width - 4, 6, label, 0, 0, 'C')
        
        # Gráfico scatter comparativo
        if make_team_scatter_func and not df_liga_mayor.empty and opponent_choice:
            try:
                filters = {
                    "Competition": lambda s: s.str.contains("Liga", case=False, na=False)
                }
                
                fig_scatter, _, _ = make_team_scatter_func(
                    df_liga_mayor,
                    primary_team="Cibao",
                    opponent=opponent_choice,
                    x_metric=x_metric or "goals",
                    y_metric=y_metric or "conceded_goals",
                    x_label=x_label or "Goles por 90",
                    y_label=y_label or "Goles en contra por 90",
                    title="Comparativa Liga",
                    filters=filters,
                )
                
                img_bytes = plotly_to_image(fig_scatter, width=1000, height=500, scale=2.0)
                if img_bytes:
                    img_path = save_image_temp(img_bytes)
                    if img_path:
                        temp_files.append(img_path)
                        pdf.set_y(120)
                        pdf.image(img_path, x=15, y=120, w=pdf.w - 30, h=150)
            except Exception as e:
                pass
    
    # ============================================================
    # PÁGINA 3: TAB 1 - EFICIENCIA Y ATAQUE
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'Eficiencia y Ataque', 0, 1, 'C')
    
    if grupos:
        y_pos = 30
        graph_height = 80
        graph_width = 120
        
        # 3 gráficos arriba
        grupos_arriba = [
            "Producción ofensiva directa",
            "Eficiencia en el tiro",
            "Patrones de ataque"
        ]
        
        for i, nombre_grupo in enumerate(grupos_arriba[:3]):
            if nombre_grupo in grupos:
                try:
                    fig = create_plot_group_figure(
                        df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                        nombre_grupo, grupos[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = 20 + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos, w=graph_width, h=graph_height)
                except Exception:
                    pass
        
        # 2 gráficos abajo (centrados)
        grupos_abajo = [
            "Balón parado y definición",
            "Juego interior y profundidad"
        ]
        
        y_pos_abajo = y_pos + graph_height + 15
        x_center_start = (pdf.w - (2 * graph_width + 10)) / 2
        
        for i, nombre_grupo in enumerate(grupos_abajo[:2]):
            if nombre_grupo in grupos:
                try:
                    fig = create_plot_group_figure(
                        df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                        nombre_grupo, grupos[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = x_center_start + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos_abajo, w=graph_width, h=graph_height)
                except Exception:
                    pass
    
    # ============================================================
    # PÁGINA 4: TAB 2 - CONSTRUCCIÓN Y PASES
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'Construcción y Pases', 0, 1, 'C')
    
    if grupos_pases:
        y_pos = 30
        graph_height = 80
        graph_width = 120
        
        # 3 gráficos arriba
        grupos_arriba = [
            "Control y estabilidad en la circulación",
            "Seguridad en la progresión",
            "Conexiones de alto valor táctico"
        ]
        
        for i, nombre_grupo in enumerate(grupos_arriba[:3]):
            if nombre_grupo in grupos_pases:
                try:
                    fig = create_plot_group_vertical_figure(
                        df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                        nombre_grupo, grupos_pases[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = 20 + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos, w=graph_width, h=graph_height)
                except Exception:
                    pass
        
        # 2 gráficos abajo
        y_pos_abajo = y_pos + graph_height + 15
        x_center_start = (pdf.w - (2 * graph_width + 10)) / 2
        
        # Reinicios del juego
        if "Reinicios del juego" in grupos_pases:
            try:
                fig = create_plot_group_vertical_figure(
                    df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                    "Reinicios del juego", grupos_pases["Reinicios del juego"]
                )
                if fig:
                    img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                    if img_bytes:
                        img_path = save_image_temp(img_bytes)
                        if img_path:
                            temp_files.append(img_path)
                            pdf.image(img_path, x=x_center_start, y=y_pos_abajo, w=graph_width, h=graph_height)
            except Exception:
                pass
        
        # Gauge longitud de pase
        if "Longitud media de pase" in grupos_pases:
            try:
                fig = create_longitud_pase_figure(
                    df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                    grupos_pases["Longitud media de pase"]
                )
                if fig:
                    img_bytes = plotly_to_image(fig, width=600, height=300, scale=2.0)
                    if img_bytes:
                        img_path = save_image_temp(img_bytes)
                        if img_path:
                            temp_files.append(img_path)
                            pdf.image(img_path, x=x_center_start + graph_width + 10, y=y_pos_abajo, w=graph_width, h=graph_height)
            except Exception:
                pass
    
    # ============================================================
    # PÁGINA 5: TAB 3 - DEFENSA Y EFICIENCIA
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'Defensa y Eficiencia', 0, 1, 'C')
    
    if grupos_def:
        y_pos = 30
        graph_height = 80
        graph_width = 120
        
        # 2 gráficos horizontales arriba
        grupos_horizontales = [
            "Dominio en los duelos (ofensivos y generales)",
            "Solidez defensiva en disputas"
        ]
        
        x_start = (pdf.w - (2 * graph_width + 10)) / 2
        
        for i, nombre_grupo in enumerate(grupos_horizontales[:2]):
            if nombre_grupo in grupos_def:
                try:
                    fig = create_plot_horizontal_figure(
                        df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                        nombre_grupo, grupos_def[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = x_start + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos, w=graph_width, h=graph_height)
                except Exception:
                    pass
        
        # 2 gráficos verticales en medio
        grupos_verticales = [
            "Acciones defensivas por 90'",
            "Volumen y calidad de llegadas rivales"
        ]
        
        y_pos_medio = y_pos + graph_height + 15
        
        for i, nombre_grupo in enumerate(grupos_verticales[:2]):
            if nombre_grupo in grupos_def:
                try:
                    fig = create_plot_vertical_figure(
                        df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                        nombre_grupo, grupos_def[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = x_start + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos_medio, w=graph_width, h=graph_height)
                except Exception:
                    pass
        
        # Gauge distancia media de disparo
        if "Distancia media de disparo" in grupos_def:
            try:
                fig = create_gauge_figure(
                    df_filtrado, df_liga_mayor, mostrar_promedio_liga,
                    grupos_def["Distancia media de disparo"]
                )
                if fig:
                    img_bytes = plotly_to_image(fig, width=600, height=300, scale=2.0)
                    if img_bytes:
                        img_path = save_image_temp(img_bytes)
                        if img_path:
                            temp_files.append(img_path)
                            y_pos_gauge = y_pos_medio + graph_height + 15
                            x_gauge = (pdf.w - graph_width) / 2
                            pdf.image(img_path, x=x_gauge, y=y_pos_gauge, w=graph_width, h=graph_height)
            except Exception:
                pass
    
    # ============================================================
    # PÁGINA 6: TAB 4 - DISTRIBUCIÓN TÁCTICA
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'Distribución Táctica', 0, 1, 'C')
    
    if grupos_tacticos:
        y_pos = 30
        graph_height = 100
        graph_width = 180
        
        heatmaps = [
            "Mapa de Recuperaciones por Altura",
            "Mapa de Presión por Altura"
        ]
        
        x_start = (pdf.w - (2 * graph_width + 10)) / 2
        
        for i, nombre_grupo in enumerate(heatmaps[:2]):
            if nombre_grupo in grupos_tacticos:
                try:
                    fig = create_heatmap_figure(
                        df_filtrado, nombre_grupo, grupos_tacticos[nombre_grupo]
                    )
                    if fig:
                        img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
                        if img_bytes:
                            img_path = save_image_temp(img_bytes)
                            if img_path:
                                temp_files.append(img_path)
                                x_pos = x_start + i * (graph_width + 10)
                                pdf.image(img_path, x=x_pos, y=y_pos, w=graph_width, h=graph_height)
                except Exception:
                    pass
    
    # ============================================================
    # PÁGINA 7: TAB 5 - ANÁLISIS COMPARATIVO (TABLAS)
    # ============================================================
    pdf.add_page()
    pdf.set_fill_color(*pdf.black_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*pdf.orange_rgb)
    pdf.set_y(15)
    pdf.cell(0, 10, 'Análisis Comparativo (Tablas)', 0, 1, 'C')
    
    if metrics_blocks and not df_filtrado.empty:
        df_base = df_filtrado.copy().sort_values("Date", ascending=False)
        df_base = df_base.head(min(len(df_base), 5))
        
        y_start = 30
        row_height = 8
        col_widths = [60] + [35] * 5
        
        df_liga_sin_cibao = None
        if mostrar_promedio_liga and not df_liga_mayor.empty:
            df_liga_sin_cibao = df_liga_mayor[df_liga_mayor["Team"].str.lower() != "cibao"].copy()
        
        for block_name, metrics_dict in metrics_blocks.items():
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(*pdf.orange_rgb)
            pdf.set_y(y_start)
            pdf.cell(0, 8, f'Bloque {block_name}', 0, 1, 'L')
            y_start += 10
            
            columnas_existentes = [c for c in metrics_dict.values() if c in df_base.columns]
            if not columnas_existentes:
                y_start += 20
                continue
            
            columnas_existentes = columnas_existentes[:5]
            
            # Header
            pdf.set_font('Arial', 'B', 9)
            pdf.set_text_color(*pdf.orange_rgb)
            pdf.set_fill_color(*hex_to_rgb("#2a2a2a"))
            x_pos = 15
            
            pdf.set_xy(x_pos, y_start)
            pdf.cell(col_widths[0], row_height, "Match", 1, 0, 'C', True)
            x_pos += col_widths[0]
            
            label_map = {v: k for k, v in metrics_dict.items() if v in columnas_existentes}
            for col in columnas_existentes:
                label = label_map.get(col, col)
                if len(label) > 15:
                    label = label[:12] + "..."
                pdf.set_xy(x_pos, y_start)
                pdf.cell(col_widths[1], row_height, label, 1, 0, 'C', True)
                x_pos += col_widths[1]
            
            y_start += row_height
            
            # Datos
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(*pdf.gray_rgb)
            
            for _, row in df_base.iterrows():
                if y_start > pdf.h - 30:
                    pdf.add_page()
                    pdf.set_fill_color(*pdf.black_rgb)
                    pdf.rect(0, 0, pdf.w, pdf.h, 'F')
                    y_start = 30
                
                x_pos = 15
                match_name = str(row.get("Match", ""))[:25]
                pdf.set_xy(x_pos, y_start)
                pdf.cell(col_widths[0], row_height, match_name, 1, 0, 'L')
                x_pos += col_widths[0]
                
                for col in columnas_existentes:
                    val = row.get(col, np.nan)
                    if pd.notna(val):
                        if isinstance(val, (int, float)):
                            val_str = f"{val:.2f}"
                        else:
                            val_str = str(val)
                    else:
                        val_str = "-"
                    
                    pdf.set_xy(x_pos, y_start)
                    pdf.cell(col_widths[1], row_height, val_str, 1, 0, 'C')
                    x_pos += col_widths[1]
                
                y_start += row_height
            
            # Promedio liga
            if df_liga_sin_cibao is not None:
                y_start += 5
                pdf.set_font('Arial', 'B', 9)
                pdf.set_text_color(*hex_to_rgb(CIBAO_ORANGE_LIGHT))
                pdf.set_xy(15, y_start)
                pdf.cell(col_widths[0], row_height, "Promedio Liga", 1, 0, 'L', True)
                x_pos = 15 + col_widths[0]
                
                pdf.set_font('Arial', '', 8)
                pdf.set_text_color(*hex_to_rgb(CIBAO_ORANGE_LIGHT))
                
                for col in columnas_existentes:
                    if col in df_liga_sin_cibao.columns:
                        liga_val = pd.to_numeric(df_liga_sin_cibao[col], errors="coerce").mean()
                        if pd.notna(liga_val):
                            val_str = f"{liga_val:.2f}"
                        else:
                            val_str = "-"
                    else:
                        val_str = "-"
                    
                    pdf.set_xy(x_pos, y_start)
                    pdf.cell(col_widths[1], row_height, val_str, 1, 0, 'C')
                    x_pos += col_widths[1]
                
                y_start += row_height
            
            y_start += 15
    
    # Limpiar archivos temporales
    for temp_file in temp_files:
        try:
            Path(temp_file).unlink(missing_ok=True)
        except:
            pass
    
    # Retornar PDF como bytes
    return bytes(pdf.output(dest='S').encode('latin-1'))
