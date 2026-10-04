import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf(filename):
    # Tight professional margins for a rich 2-page or dense 1-page executive format
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    # Executive Color Palette
    PRIMARY = colors.HexColor("#091e3a")   # Deep Marine Navy
    ACCENT = colors.HexColor("#0284c7")    # Deep Teal / Petroleum Blue
    TEXT_DARK = colors.HexColor("#1e293b") # Slate 800
    TEXT_MUTED = colors.HexColor("#475569")# Slate 600
    LINE_COLOR = colors.HexColor("#cbd5e1")# Slate 300

    name_style = ParagraphStyle(
        'DocName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=PRIMARY,
        spaceAfter=3
    )
    
    tagline_style = ParagraphStyle(
        'DocTagline',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=ACCENT,
        spaceAfter=3
    )

    contact_style = ParagraphStyle(
        'DocContact',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MUTED,
        spaceAfter=8
    )

    section_style = ParagraphStyle(
        'DocSection',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=7,
        spaceAfter=3,
        textTransform='uppercase'
    )

    body_style = ParagraphStyle(
        'DocBody',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_DARK,
        spaceAfter=3
    )

    project_title_style = ParagraphStyle(
        'DocProjTitle',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=TEXT_DARK
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=ACCENT,
        alignment=2 # Right aligned
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        fontName='Helvetica',
        fontSize=8.2,
        leading=11,
        textColor=TEXT_DARK,
        leftIndent=10,
        spaceAfter=2
    )

    story = []

    # Header
    story.append(Paragraph("ERIOLUWA AYODEJI", name_style))
    story.append(Paragraph("PETROLEUM ENGINEER & ENERGY AI SYSTEMS ARCHITECT", tagline_style))
    story.append(Paragraph("Lagos, Nigeria | +234 902 617 0219 | erioluwaayodeji@gmail.com | github.com/ayodejierioluwa", contact_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY, spaceAfter=6))

    # Executive Summary
    story.append(Paragraph("EXECUTIVE PROFILE", section_style))
    summary_text = (
        "Petroleum Engineering graduate (B.Eng., Second-Class Upper) from Covenant University and technical founder "
        "pioneering real-time physics-informed AI systems for upstream drilling dynamics, predictive asset maintenance, and "
        "regulatory digital twins. Founder & Systems Architect of the <b>PetroOne Energy Intelligence Suite</b>, including "
        "<b>Omesham AI</b> (autonomous drilling telemetry & vibration dampening) and <b>GAIA.AI</b>. Combines deep subsurface domain "
        "knowledge with advanced algorithmic engineering across high-frequency SCADA/WITSML streaming, Aspen HYSYS process simulation, "
        "and industrial safety design."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=4, spaceAfter=5))

    # Core Technical Skills
    story.append(Paragraph("TECHNICAL PROFICIENCIES & DOMAIN MASTERY", section_style))
    skills_data = [
        [
            Paragraph("<b>Drilling & Petroleum Engineering:</b>", body_style),
            Paragraph("Downhole Telemetry (WITSML/LAS), Torsional Stick-Slip Mitigation, Rate of Penetration (ROP) & Weight on Bit (WOB) Optimization, BHA Directional Trajectory, Well Intervention, Aspen HYSYS, HAZOP/HAZID, PFDs/P&IDs.", body_style)
        ],
        [
            Paragraph("<b>AI, Systems & Architecture:</b>", body_style),
            Paragraph("Physics-Informed Neural Networks, Python (NumPy, SciPy, Pandas), Real-time Time-Series Analytics, Next.js/React, Micro-frontend SSO Handshakes, Serverless Cloud Architecture, REST/WebSocket APIs, PostgreSQL.", body_style)
        ]
    ]
    t_skills = Table(skills_data, colWidths=[1.9*inch, 5.3*inch])
    t_skills.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_skills)
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=4, spaceAfter=5))

    # Flagship Energy Technology Projects
    story.append(Paragraph("FLAGSHIP ENERGY & AI CREATIONS", section_style))

    # 1. Omesham AI
    p1_head = [
        Paragraph("<b>Omesham AI — Autonomous Physics-Informed Drilling Co-Pilot</b>", project_title_style),
        Paragraph("Lead Architect", meta_style)
    ]
    t_p1 = Table([p1_head], colWidths=[5.4*inch, 1.8*inch])
    t_p1.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_p1)
    story.append(Paragraph("• Engineered an upstream telemetry co-pilot ingesting high-frequency downhole data (WITSML/LAS) across active geothermal and oil basins (Utah FORGE, Permian Basin).", bullet_style))
    story.append(Paragraph("• <b>Torsional Vibration Mitigation:</b> Modeled drillstring wave equations to detect and suppress torsional stick-slip resonance, mitigating destructive lateral vibrations (>3G) and drillstring twist-offs.", bullet_style))
    story.append(Paragraph("• <b>Autonomous State Classification:</b> Built real-time classifiers distinguishing Sliding vs. Rotating vs. Tripping states with live directional BHA toolface azimuth drift tracking.", bullet_style))
    story.append(Paragraph("• <b>Predictive Hydraulics:</b> Developed transient Standpipe Pressure (SPP) models detecting downhole mud-motor micro-stalls and BHA washouts up to 30 minutes before mechanical manifestation.", bullet_style))
    story.append(Paragraph("• Pitched at executive level to independent operators including <b>First E&P (Ademola Adeyemi-Bero)</b> for offshore Niger Delta shallow-water assets.", bullet_style))

    # 2. PetroOne Master Suite
    p2_head = [
        Paragraph("<b>PetroOne Energy Intelligence Suite</b> (PetroSight, GAIA.AI, Petrogenesis 3D)", project_title_style),
        Paragraph("Full-Stack Founder", meta_style)
    ]
    t_p2 = Table([p2_head], colWidths=[5.4*inch, 1.8*inch])
    t_p2.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_p2)
    story.append(Paragraph("• Architected a unified energy micro-frontend suite with orbital single sign-on (SSO) bridging <b>Omesham AI</b>, <b>PetroSight AI</b> (predictive maintenance & asset health), <b>GAIA.AI</b> (upstream lead and field intelligence), and <b>Petrogenesis 3D</b> (subsurface borehole visualization).", bullet_style))
    story.append(Paragraph("• Engineered fault-tolerant telemetry stream handlers managing live operational alarms with zero-latency visual status reporting.", bullet_style))

    # 3. NUPRC Digital Twin
    p3_head = [
        Paragraph("<b>NUPRC Digital Twin & Regulatory Safety Framework</b>", project_title_style),
        Paragraph("Technical Author", meta_style)
    ]
    t_p3 = Table([p3_head], colWidths=[5.4*inch, 1.8*inch])
    t_p3.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_p3)
    story.append(Paragraph("• Designed an enterprise digital twin architecture for regulatory oversight with the <b>Nigerian Upstream Petroleum Regulatory Commission (NUPRC)</b>, focusing on real-time hydrocarbon accounting and offshore safety integrity.", bullet_style))

    # 4. Mindflow AI
    p4_head = [
        Paragraph("<b>Mindflow AI — Voice-First Executive Intelligence Engine</b>", project_title_style),
        Paragraph("Creator", meta_style)
    ]
    t_p4 = Table([p4_head], colWidths=[5.4*inch, 1.8*inch])
    t_p4.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_p4)
    story.append(Paragraph("• Deployed a voice-to-structured-data AI assistant using Groq Whisper (<0.5s audio transcription) and multimodal LLMs for automated task, date, and fiscal expense structuring deployed serverless on Vercel.", bullet_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=4, spaceAfter=5))

    # Professional Engineering Experience
    story.append(Paragraph("PROFESSIONAL INDUSTRY EXPERIENCE", section_style))

    # NETCO
    netco_head = [
        Paragraph("<b>National Engineering & Technical Company (NETCO - NNPC Subsidiary)</b>", project_title_style),
        Paragraph("Mar 2024 – Sept 2024", meta_style)
    ]
    t_netco = Table([netco_head], colWidths=[5.4*inch, 1.8*inch])
    t_netco.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_netco)
    story.append(Paragraph("<i>Engineering Intern — Process & Upstream Facility Engineering</i>", body_style))
    story.append(Paragraph("• Performed process simulations in Aspen HYSYS for real-world oil and gas upstream production and gas treatment facilities.", bullet_style))
    story.append(Paragraph("• Contributed to commercial Hazard Identification (HAZID) and Hazard and Operability (HAZOP) studies for facility debottlenecking.", bullet_style))
    story.append(Paragraph("• Developed practical exposure to well intervention procedures, including coiled tubing operations, cementing, and high-pressure nitrogen purging.", bullet_style))

    # Tomesy
    tomesy_head = [
        Paragraph("<b>Tomesy Engineering Nigeria Limited</b>", project_title_style),
        Paragraph("Jul 2023 – Aug 2023", meta_style)
    ]
    t_tomesy = Table([tomesy_head], colWidths=[5.4*inch, 1.8*inch])
    t_tomesy.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_tomesy)
    story.append(Paragraph("<i>Engineering Intern — Process Plant Systems</i>", body_style))
    story.append(Paragraph("• Drafted industrial Process Flow Diagrams (PFDs) and assisted with engineering risk analysis conforming to HSE standards.", bullet_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=4, spaceAfter=5))

    # Education, Honors & Certifications
    story.append(Paragraph("EDUCATION & PROFESSIONAL AFFILIATIONS", section_style))
    edu_head = [
        Paragraph("<b>Covenant University, Ota, Nigeria</b> — <i>B.Eng., Petroleum Engineering</i>", project_title_style),
        Paragraph("2020 – 2025", meta_style)
    ]
    t_edu = Table([edu_head], colWidths=[5.4*inch, 1.8*inch])
    t_edu.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_edu)
    story.append(Paragraph("• <b>Academic Distinction:</b> Graduated Second-Class Honours (Upper Division).", bullet_style))
    story.append(Paragraph("• <b>Leadership:</b> Assistant Membership Lead, Society of Petroleum Engineers (SPE), Covenant University (2024 – 2025).", bullet_style))
    story.append(Paragraph("• <b>Certifications:</b> Aspen HYSYS Process Simulation, Data Analysis with Python (DataCamp), HSE Level 1 & 2.", bullet_style))

    doc.build(story)

if __name__ == "__main__":
    out_dir = "/Users/macbook/Desktop"
    out_file = os.path.join(out_dir, "Erioluwa_Ayodeji_Executive_CV.pdf")
    generate_pdf(out_file)
    print("SUCCESS_UPDATED:", out_file)
