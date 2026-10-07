import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def generate_certificate(
    name,
    email,
    course,
    certificate_id,
    output_folder
):

    os.makedirs(output_folder, exist_ok=True)

    file_name = f"certificate_{certificate_id}.pdf"

    file_path = os.path.join(
        output_folder,
        file_name
    )

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        file_path,
        pagesize=(page_width, page_height)
    )

    # Outer border
    pdf.setStrokeColor(colors.darkblue)
    pdf.setLineWidth(4)

    pdf.rect(
        15 * mm,
        15 * mm,
        page_width - 30 * mm,
        page_height - 30 * mm
    )

    # Inner border
    pdf.setStrokeColor(colors.lightgrey)
    pdf.setLineWidth(1)

    pdf.rect(
        22 * mm,
        22 * mm,
        page_width - 44 * mm,
        page_height - 44 * mm
    )

    # Title
    pdf.setFillColor(colors.darkblue)
    pdf.setFont("Helvetica-Bold", 30)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 65 * mm,
        "CERTIFICATE OF COMPLETION"
    )

    # Subtitle
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 85 * mm,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFillColor(colors.darkblue)
    pdf.setFont("Helvetica-Bold", 28)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 105 * mm,
        name
    )

    # Course text
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 125 * mm,
        "for successfully completing"
    )

    # Course name
    pdf.setFillColor(colors.darkblue)
    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 142 * mm,
        course
    )

    # Certificate ID
    pdf.setFillColor(colors.grey)
    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        30 * mm,
        28 * mm,
        f"Certificate ID: {certificate_id}"
    )

    pdf.drawRightString(
        page_width - 30 * mm,
        28 * mm,
        email
    )

    pdf.showPage()
    pdf.save()

    return file_path