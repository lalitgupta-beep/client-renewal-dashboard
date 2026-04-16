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
                            rightMargin=30, leftMargin=30,
                            topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'title', parent=styles['Title'],
        fontSize=14, textColor=colors.white, alignment=1
    )

    heading_style = ParagraphStyle(
        'heading', parent=styles['Heading3'],
        fontSize=12, textColor=colors.HexColor("#111827"), spaceAfter=6
    )

    normal_style = ParagraphStyle(
        'normal', parent=styles['Normal'],
        fontSize=10, leading=14
    )

    watermark_style = ParagraphStyle(
        'watermark',
        parent=styles['Normal'],
        fontSize=40,
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
    story.append(Spacer(1, -30))

    # HEADER
    header = Table([[Paragraph("Neusource Startup Minds India Limited", title_style)]], colWidths=[500])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1d4ed8")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(header)
    story.append(Spacer(1, 8))

    # LOGO
    try:
        story.append(Image("logo.png", width=100, height=30))
        story.append(Spacer(1, 6))
    except:
        pass

    # DATE
    story.append(Paragraph(f"Date: {datetime.today().strftime('%d %B %Y')}", normal_style))
    story.append(Spacer(1, 10))

    # INTRO
    story.append(Paragraph("Dear Sir,", normal_style))
    story.append(Paragraph("Hope you are doing well.", normal_style))
    story.append(Spacer(1, 5))

    story.append(Paragraph(
        "As discussed, please find below the proposal for annual statutory compliances for FY 2025–2026.",
        normal_style
    ))

    story.append(Spacer(1, 10))

    # CLIENT
    story.append(Paragraph(f"<b>Client Name:</b> {client_name}", normal_style))
    story.append(Paragraph(f"<b>Entity Type:</b> {entity_type}", normal_style))

    story.append(Spacer(1, 10))

    # SCOPE
    story.append(Paragraph("Scope of Work", heading_style))

    scope_points = [
        "Preparation of Balance Sheet & Profit and Loss Account",
        "Preparation of Audit Report, Director's Report, Extract of Annual Return & Financial Statements",
        "Preparation & filing of Form DPT-3",
        "Preparation & Filing of Form AOC-04",
        "Preparation & Filing of Form MGT-07",
        "Auditor's DSC usage in AOC-04",
        "Preparation of Minutes of Board Meeting",
        "Preparation of Minutes of AGM",
        "Income Tax Return filing (Company)",
        "DIN KYC of Directors",
        "ITR of Directors (if opted)",
        "Tax Audit compliance (if applicable & opted)"
    ]

    for p in scope_points:
        story.append(Paragraph(f"✔ {p}", normal_style))

    story.append(Spacer(1, 10))

    # 🔥 PRICING TABLE
    story.append(Paragraph("Fee Structure", heading_style))

    table_data = [
        ["Particulars", "Base", "GST", "Total"],
        ["1 Year Plan", f"{ren_base:,}", f"{ren_gst:,}", f"{renewal:,}"],
        ["Tax Audit", f"{tax_base:,}", f"{tax_gst:,}", f"{tax_audit:,}"],
        ["★ 2+1 Offer (Recommended)", f"{off_base:,}", f"{off_gst:,}", f"{offer:,}"],
        ["Total Payable", "", "", f"{total_price:,}"]
    ]

    table = Table(table_data, colWidths=[180, 100, 100, 120])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        # Recommended highlight
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#bbf7d0")),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),

        # Total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    story.append(table)

    story.append(Spacer(1, 12))

    # 🔥 COMPARISON
    story.append(Paragraph("Cost Comparison", heading_style))

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

    comp_table = Table(comp_data, colWidths=[300, 150])

    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#bbf7d0")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    story.append(comp_table)

    story.append(Spacer(1, 10))

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
