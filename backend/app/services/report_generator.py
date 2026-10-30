"""Deterministic (non-AI) service report rendering to PDF and DOCX.

No diagnostic actions, parts, or outcomes are invented here: this module only
formats whatever was captured on the ServiceReport/WorkOrder/ServiceNote rows.
Any required field left blank is rendered as "[REQUIRES ENGINEER
CONFIRMATION]" rather than being silently omitted or guessed.
"""

import os
from datetime import datetime

from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import REPORTS_DIR

MISSING = "[REQUIRES ENGINEER CONFIRMATION]"


def _val(value) -> str:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return MISSING
    return str(value)


def _report_context(work_order, report, customer, site, equipment, engineer) -> dict:
    return {
        "report_id": report.id,
        "work_order_title": work_order.title,
        "customer_name": customer.name if customer else MISSING,
        "site_name": site.name if site else MISSING,
        "engineer_name": engineer.full_name if engineer else MISSING,
        "generated_at": report.generated_at.strftime("%Y-%m-%d %H:%M UTC"),
        "equipment_manufacturer": equipment.manufacturer if equipment else MISSING,
        "equipment_model": equipment.model if equipment else MISSING,
        "equipment_serial": equipment.serial_number if equipment and equipment.serial_number else MISSING,
        "work_order_number": work_order.id,
        "initial_condition": _val(report.initial_condition),
        "investigation": _val(report.investigation),
        "outcome": _val(report.outcome),
        "follow_up": _val(report.follow_up),
        "parts_used": _val(report.parts_used),
        "engineer_signature_name": _val(report.engineer_signature_name),
        "customer_signature_name": _val(report.customer_signature_name),
    }


def generate_pdf(work_order, report, customer, site, equipment, engineer) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ctx = _report_context(work_order, report, customer, site, equipment, engineer)
    path = os.path.join(REPORTS_DIR, f"{report.id}.pdf")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4, title="NightBrew FieldOps AI - Service Report")
    elements = []

    elements.append(Paragraph("NightBrew FieldOps AI - Service Report", styles["Title"]))
    elements.append(Spacer(1, 6 * mm))

    meta_rows = [
        ["Work Order #", ctx["work_order_number"]],
        ["Customer", ctx["customer_name"]],
        ["Site", ctx["site_name"]],
        ["Engineer", ctx["engineer_name"]],
        ["Date Generated", ctx["generated_at"]],
        ["Equipment", f"{ctx['equipment_manufacturer']} {ctx['equipment_model']}"],
        ["Serial Number", ctx["equipment_serial"]],
    ]
    meta_table = Table(meta_rows, colWidths=[55 * mm, 110 * mm])
    meta_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elements.append(meta_table)
    elements.append(Spacer(1, 8 * mm))

    for heading, key in [
        ("Initial Condition", "initial_condition"),
        ("Investigation", "investigation"),
        ("Outcome", "outcome"),
        ("Follow Up", "follow_up"),
        ("Parts Used", "parts_used"),
    ]:
        elements.append(Paragraph(heading, styles["Heading2"]))
        elements.append(Paragraph(ctx[key].replace("\n", "<br/>"), styles["BodyText"]))
        elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph("Signatures", styles["Heading2"]))
    sig_rows = [
        ["Engineer", ctx["engineer_signature_name"]],
        ["Customer", ctx["customer_signature_name"]],
    ]
    sig_table = Table(sig_rows, colWidths=[55 * mm, 110 * mm])
    sig_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(sig_table)

    doc.build(elements)
    return path


def generate_docx(work_order, report, customer, site, equipment, engineer) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ctx = _report_context(work_order, report, customer, site, equipment, engineer)
    path = os.path.join(REPORTS_DIR, f"{report.id}.docx")

    document = Document()
    document.add_heading("NightBrew FieldOps AI - Service Report", level=1)

    table = document.add_table(rows=0, cols=2)
    for label, key in [
        ("Work Order #", "work_order_number"),
        ("Customer", "customer_name"),
        ("Site", "site_name"),
        ("Engineer", "engineer_name"),
        ("Date Generated", "generated_at"),
        ("Equipment", "equipment_model"),
        ("Serial Number", "equipment_serial"),
    ]:
        row = table.add_row().cells
        row[0].text = label
        row[1].text = ctx[key]

    for heading, key in [
        ("Initial Condition", "initial_condition"),
        ("Investigation", "investigation"),
        ("Outcome", "outcome"),
        ("Follow Up", "follow_up"),
        ("Parts Used", "parts_used"),
    ]:
        document.add_heading(heading, level=2)
        document.add_paragraph(ctx[key])

    document.add_heading("Signatures", level=2)
    document.add_paragraph(f"Engineer: {ctx['engineer_signature_name']}")
    document.add_paragraph(f"Customer: {ctx['customer_signature_name']}")

    document.save(path)
    return path
