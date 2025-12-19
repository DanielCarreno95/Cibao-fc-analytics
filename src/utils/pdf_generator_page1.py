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
        self.set_auto_page_break(auto=True, margin=20)
        self.orange_rgb = hex_to_rgb(CIBAO_ORANGE)
        self.gray_rgb = hex_to_rgb(CIBAO_GRAY)
        self.black_rgb = hex_to_rgb(CIBAO_BLACK)
        self.es_contenido = False
    
    def header(self):
        """Header personalizado (opcional, no lo usamos por ahora)"""
        pass
    
    def footer(self):
        """Footer con número de página"""
        if self.es_contenido:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(*self.gray_rgb)
            self.cell(0, 10, clean_text_for_pdf(f'Pagina {self.page_no()}'), 0, 0, 'C')
    
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
                # Título
                pdf.set_font('Arial', 'B', 14)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_y(10)
                pdf.cell(0, 8, titulo_scatter, align='C', ln=True)
                
                # Convertir y mostrar scatter a tamaño completo
                img_bytes = plotly_to_image(fig, width=1200, height=600, scale=2.0)
                if img_bytes:
                    img_path = save_image_temp(img_bytes)
                    if img_path:
                        temp_files.append(img_path)
                        # Gráfico centrado, ocupando la mayor parte de la página
                        ancho_scatter = pdf.w - 20
                        alto_scatter = pdf.h - 30
                        pdf.image(
                            img_path,
                            x=10,
                            y=20,
                            w=ancho_scatter,
                            h=alto_scatter
                        )
        
        # Procesar resto de gráficos en grupos de 4 (2x2 por página)
        num_graficos = len(otros_graficos)
        graficos_por_pagina = 4
        
        for i in range(0, num_graficos, graficos_por_pagina):
            # Nueva página para cada grupo de 4
            pdf.add_page()
            
            # Fondo negro
            pdf.set_fill_color(*pdf.black_rgb)
            pdf.rect(0, 0, pdf.w, pdf.h, 'F')
            
            # Título de la página (opcional)
            if i == 0:
                pdf.set_font('Arial', 'B', 16)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_y(8)
                pdf.cell(0, 8, clean_text_for_pdf("Analisis de Rendimiento"), align='C', ln=True)
                y_inicio = 20
            else:
                y_inicio = 10
            
            # Dimensiones para 2x2 en landscape A4 (297mm x 210mm)
            # Márgenes: 10mm a cada lado = 20mm total horizontal, 10mm arriba/abajo
            ancho_grafico = (pdf.w - 30) / 2  # 2 columnas con márgenes (10mm cada lado + 10mm entre)
            alto_grafico = (pdf.h - y_inicio - 25) / 2  # 2 filas con espacio entre
            
            # Procesar hasta 4 gráficos en esta página
            grupo = otros_graficos[i:i+graficos_por_pagina]
            
            for idx, figura_info in enumerate(grupo):
                fig = figura_info.get('fig')
                titulo_grafico_raw = figura_info.get('titulo', f'Grafico {i+idx+1}')
                # Limpiar título ANTES de truncarlo
                titulo_grafico = clean_text_for_pdf(titulo_grafico_raw)
                
                if fig is None:
                    continue
                
                # Convertir Plotly a imagen
                img_bytes = plotly_to_image(fig, width=800, height=400, scale=2.0)
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
                
                x_pos = 10 + columna * (ancho_grafico + 10)
                y_pos = y_inicio + fila * (alto_grafico + 5)
                
                # Título del gráfico (pequeño, arriba)
                pdf.set_font('Arial', 'B', 9)
                pdf.set_text_color(*pdf.orange_rgb)
                pdf.set_xy(x_pos, y_pos)
                # Truncar título si es muy largo (ya está limpio de Unicode)
                titulo_corto = titulo_grafico[:35] + "..." if len(titulo_grafico) > 35 else titulo_grafico
                pdf.cell(ancho_grafico, 4, titulo_corto, align='C')
                
                # Imagen del gráfico
                pdf.image(
                    img_path,
                    x=x_pos,
                    y=y_pos + 5,
                    w=ancho_grafico,
                    h=alto_grafico - 5
                )
        
        # Página de cierre
        pdf.generar_cierre()
        
        # Generar PDF como bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        return pdf_bytes
        
    finally:
        # Limpiar archivos temporales
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
            except:
                pass

