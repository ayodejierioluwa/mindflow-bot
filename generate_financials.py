import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_financials(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    PRIMARY = colors.HexColor("#091e3a")   # Marine Navy
    ACCENT = colors.HexColor("#0284c7")    # Energy Blue
    TEXT_DARK = colors.HexColor("#1e293b") # Slate 800
    TEXT_MUTED = colors.HexColor("#64748b")
    LINE_COLOR = colors.HexColor("#cbd5e1")
    BG_HEADER = colors.HexColor("#f1f5f9")

    title_style = ParagraphStyle(
        'FinTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'FinSub',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=ACCENT,
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'FinMeta',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MUTED,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        'FinSection',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        textTransform='uppercase'
    )

    body_style = ParagraphStyle(
        'FinBody',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    tbl_head = ParagraphStyle('TblHead', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=PRIMARY, alignment=1)
    tbl_cell = ParagraphStyle('TblCell', fontName='Helvetica', fontSize=8, leading=10, textColor=TEXT_DARK, alignment=1)
    tbl_cell_bold = ParagraphStyle('TblCellB', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=TEXT_DARK, alignment=1)
    tbl_cell_left = ParagraphStyle('TblCellL', fontName='Helvetica', fontSize=8, leading=10, textColor=TEXT_DARK)
    tbl_cell_left_bold = ParagraphStyle('TblCellLB', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=PRIMARY)

    story = []

    # Title Banner
    story.append(Paragraph("PETROONE INC. — OMESHAM AI", title_style))
    story.append(Paragraph("HISTORICAL & 3-YEAR PROJECTED FINANCIAL STATEMENT (2026 – 2028)", subtitle_style))
    story.append(Paragraph("Currency: USD ($) | Target Market: Qatar, GCC & West Africa | Prepared for Qatar Startup Program", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    # Executive Overview
    story.append(Paragraph("EXECUTIVE SUMMARY & UNIT ECONOMICS", section_style))
    summary_text = (
        "PetroOne monetizes via a high-margin enterprise SaaS model billed per active drilling rig ($18,000/rig/month average contract value) "
        "and multi-asset enterprise licenses ($350,000 – $600,000/year for national oil companies). With cloud telemetry processing and "
        "reusable algorithmic modules, gross software margins exceed 82%. Break-even is achieved in Year 2 at 18 active monitored rigs."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=4, spaceAfter=8))

    # Financial Table
    story.append(Paragraph("3-YEAR INCOME STATEMENT & OPERATIONAL PROJECTIONS", section_style))

    table_data = [
        [Paragraph("<b>METRIC (USD)</b>", tbl_head), Paragraph("<b>2025 (Hist)</b>", tbl_head), Paragraph("<b>2026 (Y1 Proj)</b>", tbl_head), Paragraph("<b>2027 (Y2 Proj)</b>", tbl_head), Paragraph("<b>2028 (Y3 Proj)</b>", tbl_head)],
        [Paragraph("Active Commercial Rigs Monitored", tbl_cell_left), Paragraph("0 (Pilot)", tbl_cell), Paragraph("6", tbl_cell), Paragraph("22", tbl_cell), Paragraph("55", tbl_cell)],
        [Paragraph("Enterprise Fleet Operator Licenses", tbl_cell_left), Paragraph("0", tbl_cell), Paragraph("1", tbl_cell), Paragraph("3", tbl_cell), Paragraph("7", tbl_cell)],
        [Paragraph("<b>GROSS REVENUE</b>", tbl_cell_left_bold), Paragraph("<b>$0</b>", tbl_cell_bold), Paragraph("<b>$648,000</b>", tbl_cell_bold), Paragraph("<b>$2,450,000</b>", tbl_cell_bold), Paragraph("<b>$6,850,000</b>", tbl_cell_bold)],
        [Paragraph("   • Rig Telemetry Subscriptions", tbl_cell_left), Paragraph("$0", tbl_cell), Paragraph("$498,000", tbl_cell), Paragraph("$1,700,000", tbl_cell), Paragraph("$4,650,000", tbl_cell)],
        [Paragraph("   • Enterprise Custom Integrations", tbl_cell_left), Paragraph("$0", tbl_cell), Paragraph("$150,000", tbl_cell), Paragraph("$750,000", tbl_cell), Paragraph("$2,200,000", tbl_cell)],
        [Paragraph("Cost of Goods Sold (Cloud/Compute/WITSML)", tbl_cell_left), Paragraph("$12,000", tbl_cell), Paragraph("$95,000", tbl_cell), Paragraph("$340,000", tbl_cell), Paragraph("$890,000", tbl_cell)],
        [Paragraph("<b>GROSS PROFIT</b>", tbl_cell_left_bold), Paragraph("<b>-$12,000</b>", tbl_cell_bold), Paragraph("<b>$553,000 (85%)</b>", tbl_cell_bold), Paragraph("<b>$2,110,000 (86%)</b>", tbl_cell_bold), Paragraph("<b>$5,960,000 (87%)</b>", tbl_cell_bold)],
        [Paragraph("<b>OPERATING EXPENSES (OPEX)</b>", tbl_cell_left_bold), Paragraph("<b>$35,000</b>", tbl_cell_bold), Paragraph("<b>$490,000</b>", tbl_cell_bold), Paragraph("<b>$1,380,000</b>", tbl_cell_bold), Paragraph("<b>$2,850,000</b>", tbl_cell_bold)],
        [Paragraph("   • Engineering & R&D Talent (Qatar & Remote)", tbl_cell_left), Paragraph("$25,000", tbl_cell), Paragraph("$280,000", tbl_cell), Paragraph("$750,000", tbl_cell), Paragraph("$1,450,000", tbl_cell)],
        [Paragraph("   • Business Development & Regional Sales", tbl_cell_left), Paragraph("$5,000", tbl_cell), Paragraph("$110,000", tbl_cell), Paragraph("$380,000", tbl_cell), Paragraph("$800,000", tbl_cell)],
        [Paragraph("   • Qatar Office, QSTP Legal, Compliance", tbl_cell_left), Paragraph("$5,000", tbl_cell), Paragraph("$100,000", tbl_cell), Paragraph("$250,000", tbl_cell), Paragraph("$600,000", tbl_cell)],
        [Paragraph("<b>EBITDA / OPERATING INCOME</b>", tbl_cell_left_bold), Paragraph("<b>-$47,000</b>", tbl_cell_bold), Paragraph("<b>$63,000</b>", tbl_cell_bold), Paragraph("<b>$730,000</b>", tbl_cell_bold), Paragraph("<b>$3,110,000</b>", tbl_cell_bold)],
        [Paragraph("Tax (Qatar Corporate Tax 10% / Exemptions)", tbl_cell_left), Paragraph("$0", tbl_cell), Paragraph("$6,300", tbl_cell), Paragraph("$73,000", tbl_cell), Paragraph("$311,000", tbl_cell)],
        [Paragraph("<b>NET PROFIT</b>", tbl_cell_left_bold), Paragraph("<b>-$47,000</b>", tbl_cell_bold), Paragraph("<b>$56,700</b>", tbl_cell_bold), Paragraph("<b>$657,000</b>", tbl_cell_bold), Paragraph("<b>$2,799,000</b>", tbl_cell_bold)],
    ]

    t_fin = Table(table_data, colWidths=[2.8*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor("#f0fdf4")), # Light green for gross profit
        ('BACKGROUND', (0,14), (-1,14), colors.HexColor("#eff6ff")), # Light blue for net profit
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 10))

    # Assumptions & Use of Funds
    story.append(Paragraph("STRATEGIC ASSUMPTIONS & USE OF FUNDS", section_style))
    assumptions_text = (
        "• <b>Contract Pricing:</b> Base rig rate calculated at $18,000/rig/month; enterprise multi-well NOC licenses range from $250k–$600k/yr.<br/>"
        "• <b>Target Deployment:</b> Initial 6 rigs deployed across Qatari offshore gas wells and West African independent operators.<br/>"
        "• <b>Use of Seed Capital ($500k – $1M target):</b> 50% for core Qatari engineering & downhole physics hires; 30% for local business development & QatarEnergy/QSTP pilot testing; 20% for WITSML streaming server infrastructure & compliance."
    )
    story.append(Paragraph(assumptions_text, body_style))

    doc.build(story)

if __name__ == "__main__":
    out_file = "/Users/macbook/Desktop/PetroOne_Omesham_Historical_Projected_Financials.pdf"
    generate_financials(out_file)
    print("FINANCIALS_SUCCESS:", out_file)
