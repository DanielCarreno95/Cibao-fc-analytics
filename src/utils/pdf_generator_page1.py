"""
Generador de PDF para Página 1 - Rendimiento Colectivo Liga
Basado en el template de PDF TEMPLATE pero adaptado para gráficos Plotly
"""

import io
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
        # A4 Landscape: 297mm x 210mm
        super().__init__(orientation='L', unit='mm', format=(297, 210))
        self.set_auto_page_break(auto=True, margin=35)  # Más margen para header/footer
        self.orange_rgb = hex_to_rgb(CIBAO_ORANGE)
        self.gray_rgb = hex_to_rgb(CIBAO_GRAY)
        self.black_rgb = hex_to_rgb(CIBAO_BLACK)
        self.es_contenido = False
        self.tab_actual = None  # Para rastrear el tab actual
    
    def header(self):
        """Header personalizado con logo y título"""
        if self.es_contenido:
            # Fondo del header (barra naranja)
            self.set_fill_color(*self.orange_rgb)
            self.rect(0, 0, self.w, 20, 'F')
            
            # Título del header
            self.set_y(5)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(255, 255, 255)  # Blanco
            self.cell(0, 10, clean_text_for_pdf("Cibao FC - Reporte de Rendimiento Colectivo"), align='C')
            
            # Fecha en la esquina derecha
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            self.set_font('Arial', '', 9)
            self.set_xy(self.w - 50, 5)
            self.cell(45, 10, clean_text_for_pdf(fecha_actual), align='R')
    
    def footer(self):
        """Footer con número de página y marca"""
        if self.es_contenido:
            # Fondo del footer (barra gris oscura)
            self.set_fill_color(40, 40, 40)
            self.rect(0, self.h - 15, self.w, 15, 'F')
            
            # Número de página centrado
            self.set_y(-12)
            self.set_font('Arial', 'I', 9)
            self.set_text_color(*self.gray_rgb)
            self.cell(0, 10, clean_text_for_pdf(f'Pagina {self.page_no()}'), align='C')
            
            # Marca en la esquina izquierda
            self.set_xy(10, -12)
            self.set_font('Arial', '', 8)
            self.cell(0, 10, clean_text_for_pdf("Cibao FC Data Hub"), align='L')
    
    def generar_caratula(self, titulo: str, subtitulo: str):
        """Genera la portada del PDF"""
        self.add_page()
        self.es_contenido = False
        
        # Fondo naranja (como solicitaste)
        self.set_fill_color(*self.orange_rgb)
        self.rect(0, 0, self.w, self.h, 'F')
        
        # Título principal (blanco sobre naranja)
        self.set_y(75)
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
    subtitulo: str = "Cibao FC - Liga Dominicana"
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
        
        # Página especial para scatter inicial (si existe)
        if scatter_inicial:
            pdf.add_page()
            pdf.set_fill_color(*pdf.black_rgb)
            pdf.rect(0, 0, pdf.w, pdf.h, 'F')
            
            fig = scatter_inicial.get('fig')
            titulo_scatter_raw = scatter_inicial.get('titulo', 'Comparativa Liga')
            titulo_scatter = clean_text_for_pdf(titulo_scatter_raw)
            
            if fig is not None:
                # Título (después del header)
                pdf.set_font('Arial', 'B', 16)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_y(25)
                pdf.cell(0, 10, titulo_scatter, align='C', ln=True)
                
                # Convertir y mostrar scatter a tamaño completo con mejor proporción
                # Aspect ratio más cuadrado para evitar alargamiento
                img_bytes = plotly_to_image(fig, width=1400, height=800, scale=2.0)
                if img_bytes:
                    img_path = save_image_temp(img_bytes)
                    if img_path:
                        temp_files.append(img_path)
                        # Gráfico centrado, con mejor proporción (más ancho que alto)
                        ancho_scatter = pdf.w - 40
                        # Mantener proporción 16:9 aproximadamente
                        alto_scatter = (ancho_scatter * 9) / 16
                        # Asegurar que quepa en la página (considerando header y footer)
                        max_alto = pdf.h - 50  # Espacio para header (20) + footer (15) + márgenes
                        if alto_scatter > max_alto:
                            alto_scatter = max_alto
                            ancho_scatter = (alto_scatter * 16) / 9
                        # Centrar horizontalmente y verticalmente
                        x_centro = (pdf.w - ancho_scatter) / 2
                        y_centro = 38 + (max_alto - alto_scatter) / 2  # Después del título
                        pdf.image(
                            img_path,
                            x=x_centro,
                            y=y_centro,
                            w=ancho_scatter,
                            h=alto_scatter
                        )
        
        # Procesar resto de gráficos agrupados por tab
        # Primero, agrupar por tab
        graficos_por_tab = {}
        for figura_info in otros_graficos:
            tab_nombre = figura_info.get('tab', 'Sin categoria')
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
                
                # Título de la sección (nombre del tab)
                pdf.set_font('Arial', 'B', 18)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_y(25)
                pdf.cell(0, 10, clean_text_for_pdf(tab_nombre), align='C', ln=True)
                
                y_inicio = 38
                
                # Dimensiones para 2x2 en landscape A4 (297mm x 210mm)
                # Márgenes: 15mm a cada lado = 30mm total horizontal
                # Espacio para header (20mm) y footer (15mm) = 35mm vertical
                ancho_grafico = (pdf.w - 40) / 2  # 2 columnas con márgenes
                # Altura ajustada para mejor proporción (más ancho que alto)
                alto_grafico = ((pdf.h - y_inicio - 30) / 2) * 0.85  # Reducir altura para mejor proporción
                
                # Procesar hasta 4 gráficos en esta página
                grupo = graficos_tab[i:i+graficos_por_pagina]
                
                for idx, figura_info in enumerate(grupo):
                    fig = figura_info.get('fig')
                    titulo_grafico_raw = figura_info.get('titulo', f'Grafico {i+idx+1}')
                    # Limpiar título ANTES de truncarlo
                    titulo_grafico = clean_text_for_pdf(titulo_grafico_raw)
                    
                    if fig is None:
                        continue
                    
                    # Convertir Plotly a imagen con mejor proporción (más ancho)
                    img_bytes = plotly_to_image(fig, width=900, height=500, scale=2.0)
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

