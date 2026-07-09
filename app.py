import streamlit as st
import pandas as pd
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Client Renewal Dashboard", layout="wide")

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.card {
    padding: 12px;
    border-radius: 10px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
}
.label {font-size:11px;color:#6b7280;}
.value {font-size:15px;font-weight:600;}
.primary {background:#4f46e5;color:white;}
.success {background:#059669;color:white;}
.primary .label, .primary .value,
.success .label, .success .value {
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("client_renewal_backend_data.xlsx")
df.columns = df.columns.str.strip()

def format_inr(x):
    try:
        return f"₹{int(x):,}"
    except:
        return "₹0"

# -------------------------
# PDF FUNCTION
# -------------------------
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pandas as pd

def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except:
        return 0

def gst_breakup(amount):
    base = int(round(amount / 1.18))
    gst = amount - base
    return base, gst


def generate_pdf_bytes(client_name, entity_type, plan, renewal, offer, tax_audit):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=36, leftMargin=36,
                            topMargin=20, bottomMargin=18)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'title', parent=styles['Title'],
        fontSize=14, textColor=colors.white, alignment=1,
        leading=16
    )

    heading_style = ParagraphStyle(
        'heading', parent=styles['Heading3'],
        fontSize=10.5, textColor=colors.HexColor("#111827"), spaceAfter=2,
        spaceBefore=1, leading=12.5
    )

    normal_style = ParagraphStyle(
        'normal', parent=styles['Normal'],
        fontSize=9.2, leading=12
    )

    watermark_style = ParagraphStyle(
        'watermark',
        parent=styles['Normal'],
        fontSize=28,
        textColor=colors.HexColor("#e5e7eb"),
        alignment=1
    )

    # SAFE VALUES
    renewal = safe_int(renewal)
    offer = safe_int(offer)
    tax_audit = safe_int(tax_audit)

    # GST
    ren_base, ren_gst = gst_breakup(renewal)
    off_base, off_gst = gst_breakup(offer)
    tax_base, tax_gst = gst_breakup(tax_audit)

    one_year_total = renewal + tax_audit
    total_price = one_year_total if plan == "1 Year Plan" else offer

    story = []

    # 🔥 WATERMARK (light)
    story.append(Paragraph("Neusource", watermark_style))
    story.append(Spacer(1, -22))

    # HEADER
    header = Table([[Paragraph("Neusource Startup Minds India Limited", title_style)]], colWidths=[500])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1d4ed8")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(header)
    story.append(Spacer(1, 5))

    # LOGO
    try:
        story.append(Image("logo.png", width=75, height=22))
        story.append(Spacer(1, 4))
    except:
        pass

    # DATE
    story.append(Paragraph(f"Date: {datetime.today().strftime('%d %B %Y')}", normal_style))
    story.append(Spacer(1, 5))

    # INTRO
    story.append(Paragraph("Dear Sir,", normal_style))
    story.append(Paragraph("Hope you are doing well.", normal_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph(
        "As discussed, please find below the proposal for annual statutory compliances for FY 2025–2026.",
        normal_style
    ))

    story.append(Spacer(1, 6))

    # -------------------------
    # BLOCK HELPER (card-style section with colored title bar)
    # -------------------------
    FULL_WIDTH = 523

    box_header_style = ParagraphStyle(
        'box_header', parent=styles['Heading3'],
        fontSize=11, textColor=colors.white, leading=13,
        spaceAfter=0, spaceBefore=0
    )

    def make_box(title, content_flowables, width=FULL_WIDTH, bar_color="#1d4ed8"):
        box_data = [[Paragraph(title, box_header_style)], [content_flowables]]
        box = Table(box_data, colWidths=[width])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bar_color)),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('LEFTPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 6),
            ('LEFTPADDING', (0, 1), (-1, 1), 10),
            ('RIGHTPADDING', (0, 1), (-1, 1), 10),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor(bar_color)),
            ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.HexColor(bar_color)),
        ]))
        return box

    # -------------------------
    # BLOCK 1: CLIENT DETAILS
    # -------------------------
    client_content = [
        Paragraph(f"<b>Client Name:</b> {client_name}", normal_style),
        Spacer(1, 3),
        Paragraph(f"<b>Entity Type:</b> {entity_type}", normal_style),
    ]
    story.append(make_box("Client Details", client_content))
    story.append(Spacer(1, 6))

    # -------------------------
    # BLOCK 2: SCOPE OF WORK
    # -------------------------
    scope_points = [

        "A. Statutory Audit & Financials",

        "Review, Finalization & Statutory Audit of Balance Sheet, Profit & Loss Account and Audit Report (based on books/records shared by the client)",

        "B. ROC Annual Filings",

        "Filing of Form AOC-4 – Financial Statements",

        "Filing of Form MGT-7 / MGT-7A – Annual Return (as applicable)",

        "Filing of Form ADT-1 – Appointment / Re-appointment of Statutory Auditor (if applicable)",

        "Filing of Form DPT-3 – Return of Deposits (if applicable)",

        "C. Income Tax Compliances",

        "Income Tax Return Filing – Company",

        "Income Tax Return Filing – Directors (If Opted)",

        "Tax Audit (if applicable & charged in this proposal)",

        "D. Director & Other Regulatory Compliances",

        "DIR-3 KYC of All Directors"
    ]

    scope_content = []
    for i, p in enumerate(scope_points):
        if p.startswith(("A.", "B.", "C.", "D.")):
            if i != 0:
                scope_content.append(Spacer(1, 2))
            scope_content.append(
                Paragraph(f"<b><font color='#1d4ed8'>{p}</font></b>", heading_style)
            )
        else:
            scope_content.append(Paragraph(f"• {p}", normal_style))

    story.append(make_box("Scope of Work", scope_content))
    story.append(Spacer(1, 6))

    # -------------------------
    # BLOCK 3: FEE STRUCTURE
    # -------------------------
    table_data = [
        ["Particulars", "Base", "GST", "Total"],
        ["1 Year Plan", f"{ren_base:,}", f"{ren_gst:,}", f"{renewal:,}"],
        ["Tax Audit", f"{tax_base:,}", f"{tax_gst:,}", f"{tax_audit:,}"],
        ["★ 2+1 Offer (Recommended)", f"{off_base:,}", f"{off_gst:,}", f"{offer:,}"],
        ["Total Payable", "", "", f"{total_price:,}"]
    ]

    table = Table(table_data, colWidths=[173, 94, 94, 112])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

        # Recommended highlight
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#bbf7d0")),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),

        # Total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    story.append(make_box("Fee Structure", [table]))
    story.append(Spacer(1, 6))

    # -------------------------
    # BLOCK 4: COST COMPARISON
    # -------------------------
    three_year_cost = one_year_total * 3
    per_year = int(offer / 3)
    savings = three_year_cost - offer

    comp_data = [
        ["Particulars", "Amount"],
        ["1 Year Total", f"{one_year_total:,}"],
        ["3 Year Cost (1 Year Plan)", f"{three_year_cost:,}"],
        ["2+1 Offer", f"{offer:,}"],
        ["Per Year Cost (2+1)", f"{per_year:,}"],
        ["🔥 You Save", f"{savings:,}"]
    ]

    comp_table = Table(comp_data, colWidths=[293, 180])

    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#bbf7d0")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    story.append(make_box("Cost Comparison", [comp_table], bar_color="#111827"))
    story.append(Spacer(1, 6))

    # CLOSING
    story.append(Paragraph("We assure you of timely and accurate compliance support.", normal_style))
    story.append(Paragraph("<b>Thank you for being with us.</b>", normal_style))

    doc.build(story)
    buffer.seek(0)

    return buffer
# -------------------------
# CARD
# -------------------------
def card(title, value):
    return f"""
    <div class="card">
        <div class="label">{title}</div>
        <div class="value">{value}</div>
    </div>
    """

# -------------------------
# UI
# -------------------------
st.title("📊 Client Renewal Dashboard")

client_code = st.text_input("Enter Client Code")

# 🔥 IMPORTANT: remove button dependency
if client_code:

    data = df[df["ClientCode"].astype(str) == client_code]

    if data.empty:
        st.error("Client not found ❌")
    else:

        # -------------------------
        # COMPANY DROPDOWN (FIXED)
        # -------------------------
        if len(data) > 1:
            selected_company = st.selectbox(
                "Select Company",
                data["FileName"].unique()
            )
            row = data[data["FileName"] == selected_company].iloc[0]
        else:
            row = data.iloc[0]

        company = row.get("FileName", "Client")

        st.success(company)

        # -------------------------
        # OVERVIEW
        # -------------------------
        c1, c2, c3, c4, c5 = st.columns(5)

        c1.markdown(card("Client Code", row['ClientCode']), unsafe_allow_html=True)
        c2.markdown(card("Company", company), unsafe_allow_html=True)
        c3.markdown(card("Entity", row['Co Type']), unsafe_allow_html=True)
        c4.markdown(card("Turnover 23-24", format_inr(row.get('Turn over 23-24',0))), unsafe_allow_html=True)
        c5.markdown(card("Turnover 24-25", format_inr(row.get('Turn over 24-25',0))), unsafe_allow_html=True)

        # -------------------------
        # FEE SUMMARY
        # -------------------------
        st.subheader("💰 Fee Summary")

        c1, c2, c3 = st.columns(3)

        c1.markdown(card("FY 23-24", format_inr(row.get("Fee 23-24",0))), unsafe_allow_html=True)
        c2.markdown(card("FY 24-25", format_inr(row.get("Fee 24-25",0))), unsafe_allow_html=True)
        c3.markdown(card("Current Total", format_inr(row.get("Total",0))), unsafe_allow_html=True)

        # -------------------------
        # RENEWAL + TAX AUDIT FIX
        # -------------------------
        renewal = 0
        offer = 0

        for col in df.columns:
            if "renewal" in col.lower():
                renewal = row[col]
            if "offer" in col.lower():
                offer = row[col]

        tax_audit_2526 = row.get("Tax Audit 25-26", 0)

        st.subheader("🚀 Renewal Pricing")

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"""
        <div class="card primary">
            <div class="label">1 Year Plan</div>
            <div class="value">{format_inr(renewal)}</div>
        </div>
        """, unsafe_allow_html=True)

        c2.markdown(f"""
        <div class="card success">
            <div class="label">2+1 Offer</div>
            <div class="value">{format_inr(offer)}</div>
        </div>
        """, unsafe_allow_html=True)

        # 🔥 NEW (Tax Audit in renewal section)
        c3.markdown(f"""
<div class="card" style="background:#f59e0b;color:white;">
    <div class="label" style="color:white;">Tax Audit 25-26</div>
    <div class="value">{format_inr(tax_audit_2526)}</div>
</div>
""", unsafe_allow_html=True)

        # -------------------------
        # PDF
        # -------------------------
        st.subheader("📄 Download Proposal")

        col1, col2 = st.columns(2)

        with col1:
            pdf1 = generate_pdf_bytes(
    company,
    row.get("Co Type", ""),
    "1 Year Plan",
    renewal,
    offer,
    tax_audit_2526
)
            st.download_button("⬇️ 1 Year Proposal", pdf1, "proposal_1_year.pdf")

        with col2:
            pdf2 = generate_pdf_bytes(
    company,
    row.get("Co Type", ""),
    "2+1 Offer",
    renewal,
    offer,
    tax_audit_2526
)	
            st.download_button("⬇️ 2+1 Proposal", pdf2, "proposal_2plus1.pdf")
