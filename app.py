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
def generate_pdf_bytes(client_name, plan, renewal, offer):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    price = renewal if plan == "1 Year Plan" else offer
    price = int(price) if price else 0

    story = []

    story.append(Paragraph("<b>NeuSource Systems</b>", styles['Title']))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Dear Sir,", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Hope you are doing well.", styles['Normal']))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "As discussed, please find below the proposal for annual statutory compliances for the financial year 2024–2025.",
        styles['Normal']
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Scope of Work:</b>", styles['Heading3']))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "• Balance Sheet & P&L<br/>"
        "• ROC Filings<br/>"
        "• ITR Filing<br/>"
        "• DIN KYC<br/>"
        "• Tax Audit",
        styles['Normal']
    ))

    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Fee Structure:</b>", styles['Heading3']))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"<b>{plan}</b>", styles['Normal']))
    story.append(Paragraph(f"Total Payable: ₹{price:,}", styles['Normal']))

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
            pdf1 = generate_pdf_bytes(company, "1 Year Plan", renewal, offer)
            st.download_button("⬇️ 1 Year Proposal", pdf1, "proposal_1_year.pdf")

        with col2:
            pdf2 = generate_pdf_bytes(company, "2+1 Offer", renewal, offer)
            st.download_button("⬇️ 2+1 Proposal", pdf2, "proposal_2plus1.pdf")
