"""
Generador de PDF para Página 1 - Rendimiento Colectivo Liga
Basado en el template de PDF TEMPLATE pero adaptado para gráficos Plotly
"""

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from fpdf import FPDF

# Colores Cibao FC
CIBAO_ORANGE = "#FF8C00"
CIBAO_ORANGE_LIGHT = "#FFA64D"
CIBAO_BLACK = "#111111"
CIBAO_GRAY = "#D3D3D3"
CIBAO_WHITE = "#E8E8E8"


def hex_to_rgb(hex_color: str) -> tuple:
    """Convierte color hex a RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def plotly_to_image(fig: go.Figure, width: int = 800, height: int = 400, scale: float = 2.0) -> Optional[bytes]:
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


def clean_text_for_pdf(text: str) -> str:
    """Limpia texto de caracteres Unicode problemáticos para FPDF"""
    if not text:
        return ""
    
    # Reemplazar caracteres Unicode problemáticos por ASCII
    replacements = {
        "—": "-",  # em dash -> hyphen
        "–": "-",  # en dash -> hyphen
        "…": "...",  # ellipsis
        "«": '"',  # left double angle quote
        "»": '"',  # right double angle quote
        "“": '"',  # left double quotation mark
        "”": '"',  # right double quotation mark
        "'": "'",  # left single quotation mark
        "'": "'",  # right single quotation mark
        "€": "EUR",  # euro sign
        "£": "GBP",  # pound sign
        "©": "(c)",  # copyright
        "®": "(R)",  # registered
        "™": "(TM)",  # trademark
        "°": " grados",  # degree sign
        "±": "+/-",  # plus-minus
        "×": "x",  # multiplication
        "÷": "/",  # division
    }
    
    cleaned = text
    for unicode_char, ascii_char in replacements.items():
        cleaned = cleaned.replace(unicode_char, ascii_char)
    
    # FORZAR a ASCII puro - eliminar cualquier carácter fuera de ASCII
    # Esto garantiza que no habrá errores de Unicode con FPDF
    # También reemplazar acentos por versiones sin acento
    accent_replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N", "Ü": "U",
    }
    for accent, no_accent in accent_replacements.items():
        cleaned = cleaned.replace(accent, no_accent)
    
    # Filtrar solo caracteres ASCII (0-127)
    cleaned = ''.join(c if ord(c) < 128 else ' ' for c in cleaned)
    
    # Limpiar espacios múltiples
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


class ReportePDFPage1(FPDF):
    """PDF personalizado para Reporte de Rendimiento Colectivo - Liga"""
    
    def __init__(self):
        # A4 Landscape (horizontal): ancho=297mm, alto=210mm
        # Usar 'A4' con orientation='L' para asegurar formato horizontal
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=25)  # Margen ajustado para header (22mm) y footer (18mm)
        self.orange_rgb = hex_to_rgb(CIBAO_ORANGE)
        self.gray_rgb = hex_to_rgb(CIBAO_GRAY)
        self.black_rgb = hex_to_rgb(CIBAO_BLACK)
        self.es_contenido = False
        self.tab_actual = None  # Para rastrear el tab actual
    
    def header(self):
        """Header personalizado estético y profesional"""
        if self.es_contenido:
            # Fondo del header (barra naranja con gradiente visual)
            self.set_fill_color(*self.orange_rgb)
            self.rect(0, 0, self.w, 22, 'F')
            
            # Línea decorativa superior (más oscura)
            self.set_fill_color(200, 100, 0)  # Naranja más oscuro
            self.rect(0, 0, self.w, 2, 'F')
            
            # Título del header (centrado, blanco, bold)
            self.set_y(6)
            self.set_font('Arial', 'B', 13)
            self.set_text_color(255, 255, 255)  # Blanco
            self.cell(0, 10, clean_text_for_pdf("CIBAO FC - REPORTE DE RENDIMIENTO COLECTIVO"), align='C')
            
            # Fecha en la esquina derecha (estilo elegante)
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            self.set_font('Arial', '', 9)
            self.set_text_color(255, 255, 255)  # Blanco
            self.set_xy(self.w - 55, 6)
            # Fondo sutil para la fecha
            self.set_fill_color(220, 120, 0)
            self.rect(self.w - 55, 6, 50, 8, 'F')
            self.set_xy(self.w - 52, 8)
            self.cell(45, 6, clean_text_for_pdf(fecha_actual), align='R')
            
            # Línea decorativa inferior (más clara)
            self.set_fill_color(255, 180, 80)
            self.rect(0, 20, self.w, 2, 'F')
    
    def footer(self):
        """Footer estético y profesional con número de página y marca"""
        if self.es_contenido:
            # Fondo del footer (barra gris oscura elegante)
            self.set_fill_color(30, 30, 30)  # Gris muy oscuro
            self.rect(0, self.h - 18, self.w, 18, 'F')
            
            # Línea decorativa superior (naranja sutil)
            self.set_fill_color(*self.orange_rgb)
            self.rect(0, self.h - 18, self.w, 2, 'F')
            
            # Línea decorativa inferior (gris más claro)
            self.set_fill_color(60, 60, 60)
            self.rect(0, self.h - 2, self.w, 2, 'F')
            
            # Número de página centrado (estilo elegante)
            self.set_y(-11)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(*self.orange_rgb)  # Naranja para destacar
            # Fondo sutil para el número de página
            self.set_fill_color(50, 50, 50)
            page_text = clean_text_for_pdf(f'Pagina {self.page_no()}')
            text_width = self.get_string_width(page_text) + 8
            self.rect((self.w - text_width) / 2, self.h - 14, text_width, 8, 'F')
            self.set_xy((self.w - text_width) / 2 + 4, -11)
            self.cell(text_width - 8, 6, page_text, align='C')
            
            # Marca en la esquina izquierda (estilo profesional)
            self.set_xy(12, -11)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*self.gray_rgb)
            self.cell(0, 6, clean_text_for_pdf("Cibao FC Data Hub"), align='L')
            
            # Separador decorativo
            self.set_fill_color(*self.orange_rgb)
            self.rect(10, self.h - 12, 1, 4, 'F')
            
            # Copyright/año en la esquina derecha
            año_actual = datetime.now().strftime("%Y")
            self.set_xy(self.w - 50, -11)
            self.set_font('Arial', '', 8)
            self.set_text_color(120, 120, 120)
            self.cell(45, 6, clean_text_for_pdf(f"© {año_actual} Cibao FC"), align='R')
    
    def generar_caratula(self, titulo: str, subtitulo: str):
        """Genera la portada del PDF"""
        self.add_page()
        self.es_contenido = False
        
        # Fondo naranja (como solicitaste)
        self.set_fill_color(*self.orange_rgb)
        self.rect(0, 0, self.w, self.h, 'F')
        
        # Intentar cargar logo si existe
        logo_paths = [
            "assets/assets/logo.png",  # Ruta donde está el logo en GitHub
            "assets/images/logo.png",
            "PDF TEMPLATE/logo.png",
            "logo.png"
        ]
        
        logo_img = None
        for path in logo_paths:
            if os.path.exists(path):
                logo_img = path
                break
        
        # Si hay logo, mostrarlo arriba
        if logo_img:
            try:
                # Logo centrado en la parte superior
                logo_width = 60  # mm
                logo_height = 60  # mm
                x_logo = (self.w - logo_width) / 2
                self.image(logo_img, x=x_logo, y=30, w=logo_width, h=logo_height)
                y_titulo = 100  # Empezar título más abajo si hay logo
            except:
                y_titulo = 75
        else:
            y_titulo = 75
        
        # Título principal (blanco sobre naranja)
        self.set_y(y_titulo)
        self.set_font('Arial', 'B', 32)
        self.set_text_color(255, 255, 255)  # Blanco
        self.multi_cell(0, 18, clean_text_for_pdf(titulo), align='C')
        
        # Subtítulo deportivo (blanco sobre naranja)
        self.ln(12)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)  # Blanco
        self.multi_cell(0, 12, clean_text_for_pdf(subtitulo), align='C')
        
        # Fecha (blanco sobre naranja)
        fecha_actual = datetime.now().strftime("%d de %B de %Y")
        self.set_font('Arial', '', 14)
        self.set_text_color(255, 255, 255)  # Blanco
        self.set_y(self.get_y() + 25)
        self.cell(0, 10, clean_text_for_pdf(f'Fecha de generacion: {fecha_actual}'), 0, 1, 'C')
    
    def generar_cierre(self):
        """Página de cierre"""
        self.es_contenido = False
        self.add_page()
        
        # Fondo negro
        self.set_fill_color(*self.black_rgb)
        self.rect(0, 0, self.w, self.h, 'F')
        
        # Texto de cierre
        self.set_y(self.h / 2)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(*self.orange_rgb)
        self.cell(0, 10, clean_text_for_pdf("FIN DEL REPORTE"), align='C')
        self.ln(10)
        self.set_font('Arial', '', 12)
        self.set_text_color(*self.gray_rgb)
        self.cell(0, 10, clean_text_for_pdf("Generado con Cibao FC Data Hub"), align='C')


def generar_pdf_page1(
    figuras: List[Dict[str, Any]],
    titulo: str = "Reporte de Rendimiento Colectivo",
    subtitulo: str = "Cibao FC - Liga Dominicana",
    kpis_data: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Genera un PDF con los gráficos de la página 1
    
    Args:
        figuras: Lista de diccionarios con:
            - 'fig': objeto go.Figure de Plotly
            - 'titulo': título del gráfico (opcional)
            - 'es_scatter': True si es el scatter inicial (va solo en página completa)
        titulo: Título principal del PDF
        subtitulo: Subtítulo del PDF
    
    Returns:
        bytes del PDF generado
    """
    pdf = ReportePDFPage1()
    temp_files = []
    
    try:
        # Portada
        pdf.generar_caratula(titulo, subtitulo)
        
        # Activar modo contenido
        pdf.es_contenido = True
        
        # Separar scatter inicial del resto
        scatter_inicial = None
        otros_graficos = []
        
        for figura_info in figuras:
            if figura_info.get('es_scatter', False):
                scatter_inicial = figura_info
            else:
                otros_graficos.append(figura_info)
        
        # Página especial para scatter inicial + KPIs (si existe)
        if scatter_inicial:
            pdf.add_page()
            pdf.set_fill_color(*pdf.black_rgb)
            pdf.rect(0, 0, pdf.w, pdf.h, 'F')
            
            fig = scatter_inicial.get('fig')
            titulo_scatter_raw = scatter_inicial.get('titulo', 'Comparativa Liga')
            titulo_scatter = clean_text_for_pdf(titulo_scatter_raw)
            
            if fig is not None:
                # Título (después del header - 22mm)
                pdf.set_font('Arial', 'B', 16)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_y(28)
                pdf.cell(0, 10, titulo_scatter, align='C', ln=True)
                
                # Convertir y mostrar scatter con mejor proporción (más ancho, menos alto)
                img_bytes = plotly_to_image(fig, width=1600, height=700, scale=2.0)
                if img_bytes:
                    img_path = save_image_temp(img_bytes)
                    if img_path:
                        temp_files.append(img_path)
                        # Gráfico más ancho y menos alto (proporción 2.3:1)
                        ancho_scatter = pdf.w - 40
                        alto_scatter = ancho_scatter / 2.3  # Más ancho que alto
                        # Asegurar que quepa
                        max_alto = pdf.h - 100  # Espacio para header, footer y KPIs
                        if alto_scatter > max_alto:
                            alto_scatter = max_alto
                            ancho_scatter = alto_scatter * 2.3
                        # Centrar horizontalmente
                        x_centro = (pdf.w - ancho_scatter) / 2
                        pdf.image(
                            img_path,
                            x=x_centro,
                            y=38,
                            w=ancho_scatter,
                            h=alto_scatter
                        )
                
                # Añadir KPIs debajo del scatter si están disponibles
                if kpis_data:
                    y_kpis = 38 + alto_scatter + 10
                    pdf.set_y(y_kpis)
                    
                    # Título de KPIs
                    pdf.set_font('Arial', 'B', 14)
                    pdf.set_text_color(*pdf.orange_rgb)
                    pdf.cell(0, 8, clean_text_for_pdf("Indicadores del Ultimo Partido"), align='C', ln=True)
                    pdf.ln(3)
                    
                    # KPIs textuales
                    kpi_texts = kpis_data.get('textuales', [])
                    if kpi_texts:
                        ancho_kpi = (pdf.w - 50) / len(kpi_texts)
                        x_inicio = 25
                        pdf.set_font('Arial', 'B', 10)
                        pdf.set_text_color(*pdf.orange_rgb)
                        
                        for idx, (label, value) in enumerate(kpi_texts):
                            x_pos = x_inicio + idx * ancho_kpi
                            pdf.set_xy(x_pos, pdf.get_y())
                            
                            # Caja para KPI
                            pdf.set_fill_color(25, 25, 25)
                            pdf.rect(x_pos, pdf.get_y(), ancho_kpi - 5, 12, 'F')
                            pdf.set_draw_color(*pdf.orange_rgb)
                            pdf.rect(x_pos, pdf.get_y(), ancho_kpi - 5, 12, 'D')
                            
                            # Valor
                            display = str(value) if pd.notna(value) else "-"
                            pdf.set_text_color(*pdf.orange_rgb)
                            pdf.set_xy(x_pos + 2, pdf.get_y() + 1)
                            pdf.set_font('Arial', 'B', 9)
                            pdf.cell(ancho_kpi - 9, 5, clean_text_for_pdf(display[:20]), align='C')
                            
                            # Label
                            pdf.set_text_color(*pdf.gray_rgb)
                            pdf.set_xy(x_pos + 2, pdf.get_y() + 6)
                            pdf.set_font('Arial', '', 7)
                            pdf.cell(ancho_kpi - 9, 4, clean_text_for_pdf(label[:25]), align='C')
                        
                        pdf.ln(15)
                    
                    # KPIs numéricos
                    kpi_numericos = kpis_data.get('numericos', [])
                    if kpi_numericos:
                        ancho_kpi = (pdf.w - 50) / len(kpi_numericos)
                        x_inicio = 25
                        y_kpi_num = pdf.get_y()
                        
                        for idx, (label, val) in enumerate(kpi_numericos):
                            x_pos = x_inicio + idx * ancho_kpi
                            
                            # Caja para KPI numérico
                            pdf.set_fill_color(25, 25, 25)
                            pdf.rect(x_pos, y_kpi_num, ancho_kpi - 5, 18, 'F')
                            pdf.set_draw_color(*pdf.orange_rgb)
                            pdf.rect(x_pos, y_kpi_num, ancho_kpi - 5, 18, 'D')
                            
                            # Valor numérico
                            if "Tarjetas" in label:
                                display = "-" if pd.isna(val) else f"{int(val)}"
                            else:
                                display = "-" if pd.isna(val) else f"{val:.2f}"
                            
                            pdf.set_text_color(*pdf.orange_rgb)
                            pdf.set_xy(x_pos + 2, y_kpi_num + 2)
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(ancho_kpi - 9, 8, clean_text_for_pdf(display), align='C')
                            
                            # Label
                            pdf.set_text_color(*pdf.gray_rgb)
                            pdf.set_xy(x_pos + 2, y_kpi_num + 11)
                            pdf.set_font('Arial', '', 7)
                            pdf.cell(ancho_kpi - 9, 5, clean_text_for_pdf(label[:30]), align='C')
        
        # Procesar resto de gráficos agrupados por tab
        # Primero, agrupar por tab (filtrar "Sin categoria")
        graficos_por_tab = {}
        for figura_info in otros_graficos:
            tab_nombre = figura_info.get('tab', None)
            # Si no tiene tab, intentar inferirlo del título o usar "Otros"
            if not tab_nombre or tab_nombre == "Sin categoria":
                # Intentar inferir del título (usar nombres exactos de los tabs)
                titulo = figura_info.get('titulo', '').lower()
                if any(x in titulo for x in ['eficiencia', 'ataque', 'produccion', 'tiro', 'patrones', 'balon', 'juego']):
                    tab_nombre = "Eficiencia y Ataque"
                elif any(x in titulo for x in ['pase', 'construccion', 'construcción', 'control', 'progresion', 'longitud']):
                    tab_nombre = "Construcción y Pases"
                elif any(x in titulo for x in ['defensa', 'duelo', 'disputa', 'intercepcion', 'despeje']):
                    tab_nombre = "Defensa y Eficiencia"
                elif any(x in titulo for x in ['recuperacion', 'presion', 'distribucion', 'distribución', 'tactica', 'táctica']):
                    tab_nombre = "Distribución Táctica"
                elif any(x in titulo for x in ['comparativa', 'tabla', 'analisis', 'análisis']):
                    tab_nombre = "Análisis Comparativo (Tablas)"
                else:
                    tab_nombre = "Otros"
            
            if tab_nombre not in graficos_por_tab:
                graficos_por_tab[tab_nombre] = []
            graficos_por_tab[tab_nombre].append(figura_info)
        
        # Procesar cada tab
        for tab_nombre, graficos_tab in graficos_por_tab.items():
            num_graficos = len(graficos_tab)
            graficos_por_pagina = 4
            
            for i in range(0, num_graficos, graficos_por_pagina):
                # Nueva página para cada grupo de 4
                pdf.add_page()
                
                # Fondo negro
                pdf.set_fill_color(*pdf.black_rgb)
                pdf.rect(0, 0, pdf.w, pdf.h, 'F')
                
                # Título de la sección (nombre del tab) - solo en primera página del tab
                if i == 0:
                    pdf.set_font('Arial', 'B', 20)
                    pdf.set_text_color(*pdf.orange_rgb)
                    pdf.set_y(28)  # Después del header (22mm) + espacio (6mm)
                    pdf.cell(0, 10, clean_text_for_pdf(tab_nombre), align='C', ln=True)
                    y_inicio = 42
                else:
                    y_inicio = 28  # Después del header
                
                # Dimensiones para 2x2 en landscape A4 (297mm x 210mm)
                # Formato tipo presentación: gráficos más anchos que altos
                ancho_grafico = (pdf.w - 40) / 2  # 2 columnas con márgenes
                # Proporción 2.5:1 (mucho más ancho que alto) para formato presentación
                # Considerar header (22mm) y footer (18mm)
                alto_disponible = pdf.h - y_inicio - 20  # Espacio para footer
                alto_grafico = (alto_disponible / 2) * 0.70  # Más ancho, menos alto (formato PPT)
                
                # Procesar hasta 4 gráficos en esta página
                grupo = graficos_tab[i:i+graficos_por_pagina]
                
                for idx, figura_info in enumerate(grupo):
                    fig = figura_info.get('fig')
                    titulo_grafico_raw = figura_info.get('titulo', f'Grafico {i+idx+1}')
                    # Limpiar título ANTES de truncarlo
                    titulo_grafico = clean_text_for_pdf(titulo_grafico_raw)
                    
                    if fig is None:
                        continue
                    
                    # Convertir Plotly a imagen con mejor proporción (más ancho, menos alto)
                    # Proporción 2.5:1 para formato presentación (menos alargado)
                    img_bytes = plotly_to_image(fig, width=1100, height=350, scale=2.0)
                    if img_bytes is None:
                        continue
                    
                    # Guardar temporalmente
                    img_path = save_image_temp(img_bytes)
                    if img_path is None:
                        continue
                    
                    temp_files.append(img_path)
                    
                    # Calcular posición (2x2 grid)
                    fila = idx // 2
                    columna = idx % 2
                    
                    x_pos = 15 + columna * (ancho_grafico + 10)
                    y_pos = y_inicio + fila * (alto_grafico + 8)
                    
                    # Título del gráfico (pequeño, arriba)
                    pdf.set_font('Arial', 'B', 10)
                    pdf.set_text_color(*pdf.orange_rgb)
                    pdf.set_xy(x_pos, y_pos)
                    # Truncar título si es muy largo (ya está limpio de Unicode)
                    titulo_corto = titulo_grafico[:40] + "..." if len(titulo_grafico) > 40 else titulo_grafico
                    pdf.cell(ancho_grafico, 5, titulo_corto, align='C')
                    
                    # Imagen del gráfico
                    pdf.image(
                        img_path,
                        x=x_pos,
                        y=y_pos + 6,
                        w=ancho_grafico,
                        h=alto_grafico - 6
                    )
        
        # Página de cierre
        pdf.generar_cierre()
        
        # Generar PDF como bytes
        pdf_bytes = pdf.output(dest='S')
        
        # Asegurar que es bytes (no bytearray)
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        
        return pdf_bytes
        
    finally:
        # Limpiar archivos temporales
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
            except:
                pass

