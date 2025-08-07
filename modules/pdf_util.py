# modules/pdf_util.py

import os
from fpdf import FPDF
from datetime import datetime

def init_pdf(filename, logo_path=None):
    """
    Inicializa el objeto FPDF con página, márgenes y logo opcional.
    Devuelve el objeto pdf.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Logo
    if logo_path and os.path.isfile(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
    # Título
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Recibo de Nómina', ln=True, align='C')
    pdf.ln(10)
    return pdf

def add_nomina_section(pdf, nomina_data, usuario):
    """
    Agrega al PDF los datos de la nómina:
    - Empleado, ID, periodo
    - Tabla con horas, bruto, descuentos y neto
    """
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Empleado: {usuario}', ln=True)
    pdf.cell(0, 8, f'Nómina ID: {nomina_data["id"]}', ln=True)
    pdf.cell(0, 8, f'Periodo: {nomina_data["fecha_inicio"]} - {nomina_data["fecha_fin"]}', ln=True)
    pdf.ln(5)

    # Ancho efectivo de página y columnas
    epw = pdf.w - 2*pdf.l_margin
    col_width = epw / 4

    # Cabecera de tabla
    pdf.set_font('Arial', 'B', 12)
    for header in ('Horas','Bruto','Descuentos','Neto'):
        pdf.cell(col_width, 8, header, border=1, align='C')
    pdf.ln()

    # Datos
    pdf.set_font('Arial', '', 12)
    pdf.cell(col_width, 8, f"{nomina_data['horas_trabajadas']}",     border=1, align='C')
    pdf.cell(col_width, 8, f"{nomina_data['sueldo_bruto']}",        border=1, align='C')
    pdf.cell(col_width, 8, f"{nomina_data['descuentos_total']}",    border=1, align='C')
    pdf.cell(col_width, 8, f"{nomina_data['neto_a_pagar']}",        border=1, align='C')
    pdf.ln(10)

    # Pie de página con fecha de generación
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)

def output_pdf(pdf, filename):
    """
    Guarda el PDF en disco con el nombre dado y devuelve la ruta absoluta.
    """
    pdf.output(filename)
    return os.path.abspath(filename)
