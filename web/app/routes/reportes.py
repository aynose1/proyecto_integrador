from datetime import datetime
from io import BytesIO

from flask import Blueprint, render_template, send_file
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.decorators import admin_required

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


def _placeholder_rows():
    return [
        ["Módulo", "Estado"],
        ["Reportes", "En construcción"],
        ["Generado", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]


@bp.route("")
@admin_required
def index():
    return render_template("reportes/index.html")


@bp.route("/exportar/excel")
@admin_required
def exportar_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Reportes"

    for row in _placeholder_rows():
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"reportes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/exportar/pdf")
@admin_required
def exportar_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(inch, height - inch, "Reportes — Gestión de Residuos")

    pdf.setFont("Helvetica", 11)
    y = height - (1.5 * inch)
    for row in _placeholder_rows():
        pdf.drawString(inch, y, " | ".join(str(cell) for cell in row))
        y -= 0.25 * inch

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(inch, inch, "Este módulo está vacío por ahora. Define el contenido cuando lo necesites.")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    filename = f"reportes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")
