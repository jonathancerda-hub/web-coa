from fpdf import FPDF
import os
import sys
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDF(FPDF):
    def header(self):
        # --- CABECERA DE PHARMADIX ACTUALIZADA ---
        try:
            # Logo en la esquina superior derecha
            self.image(resource_path("static/image/logoheader.png"), x=160, y=8, w=40)
        except FileNotFoundError:
            pass
        
        # Posiciona el cursor para las líneas
        self.set_y(30)
        # Dibuja la doble línea
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(self.get_y() + 0.5)
        self.line(10, self.get_y(), 200, self.get_y())

        # Deja un espacio antes de que comience el contenido principal
        self.ln(5)

    def footer(self):
        # El pie de página no cambia
        self.set_y(-20)
        self.set_font('DejaVuSans', 'I', 8)
        self.set_text_color(128)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.cell(0, 5, "Av. Santa Lucía Nº 218 Urb. Ind. La Aurora, Ate", 0, 2, 'R')
        self.cell(0, 5, "51 1 326 09 10 - www.pharmadix.com - ventas@pharmadix.com", 0, 0, 'R')

class AgrovetPDF(FPDF):
    def header(self):
        # --- CABECERA DE AGROVET MARKET ACTUALIZADA ---
        try:
            # Logo en la esquina superior derecha
            self.image(resource_path("static/image/agrovet_logo.png"), x=160, y=10, w=30)
        except FileNotFoundError:
            self.set_font("DejaVuSans", 'B', 14)
            self.set_xy(160, 10)
            self.cell(0, 10, 'AGROVET MARKET', 0, 0, 'R')
        
        # Posiciona el cursor para las líneas
        self.set_y(30)
        # Dibuja la doble línea
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(self.get_y() + 0.5)
        self.line(10, self.get_y(), 200, self.get_y())

        # Deja un espacio antes de que comience el contenido principal
        self.ln(5)

    def footer(self):
        # El pie de página no cambia
        self.set_y(-20)
        self.set_font('DejaVuSans', 'I', 8)
        self.set_text_color(128)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.cell(0, 5, "Av. Canadá 3792, San Luis, Lima - Perú", 0, 2, 'R')
        self.cell(0, 5, "T: +51 1 2 300 300", 0, 0, 'R')

def format_month_year(date_str):
    if not date_str: return "N/A"
    try:
        # Intentar parsear el formato estándar dd-mm-yyyy
        dt = datetime.strptime(date_str, '%d-%m-%Y')
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        return f"{meses[dt.month-1]}-{dt.strftime('%y')}"
    except (ValueError, TypeError):
        return date_str

def generar_certificado_en_memoria(data, pdf_class_name="PDF"):
    # (Esta función no necesita cambios, pero se incluye para que el archivo esté completo)
    pdf_class = AgrovetPDF if pdf_class_name == "AgrovetPDF" else PDF
    try:
        pdf = pdf_class(orientation='P', unit='mm', format='A4')
        pdf.add_font('DejaVuSans', '', resource_path('fonts/DejaVuSansCondensed.ttf'))
        pdf.add_font('DejaVuSans', 'B', resource_path('fonts/DejaVuSansCondensed-Bold.ttf'))
        pdf.add_font('DejaVuSans', 'I', resource_path('fonts/DejaVuSansCondensed-Oblique.ttf'))
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=10)  # Reducir margen inferior
        # --- SECCIÓN 1: TÍTULO ---
        cert_title = f"CERTIFICADO DE ANÁLISIS N° {data.get('CODIGO', 'N/A')}"
        dept_text = 'DEPARTAMENTO DE CONTROL DE CALIDAD'
        pdf.set_font("DejaVuSans", '', 8)  # Reducir tamaño de fuente general
        pdf.cell(0, 6, dept_text, 0, 1, 'C')
        pdf.set_font("DejaVuSans", 'B', 10)  # Reducir tamaño de fuente del título
        pdf.cell(0, 8, cert_title, 0, 1, 'C')
        pdf.ln(3)
        # --- SECCIÓN 2: DATOS DEL PRODUCTO ---
        info_producto_base = {
            "PRODUCTO": str(data.get('PRODUCTO', '')), "PRESENTACIÓN": str(data.get('PRESENTACION', '')),
            "LOTE": str(data.get('LOTE', '')), "FORMA FARMACÉUTICA": str(data.get('FORMA_FARMACEUTICA', '')),
            "CANTIDAD LOTE": str(data.get('CANTIDAD', '')), 
            "FECHA DE FABRICACIÓN": format_month_year(data.get('FECHA_PRODUCCION', '')),
            "FECHA DE EXPIRACIÓN": format_month_year(data.get('FECHA_VENCIMIENTO', '')), 
            "FECHA DE ANÁLISIS": str(data.get('FECHA_ANALISIS', '')),
            "FECHA DE EMISIÓN": str(data.get('FECHA_EMISION', ''))
        }
        info_producto = info_producto_base
        if pdf_class_name != "AgrovetPDF":
            info_producto["LINEA"] = str(data.get('LABORATORIO', ''))
            info_producto["REFERENCIA"] = str(data.get('REFERENCIA', ''))
        for key, value in info_producto.items():
            pdf.set_font("DejaVuSans", 'B', 8)
            pdf.cell(60, 5, key, 0, 0, 'L')
            pdf.set_font("DejaVuSans", '', 8)
            pdf.cell(0, 5, f": {value}", 0, 1, 'L')
        pdf.ln(4)
        # --- SECCIÓN 3: TABLA DE ANÁLISIS ---
        w_ensayo, w_especificaciones, w_resultados = 60, 80, 50
        line_height = 5  # Reducir altura de línea
        pdf.set_font("DejaVuSans", 'B', 9)  # Reducir tamaño de fuente de encabezado de tabla
        pdf.cell(w_ensayo, 6, 'ENSAYOS', 1, 0, 'C')
        pdf.cell(w_especificaciones, 6, 'ESPECIFICACIONES', 1, 0, 'C')
        pdf.cell(w_resultados, 6, 'RESULTADOS', 1, 1, 'C')
        pdf.set_font("DejaVuSans", '', 7)  # Reducir tamaño de fuente de tabla
        table_data = []
        for i in range(1, 21):
            ensayo = str(data.get(f'ENSAYO{i}', ''))
            if ensayo.startswith('[OCULTO]'):
                continue
            especificacion = str(data.get(f'ESPECIFICACION{i}', ''))
            resultado = str(data.get(f'RESULTADO{i}', ''))
            if ensayo or especificacion or resultado:
                table_data.append([ensayo, especificacion, resultado])
        y_start_table = pdf.get_y()
        x_start_table = pdf.get_x()
        current_y = y_start_table
        for row in table_data:
            ensayo, especificacion, resultado = row
            ensayo_lines = pdf.multi_cell(w_ensayo, line_height, ensayo, split_only=True)
            especificacion_lines = pdf.multi_cell(w_especificaciones, line_height, especificacion, split_only=True)
            resultado_lines = pdf.multi_cell(w_resultados, line_height, resultado, split_only=True)
            row_height = max(len(ensayo_lines), len(especificacion_lines), len(resultado_lines)) * line_height
            pdf.set_y(current_y)
            pdf.set_x(x_start_table)
            pdf.multi_cell(w_ensayo, line_height, ensayo, align='L', border=0)
            pdf.set_y(current_y)
            pdf.set_x(x_start_table + w_ensayo)
            pdf.multi_cell(w_especificaciones, line_height, especificacion, align='L', border=0)
            pdf.set_y(current_y)
            pdf.set_x(x_start_table + w_ensayo + w_especificaciones)
            pdf.multi_cell(w_resultados, line_height, resultado, align='C', border=0)
            current_y += row_height
        total_table_height = current_y - y_start_table
        pdf.rect(x_start_table, y_start_table, w_ensayo + w_especificaciones + w_resultados, total_table_height)
        pdf.line(x_start_table + w_ensayo, y_start_table, x_start_table + w_ensayo, y_start_table + total_table_height)
        pdf.line(x_start_table + w_ensayo + w_especificaciones, y_start_table, x_start_table + w_ensayo + w_especificaciones, y_start_table + total_table_height)
        pdf.set_y(current_y)
        pdf.ln(5)
        # --- SECCIÓN 4: CONCLUSIÓN Y OBSERVACIONES ---
        if pdf_class_name == "AgrovetPDF":
            pdf.set_font("DejaVuSans", '', 10)
            # Solo el texto por defecto solicitado para Agrovet
            pdf.multi_cell(0, 6, "Referencia Certificado de Análisis Pharmadix", 0, 'L')
        else:
            # Pharmadix muestra observaciones solo si tienen contenido
            observaciones = str(data.get('OBSERVACIONES', '')).strip()
            if observaciones:
                pdf.set_font("DejaVuSans", '', 8)
                pdf.multi_cell(0, 5, "OBSERVACIONES: " + observaciones, 0, 'L')
        pdf.ln(3)
        pdf.set_font("DejaVuSans", 'B', 8)
        pdf.cell(30, 5, "CONCLUSIÓN:", 0, 0, 'L')
        pdf.set_font("DejaVuSans", '', 8)
        pdf.cell(0, 5, str(data.get('CONCLUSION', '')), 0, 1, 'L')
        return bytes(pdf.output())
    except Exception as e:
        print(f"Error detallado al crear el PDF: {e}")
        return None
