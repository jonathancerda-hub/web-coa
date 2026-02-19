from fpdf import FPDF
import os
import sys
import re
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDF(FPDF):
    def header(self):
        try:
            self.image(resource_path("static/image/logoheader.png"), x=160, y=8, w=40)
        except: pass
        self.set_y(30)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(self.get_y() + 0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.cell(0, 5, "Av. Santa Lucía Nº 218 Urb. Ind. La Aurora, Ate", 0, 2, 'R')
        self.cell(0, 5, "51 1 326 09 10 - www.pharmadix.com - ventas@pharmadix.com", 0, 0, 'R')

class AgrovetPDF(FPDF):
    def header(self):
        try:
            self.image(resource_path("static/image/agrovet_logo.png"), x=160, y=10, w=30)
        except:
            self.set_font("helvetica", 'B', 14)
            self.set_xy(160, 10)
            self.cell(0, 10, 'AGROVET MARKET', 0, 0, 'R')
        self.set_y(30)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(self.get_y() + 0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.cell(0, 5, "Av. Canadá 3792, San Luis, Lima - Perú", 0, 2, 'R')
        self.cell(0, 5, "T: +51 1 2 300 300", 0, 0, 'R')

def format_month_year(date_str):
    if not date_str: return "N/A"
    try:
        dt = datetime.strptime(date_str, '%d-%m-%Y')
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        return f"{meses[dt.month-1]}-{dt.strftime('%y')}"
    except: return str(date_str)

def procesar_texto(text, catalog, mode="pharmadix"):
    if not text: return ""
    text_str = str(text)
    if "[N:" not in text_str: return text_str
    
    if mode == "agrovet":
        return re.sub(r'\[N:\s*.*?\s*\]', '', text_str).strip()
    
    def repl(m):
        nota = m.group(1).strip()
        if nota not in catalog:
            catalog.append(nota)
        idx = catalog.index(nota) + 1
        return f" ({idx})"
    return re.sub(r'\[N:\s*(.*?)\s*\]', repl, text_str)

def generar_certificado_en_memoria(data, pdf_class_name="PDF"):
    pdf_class = AgrovetPDF if pdf_class_name == "AgrovetPDF" else PDF
    try:
        pdf = pdf_class(orientation='P', unit='mm', format='A4')
        pdf.set_margins(15, 15, 15)
        pdf.c_margin = 1.0 # Evita error de espacio horizontal
        
        try:
            pdf.add_font('DejaVu', '', resource_path('fonts/DejaVuSansCondensed.ttf'))
            pdf.add_font('DejaVu', 'B', resource_path('fonts/DejaVuSansCondensed-Bold.ttf'))
            f_family = 'DejaVu'
        except:
            f_family = 'helvetica'
        
        pdf.set_font(f_family, '', 8)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        notas_catalogo = []
        is_agrovet = (pdf_class_name == "AgrovetPDF")
        proc_mode = "agrovet" if is_agrovet else "pharmadix"

        # --- SEGUNDA SECCIÓN: TÍTULO ---
        pdf.set_font(f_family, 'B', 10)
        pdf.cell(0, 6, 'DEPARTAMENTO DE CONTROL DE CALIDAD', 0, 1, 'C')
        pdf.cell(0, 8, f"CERTIFICADO DE ANÁLISIS N° {data.get('CODIGO', 'N/A')}", 0, 1, 'C')
        pdf.ln(3)

        # --- DATOS PRODUCTO ---
        info_keys = [
            ("PRODUCTO", 'PRODUCTO'), ("PRESENTACIÓN", 'PRESENTACION'),
            ("LOTE", 'LOTE'), ("FORMA FARMACÉUTICA", 'FORMA_FARMACEUTICA'),
            ("CANTIDAD LOTE", 'CANTIDAD'), 
            ("FECHA DE FABRICACIÓN", 'FECHA_PRODUCCION'),
            ("FECHA DE EXPIRACIÓN", 'FECHA_VENCIMIENTO'), 
            ("FECHA DE ANÁLISIS", 'FECHA_ANALISIS'),
            ("FECHA DE EMISIÓN", 'FECHA_EMISION')
        ]
        
        for label, key in info_keys:
            val = data.get(key, '')
            if key in ['FECHA_PRODUCCION', 'FECHA_VENCIMIENTO']: val = format_month_year(val)
            pdf.set_font(f_family, 'B', 8)
            pdf.cell(50, 5, label, 0, 0, 'L')
            pdf.set_font(f_family, '', 8)
            val_clean = procesar_texto(val, notas_catalogo, mode=proc_mode)
            pdf.cell(0, 5, f": {val_clean}", 0, 1, 'L')
            
        if not is_agrovet:
            pdf.set_font(f_family, 'B', 8)
            pdf.cell(50, 5, "LINEA", 0, 0, 'L')
            pdf.set_font(f_family, '', 8)
            pdf.cell(0, 5, f": {data.get('LABORATORIO', '')}", 0, 1, 'L')
            pdf.set_font(f_family, 'B', 8)
            pdf.cell(50, 5, "REFERENCIA", 0, 0, 'L')
            pdf.set_font(f_family, '', 8)
            pdf.cell(0, 5, f": {data.get('REFERENCIA', '')}", 0, 1, 'L')
        pdf.ln(4)

        # --- TABLA DE ANÁLISIS ---
        w1, w2, w3 = 55, 80, 45 
        pdf.set_font(f_family, 'B', 9)
        pdf.cell(w1, 7, 'ENSAYOS', 1, 0, 'C')
        pdf.cell(w2, 7, 'ESPECIFICACIONES', 1, 0, 'C')
        pdf.cell(w3, 7, 'RESULTADOS', 1, 1, 'C')
        
        pdf.set_font(f_family, '', 7)
        x_start = pdf.get_x()
        for i in range(1, 21):
            e = str(data.get(f'ENSAYO{i}', '') or '').strip()
            if e.startswith('[OCULTO]'): continue
            s = str(data.get(f'ESPECIFICACION{i}', '') or '').strip()
            r = str(data.get(f'RESULTADO{i}', '') or '').strip()
            n = str(data.get(f'NOTA{i}', '') or '').strip()
            
            if e or s or r:
                e = procesar_texto(e, notas_catalogo, mode=proc_mode)
                s = procesar_texto(s, notas_catalogo, mode=proc_mode)
                r = procesar_texto(r, notas_catalogo, mode=proc_mode)
                
                # Gestión de la NOTA estructurada
                if n and proc_mode == "pharmadix":
                    if n not in notas_catalogo:
                        notas_catalogo.append(n)
                    idx = notas_catalogo.index(n) + 1
                    r += f" ({idx})"
                
                # Calcular altura necesaria
                lines_e = pdf.multi_cell(w1, 5, e, split_only=True)
                lines_s = pdf.multi_cell(w2, 5, s, split_only=True)
                lines_r = pdf.multi_cell(w3, 5, r, split_only=True)
                row_h = max(len(lines_e), len(lines_s), len(lines_r), 1) * 5
                
                if pdf.get_y() + row_h > pdf.page_break_trigger:
                    # Cerrar tabla antes de saltar
                    pdf.line(x_start, pdf.get_y(), x_start + w1 + w2 + w3, pdf.get_y())
                    pdf.add_page()
                    # Re-dibujar cabecera si es necesario (opcional)
                
                curr_y = pdf.get_y()
                curr_x = pdf.get_x()
                
                # Renderizado con bordes Laterales únicamente ('LR') para evitar líneas internas
                pdf.multi_cell(w1, 5, e, border='LR', align='L', new_x='RIGHT', new_y='TOP')
                pdf.multi_cell(w2, 5, s, border='LR', align='L', new_x='RIGHT', new_y='TOP')
                pdf.multi_cell(w3, 5, r, border='LR', align='C', new_x='LEFT', new_y='NEXT')
                
                pdf.set_y(curr_y + row_h)

        # Línea final de la tabla
        pdf.line(x_start, pdf.get_y(), x_start + w1 + w2 + w3, pdf.get_y())
        pdf.ln(5)

        # --- FOOTER CONTENT ---
        content_obs = []
        m_obs = str(data.get('OBSERVACIONES', '') or '').strip()
        if m_obs: content_obs.append(m_obs)
        if not is_agrovet and notas_catalogo:
            for idx, n in enumerate(notas_catalogo):
                content_obs.append(f"({idx+1}) {n.upper()}")

        if is_agrovet:
            pdf.set_font(f_family, '', 10)
            pdf.multi_cell(0, 6, "Referencia Certificado de Análisis Pharmadix", 0, 'L')
        elif content_obs:
            pdf.set_font(f_family, 'B', 8)
            pdf.cell(0, 5, "OBSERVACIONES:", 0, 1, 'L')
            pdf.set_font(f_family, '', 8)
            for item in content_obs:
                pdf.multi_cell(0, 5, item, 0, 'L')
        
        pdf.ln(3)
        pdf.set_font(f_family, 'B', 8)
        pdf.cell(30, 5, "CONCLUSIÓN:", 0, 0, 'L')
        pdf.set_font(f_family, '', 8)
        pdf.cell(0, 5, str(data.get('CONCLUSION', 'PENDIENTE')), 0, 1, 'L')
        
        return bytes(pdf.output())
    except Exception as e:
        import traceback
        print(f"ERROR PDF: {e}")
        traceback.print_exc()
        return None
