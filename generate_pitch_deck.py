import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_rich_deck(filename):
    # Widescreen Presentation Canvas (11 x 8.5 inches landscape)
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()
    PRIMARY = colors.HexColor("#07182c")    # Deep Oilfield Navy
    ACCENT = colors.HexColor("#0284c7")     # Petroleum Electric Blue
    ACCENT_LIGHT = colors.HexColor("#e0f2fe")
    GOLD = colors.HexColor("#b45309")       # Amber Gold
    TEXT_DARK = colors.HexColor("#0f172a")  # Slate 900
    TEXT_MUTED = colors.HexColor("#475569") # Slate 600
    BG_CARD = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")
    SUCCESS_BG = colors.HexColor("#f0fdf4")
    SUCCESS_BORDER = colors.HexColor("#86efac")

    slide_cat = ParagraphStyle('SCat', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=ACCENT, spaceAfter=2, textTransform='uppercase')
    slide_title = ParagraphStyle('STitle', fontName='Helvetica-Bold', fontSize=21, leading=25, textColor=PRIMARY, spaceAfter=8)
    
    card_h = ParagraphStyle('CardH', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=PRIMARY, spaceAfter=4)
    card_b = ParagraphStyle('CardB', fontName='Helvetica', fontSize=8.5, leading=12, textColor=TEXT_DARK)
    
    stat_num = ParagraphStyle('StatNum', fontName='Helvetica-Bold', fontSize=20, leading=22, textColor=ACCENT, alignment=1)
    stat_label = ParagraphStyle('StatLbl', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=TEXT_MUTED, alignment=1)

    bullet_p = ParagraphStyle('BP', fontName='Helvetica', fontSize=9, leading=13, textColor=TEXT_DARK, leftIndent=8, spaceAfter=3)

    story = []

    def make_kpi(num, label, width=2.4*inch):
        content = [Paragraph(num, stat_num), Spacer(1, 2), Paragraph(label, stat_label)]
        t = Table([[content]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, ACCENT),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    def make_box(title, text, width=4.8*inch, bg=BG_CARD, border=BORDER_COLOR):
        content = [Paragraph(f"<b>{title}</b>", card_h), Paragraph(text, card_b)]
        t = Table([[content]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1, border),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    # ========================================================
    # SLIDE 1: COVER (Executive & High-Impact)
    # ========================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("PETROONE INC. &bull; UPSTREAM DRILLING DEEP-TECH", slide_cat))
    story.append(Paragraph("OMESHAM AI", ParagraphStyle('CovBig', fontName='Helvetica-Bold', fontSize=34, leading=38, textColor=PRIMARY)))
    story.append(Paragraph("Autonomous Physics-Informed Drilling Intelligence & Real-Time Downhole Telemetry Optimization", ParagraphStyle('CovSub1', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=ACCENT)))
    story.append(Paragraph("Mitigating Non-Productive Time (NPT), Torsional Stick-Slip, and Equipment Catastrophes for Offshore & Deep Gas Formations", ParagraphStyle('CovSub2', fontName='Helvetica', fontSize=11, leading=15, textColor=TEXT_MUTED)))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=12, spaceAfter=14))

    # 4 Quick KPIs on Cover
    k1 = make_kpi("$40B+", "Annual Industry NPT Loss", 2.35*inch)
    k2 = make_kpi("< 1 sec", "Live Telemetry Tele-Solve", 2.35*inch)
    k3 = make_kpi("30 Mins", "Early Washout Warning", 2.35*inch)
    k4 = make_kpi("85%+", "Software Gross Margin", 2.35*inch)
    t_cov_kpi = Table([[k1, k2, k3, k4]], colWidths=[2.48*inch, 2.48*inch, 2.48*inch, 2.48*inch])
    t_cov_kpi.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_cov_kpi)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Founder & Systems Architect:</b> Erioluwa Ayodeji &bull; B.Eng. Petroleum Engineering, Covenant University (Second-Class Upper)", ParagraphStyle('CM1', fontName='Helvetica', fontSize=9.5, leading=13, textColor=TEXT_DARK)))
    story.append(Paragraph("<b>Confidential Briefing:</b> Prepared for the Qatar Startup Program, QSTP & Regional Energy Operators (2026)", ParagraphStyle('CM2', fontName='Helvetica', fontSize=9, leading=12, textColor=TEXT_MUTED)))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 2: THE PROBLEM (DENSE TECHNICAL ANALYSIS)
    # ========================================================
    story.append(Paragraph("CRITICAL UPSTREAM PAIN POINT", slide_cat))
    story.append(Paragraph("The $40B Dilemma: Non-Productive Time (NPT) in Deep Drilling", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    p1 = make_box(
        "1. Catastrophic Torsional Stick-Slip",
        "Deep directional drilling experiences severe friction downhole. The bit freezes while the surface top drive keeps rotating, storing immense elastic energy in the drillpipe. When released, the bit spins at <b>3-5x surface RPM</b>, triggering destructive lateral shocks (<b>>3G</b>) that shatter PDC cutters, destroy downhole MWD/LWD tools, or twist the pipe completely in two ($1M–$5M per twist-off).",
        width=4.8*inch
    )
    p2 = make_box(
        "2. Costly Blind Steering in Interbedded Formations",
        "Steering through complex interbedded shale-sand sequences requires balancing 'Rotating' (fast straight-ahead) and 'Sliding' (directional motor steering) modes. Drillers manually infer downhole toolface orientation with substantial logging latency, causing wellbore tortuosity, dogleg severity spikes, and trajectory overshoot.",
        width=4.8*inch
    )
    t_p_row1 = Table([[p1, p2]], colWidths=[5.0*inch, 5.0*inch])
    t_p_row1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_p_row1)
    story.append(Spacer(1, 8))

    p3 = make_box(
        "3. Sudden Mud-Motor Stalls & Washouts",
        "Overloading downhole bits causes mud-motors to stall instantly under high flow rates, blowing seals and hydro-fracturing the formation. Meanwhile, high-pressure erosive drilling mud generates micro-cracks in drill collars (washouts) that go undetected until catastrophic loss of pressure occurs mid-drill.",
        width=4.8*inch
    )
    p4 = make_box(
        "4. Proprietary Legacy Lock-In (SLB, Baker, Nabors)",
        "Legacy oilfield service giants bundle software inside rigid multi-million-dollar hardware contracts. Operators are handcuffed to vendor-specific downhole tools and cannot run real-time physics algorithms across multi-contractor rig fleets.",
        width=4.8*inch
    )
    t_p_row2 = Table([[p3, p4]], colWidths=[5.0*inch, 5.0*inch])
    t_p_row2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_p_row2)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 3: THE SOLUTION (OMESHAM AI DEEP ENGINE)
    # ========================================================
    story.append(Paragraph("THE PROPRIETARY SOLUTION", slide_cat))
    story.append(Paragraph("Omesham AI: Physics-Informed Real-Time Drilling Co-Pilot", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))
    story.append(Paragraph("Omesham AI bridges raw WITSML/LAS rig telemetry with analytical downhole physics to predict hazards <i>before</i> mechanical failure occurs:", ParagraphStyle('SubDesc', fontName='Helvetica', fontSize=9.5, leading=13, textColor=TEXT_DARK, spaceAfter=8)))

    s1 = make_box(
        "⚡ Torsional Wave Damping",
        "Ingests surface RPM, Torque, and Hookload at 1–10Hz, solving the 1D drillstring wave equation in real time. Predicts torsional resonance before stick-slip cycles mature and computes dynamic WOB/RPM boundaries to actively damp vibrations.",
        width=3.15*inch, bg=SUCCESS_BG, border=SUCCESS_BORDER
    )
    s2 = make_box(
        "🧭 Autonomous State & Toolface",
        "Machine-learning classifier that autonomously distinguishes Rotating, Sliding, and Tripping states. Continuously tracks downhole toolface orientation, steering azimuth drift, and dogleg severity without human logging lag.",
        width=3.15*inch, bg=SUCCESS_BG, border=SUCCESS_BORDER
    )
    s3 = make_box(
        "🔍 Transient Washout Solver",
        "Monitors Standpipe Pressure (SPP) against transient hydraulic physics models. Detects high-frequency micro-leak pressure drop signatures and fluid impedance spikes <b>30 minutes in advance</b>, alerting mud teams before pipe parting.",
        width=3.15*inch, bg=SUCCESS_BG, border=SUCCESS_BORDER
    )
    t_sol = Table([[s1, s2, s3]], colWidths=[3.33*inch, 3.33*inch, 3.33*inch])
    t_sol.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_sol)
    story.append(Spacer(1, 10))

    # Field Validation Proof Box
    val_content = [
        Paragraph("<b>Basin Validation & Telemetry Testing:</b>", card_h),
        Paragraph("• Validated on high-temperature, hard-rock downhole telemetry from the <b>Utah FORGE Geothermal Project</b> and deep horizontal wells in the <b>Permian Basin</b>.<br/>"
                  "• Pitched at executive level to <b>First E&P (Ademola Adeyemi-Bero)</b> for offshore Niger Delta shallow-water fields (Anyala-Maduan) to mitigate marine wave-induced WOB vibrations.", card_b)
    ]
    t_val = Table([[val_content]], colWidths=[9.8*inch])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_val)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 4: MASTER ARCHITECTURE & SUITE
    # ========================================================
    story.append(Paragraph("SYSTEMS INTEGRATION", slide_cat))
    story.append(Paragraph("PetroOne Master Suite: Modular Upstream Micro-Frontends", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    arch_box1 = make_box(
        "Omesham AI — Drilling Dynamics",
        "• Real-time ROP, WOB, and Torsional dynamics.<br/>• Automated stick-slip optimization boundaries.<br/>• BHA 3D schematic and trajectory tracking.",
        width=4.8*inch
    )
    arch_box2 = make_box(
        "PetroSight AI — Predictive Maintenance",
        "• Early fault detection for top drives & mud pumps.<br/>• Vibration anomaly alarms & equipment health indices.<br/>• Real-time operational downtime forecasting.",
        width=4.8*inch
    )
    t_arch1 = Table([[arch_box1, arch_box2]], colWidths=[5.0*inch, 5.0*inch])
    t_arch1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_arch1)
    story.append(Spacer(1, 8))

    arch_box3 = make_box(
        "GAIA.AI — Petroleum Field Intelligence",
        "• Automated upstream asset benchmarking.<br/>• Global market analytics & operator intelligence.<br/>• Executive reporting and telemetry logging.",
        width=4.8*inch
    )
    arch_box4 = make_box(
        "Petrogenesis 3D & NUPRC Digital Twin",
        "• 3D borehole trajectory visualization in real time.<br/>• Regulatory compliance digital twin framework.<br/>• Hydrocarbon accounting and offshore asset integrity.",
        width=4.8*inch
    )
    t_arch2 = Table([[arch_box3, arch_box4]], colWidths=[5.0*inch, 5.0*inch])
    t_arch2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_arch2)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 5: MARKET OPPORTUNITY & BUSINESS MODEL
    # ========================================================
    story.append(Paragraph("BUSINESS MODEL & MARKET DYNAMICS", slide_cat))
    story.append(Paragraph("High-Margin Enterprise SaaS Built for Oilfield Scale", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    # Market Sizing Grid
    m1 = make_box("TAM: $45 Billion", "Total Addressable Market for Digital Oilfield, Drilling Automation, and Subsurface Analytics worldwide.", width=3.15*inch)
    m2 = make_box("SAM: $9.2 Billion", "Serviceable Market for Upstream Drilling Optimization Software across Middle East, GCC, and Africa.", width=3.15*inch)
    m3 = make_box("SOM: $180 Million", "Initial Serviceable Obtainable Market: 800+ active offshore and gas rigs across Qatar, UAE, and West Africa.", width=3.15*inch)
    t_m = Table([[m1, m2, m3]], colWidths=[3.33*inch, 3.33*inch, 3.33*inch])
    t_m.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_m)
    story.append(Spacer(1, 10))

    bm_content = [
        Paragraph("<b>Monetization Architecture & Unit Economics:</b>", card_h),
        Paragraph("• <b>Tier 1 — Operator Rig SaaS:</b> $18,000 / active rig / month for continuous real-time WITSML telemetry streaming, vibration mitigation, and hydraulics.<br/>"
                  "• <b>Tier 2 — Enterprise Fleet License:</b> $350,000 – $600,000 / year for national oil companies (NOCs) and supermajors across multi-well campaigns.<br/>"
                  "• <b>Gross Software Margins:</b> <b>85%+</b> driven by lightweight serverless event-driven architecture and automated WITSML parsing.<br/>"
                  "• <b>Break-Even Threshold:</b> Reached at <b>18 active monitored rigs</b> (Year 2 projected EBITDA: $730,000).", card_b)
    ]
    t_bm = Table([[bm_content]], colWidths=[9.8*inch])
    t_bm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_bm)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 6: THE QATAR STRATEGIC FIT
    # ========================================================
    story.append(Paragraph("STRATEGIC REGIONAL EXPANSION", slide_cat))
    story.append(Paragraph("Why Qatar? Powering the North Field Expansion", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    q1 = make_box(
        "1. Active Offshore Field Pilots (QatarEnergy)",
        "Qatar's $30B+ North Field East & South expansion requires drilling hundreds of complex offshore gas wells through abrasive, high-pressure Khuff formations. Omesham AI offers QatarEnergy and its EPC/drilling partners zero-risk historical shadow trials to validate 15–20% NPT reduction.",
        width=4.8*inch
    )
    q2 = make_box(
        "2. Academic & R&D Excellence (QSTP & TAMUQ)",
        "Synergy with Texas A&M University at Qatar (TAMUQ) and Qatar Science & Technology Park (QSTP) to co-develop physics-informed algorithms specialized in Khuff gas reservoir dynamics and extreme HPHT drilling environments.",
        width=4.8*inch
    )
    t_q1 = Table([[q1, q2]], colWidths=[5.0*inch, 5.0*inch])
    t_q1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_q1)
    story.append(Spacer(1, 8))

    q3 = make_box(
        "3. Local Entity & Qatari Talent Hiring",
        "Commitment to incorporate a permanent legal entity in Doha (via QSTP or QFC), establishing a local operational headquarters and hiring Qatari petroleum data engineers, telemetry analysts, and regional account managers.",
        width=4.8*inch
    )
    q4 = make_box(
        "4. Qatar National Vision 2030 Alignment",
        "Directly advances Qatar's transition into an advanced, knowledge-based economy by developing indigenous energy AI intellectual property and slashing rig fuel emissions via accelerated Rate of Penetration.",
        width=4.8*inch
    )
    t_q2 = Table([[q3, q4]], colWidths=[5.0*inch, 5.0*inch])
    t_q2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_q2)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 7: ROADMAP, ASK & CONTACT
    # ========================================================
    story.append(Paragraph("GROWTH ROADMAP & CAPITAL DEPLOYMENT", slide_cat))
    story.append(Paragraph("Milestones, Accelerator Seed Ask & Contact", slide_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    road_content = [
        Paragraph("<b>Execution Roadmap (2026 – 2028):</b>", card_h),
        Paragraph("• <b>Phase 1 (Months 1–6):</b> Legal incorporation in Qatar (QSTP/QFC), local team hiring (2 engineers), and historical shadow trials on past QatarEnergy well logs.<br/>"
                  "• <b>Phase 2 (Months 7–12):</b> Commercial live pilot on 6 active offshore rigs; validation of zero twist-offs and stick-slip damping.<br/>"
                  "• <b>Phase 3 (Months 13–24):</b> Scale to 22+ rigs across Qatar and GCC; commercial enterprise NOC integrations and SOC-2/rig cybersecurity certification.<br/>"
                  "• <b>Phase 4 (Months 25–36):</b> Full commercialization across 55+ rigs globally ($6.85M ARR projected).", card_b)
    ]
    t_road = Table([[road_content]], colWidths=[9.8*inch])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 10))

    ask_content = [
        Paragraph("<b>Seed Investment Ask: $500,000 – $750,000</b>", ParagraphStyle('AskT', fontName='Helvetica-Bold', fontSize=11, textColor=PRIMARY)),
        Paragraph("<b>Use of Capital:</b> 50% Local Qatari Engineering & Downhole AI Talent &bull; 30% Field Pilot Hardware & QatarEnergy Integration &bull; 20% Regulatory, QSTP Office & Cyber Compliance.", card_b)
    ]
    t_ask = Table([[ask_content]], colWidths=[9.8*inch])
    t_ask.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SUCCESS_BG),
        ('BOX', (0,0), (-1,-1), 1.5, SUCCESS_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_ask)
    story.append(Spacer(1, 10))

    # Contact Box
    contact_cells = [
        Paragraph("<b>ERIOLUWA AYODEJI</b> &bull; Founder & Systems Architect &bull; Covenant University B.Eng. Petroleum Engineering", ParagraphStyle('CC1', fontName='Helvetica-Bold', fontSize=9, textColor=PRIMARY, alignment=1)),
        Paragraph("Email: <b>erioluwaayodeji@gmail.com</b> &bull; Phone: <b>+234 902 617 0219</b> &bull; GitHub: <b>github.com/ayodejierioluwa/PETRO.ONE</b>", ParagraphStyle('CC2', fontName='Helvetica', fontSize=8.5, textColor=ACCENT, alignment=1))
    ]
    t_cont = Table([[contact_cells]], colWidths=[9.8*inch])
    t_cont.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cont)

    doc.build(story)

if __name__ == "__main__":
    out_deck = "/Users/macbook/Desktop/PetroOne_Omesham_Pitch_Deck.pdf"
    create_rich_deck(out_deck)
    print("RICH_DECK_SUCCESS:", out_deck)
