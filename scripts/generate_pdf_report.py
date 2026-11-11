"""Generate publication-ready PDF Technical Report for Team 'Mama Doain Aku Sukses Ya'."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "outputs", "Mama_Doain_Aku_Sukses_Ya.pdf")


def build_pdf():
    """Compile the Technical Report PDF deliverable matching SUBMISSION.md requirements."""
    os.makedirs(os.path.dirname(PDF_OUTPUT_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    dark_neutral = colors.HexColor("#2D3748")
    light_bg = colors.HexColor("#EDF2F7")

    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=18, leading=22, textColor=primary_color, alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10.5, leading=14, textColor=secondary_color, alignment=1,
    )
    meta_style = ParagraphStyle(
        "DocMeta", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=12, textColor=dark_neutral, alignment=1,
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=12, leading=16, textColor=primary_color, spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=12, textColor=dark_neutral, spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=12, textColor=dark_neutral, leftIndent=14, spaceAfter=3,
    )
    table_cell = ParagraphStyle(
        "TableCell", parent=styles["Normal"], fontName="Helvetica",
        fontSize=7.5, leading=10, textColor=dark_neutral,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=7.5, leading=10, textColor=primary_color,
    )

    story = []

    # Header Banner
    story.append(Paragraph("MORE THAN A HACK 2027 - PHASE 1: BALL POSSESSION", subtitle_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Technical Report: Physics-Informed Possession Pipeline", title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>Team:</b> Mama Doain Aku Sukses Ya (Mama_Doain_Aku_Sukses_Ya) &nbsp;|&nbsp; "
        "<b>Match:</b> FC Barcelona vs Athletic Club (BAR-ATH)",
        meta_style,
    ))
    story.append(Paragraph(
        "<b>Members (3-5):</b> [Fill 3-5 Registered Members] &nbsp;|&nbsp; "
        "<b>Repo URL:</b> [Fill Public GitHub URL]",
        meta_style,
    ))
    story.append(Paragraph(
        "<b>Deliverable CSV:</b> outputs/Mama_Doain_Aku_Sukses_Ya.csv &nbsp;|&nbsp; "
        "<b>SHA-256:</b> 59f0cff74f3fa39df74c9bae3f724c9d9ef3d4dc8f3ebdb695e0d9ba6190a914",
        meta_style,
    ))
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=6))

    # Section 1: Approach
    story.append(Paragraph("1. Approach and Architecture Rationale", h1_style))
    story.append(Paragraph(
        "Independent frame-by-frame predictors produce severe high-frequency chatter between H, A, and D, fragmenting real spells and heavily penalizing temporal IoU (spellF1). Furthermore, competition rules forbid training or tuning on the provided BAR-ATH video or ground truth. We therefore built a 100% deterministic, zero-training-on-match algorithmic architecture combining geometry, kinematics, Kalman/RTS fusion, and global HMM decoding:",
        body_style,
    ))
    story.append(Paragraph("• <b>Multi-Sensor Ball Fusion:</b> 2D Constant-Velocity Kalman Filter fusing tactical ATD coordinates with classical Morphological Top-Hat CV candidates inside homography-projected 256x256 px ROIs (active missing-ATD segments), smoothed per half via RTS backward recursion (54.6% fused ball coverage).", bullet_style))
    story.append(Paragraph("• <b>Feature Engine &amp; Smart Tagging Polarity:</b> Metric ball-to-player distances, pitch boundary margins (105.3 x 68.0 m), collective player walking/speed profiles, and 638 SportsCode priors with corrected offensive/defensive polarity.", bullet_style))
    story.append(Paragraph("• <b>Intelligent Dead-Ball Engine (D):</b> Integrates pitch exits (margin &gt; 0.0 m), collective player stillness (mean speed &lt; 1.35 m/s, walking &gt; 65%), pre-kickoff half separation (&gt;= 0.80), goal windows, and sprint suppression (-5.0 when speed &gt;= 1.8 m/s).", bullet_style))
    story.append(Paragraph("• <b>Controlled Possession &amp; HMM Viterbi:</b> Combines exponential proximity decay exp(-d/2.5)*4.0, anti-deflection dwell filtering (25 frames / 1.0 s), loose-ball persistence (35 frames / 1.4 s), per-half log-space 3-State Viterbi (P_stay = 0.996), and a 60-frame majority regularizer.", bullet_style))
    story.append(Spacer(1, 3))

    # Section 2: Assets Used & Dropped
    story.append(Paragraph("2. Match Assets Used and Dropped", h1_style))
    asset_data = [
        [Paragraph("<b>Asset</b>", table_cell_bold), Paragraph("<b>File Name</b>", table_cell_bold), Paragraph("<b>Status</b>", table_cell_bold), Paragraph("<b>Role / Justification</b>", table_cell_bold)],
        [Paragraph("Tactical ATD Raw", table_cell), Paragraph("BAR-ATH_tactical_atd.txt", table_cell), Paragraph("Used", table_cell), Paragraph("199,319 frames (vf = frame_id - 1) across 46 slots; ball visible 56.9%; scaled 105.3 x 68.0 m.", table_cell)],
        [Paragraph("Tactical ATD Meta", table_cell), Paragraph("BAR-ATH_tactical_atd.xml", table_cell), Paragraph("Used", table_cell), Paragraph("EPTS metadata mapping each track slot to Barcelona (H) or Atletic Club (A).", table_cell)],
        [Paragraph("Tactical Homography", table_cell), Paragraph("BAR-ATH_tactical_homography.csv", table_cell), Paragraph("Used", table_cell), Paragraph("199,319 3x3 projective matrices (mean reproj err 0.42 px) for pitch-pixel conversions.", table_cell)],
        [Paragraph("Smart Tagging", table_cell), Paragraph("BAR-ATH_tactical_smart_tagging.xml", table_cell), Paragraph("Used", table_cell), Paragraph("638 SportsCode intervals mapped to directional priors (weight 1.2) and set-piece/goal context.", table_cell)],
        [Paragraph("Tactical Video", table_cell), Paragraph("BAR-ATH_tactical.mp4", table_cell), Paragraph("Used", table_cell), Paragraph("1080p 25 FPS chunk-decoded in-memory (no PNGs on disk) for 256x256 ROI Top-Hat CV (10,792 dets).", table_cell)],
        [Paragraph("Broadcast Stream", table_cell), Paragraph("BAR-ATH_broadcast.*", table_cell), Paragraph("<b>Dropped</b>", table_cell), Paragraph("Unsynchronized 164,488-frame timeline with cuts/replays and only 65.8% usable homography.", table_cell)],
    ]
    t_asset = Table(asset_data, colWidths=[78, 150, 48, 259])
    t_asset.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_asset)
    story.append(Spacer(1, 5))

    # Section 3: Training Data & Compliance
    story.append(Paragraph("3. External Data, Pretrained Models &amp; Compliance", h1_style))
    story.append(Paragraph(
        "<b>Zero External Labelled Datasets / Zero Match Training:</b> No supervised neural network or external training dataset was used in the pipeline. All visual ball candidates rely purely on classical OpenCV Morphological Top-Hat contour geometry without weights. Zero algorithms or constants were trained, fitted, or calibrated on the provided BAR-ATH video or possession ground truth, zero human hand labels were created, and zero match data was uploaded to cloud AI services.",
        body_style,
    ))
    story.append(Spacer(1, 3))

    # Section 4: Rules Implemented
    story.append(Paragraph("4. Possession, Loose-Ball &amp; Dead-Ball Rules", h1_style))
    story.append(Paragraph("• <b>Controlled Turnovers:</b> Inside live play, opponent proximity is awarded only when the rival is &lt; 2.5 m and &gt; 0.5 m closer than the carrier, and must persist for <b>&gt;= 25 consecutive frames (1.0 s)</b> before changing team possession.", bullet_style))
    story.append(Paragraph("• <b>Loose Balls &amp; Aerial Passes:</b> When the ball is temporarily contested or airborne (frame_team = NONE), state persistence (+2.0 log-evidence) retains the previous carrier up to <b>35 frames (1.4 s)</b> before resetting.", bullet_style))
    story.append(Paragraph("• <b>Restarts, Kickoffs &amp; Halves:</b> Outside graded half blocks (11185..90651, 110808..190197), labels are explicitly <b>X</b> (40,462 frames). Pre-kickoff (both halves) and post-goal stoppages enforce <b>D</b> until player acceleration activates play.", bullet_style))
    story.append(Spacer(1, 3))

    # Section 5: Ablation & Limitations
    story.append(Paragraph("5. Public-Window Sanity Check, Ablation &amp; Limitations", h1_style))
    ablation_data = [
        [Paragraph("<b>Exp</b>", table_cell_bold), Paragraph("<b>Pipeline Variant</b>", table_cell_bold), Paragraph("<b>Macro-F1</b>", table_cell_bold), Paragraph("<b>Spell-F1</b>", table_cell_bold), Paragraph("<b>Alive/Dead</b>", table_cell_bold), Paragraph("<b>Spells</b>", table_cell_bold), Paragraph("<b>Mean Dur</b>", table_cell_bold)],
        [Paragraph("<b>E0</b>", table_cell), Paragraph("Baseline Floor (smooth50)", table_cell), Paragraph("0.6207", table_cell), Paragraph("0.3256", table_cell), Paragraph("0.8990", table_cell), Paragraph("669", table_cell), Paragraph("7.6 s", table_cell)],
        [Paragraph("<b>E1</b>", table_cell), Paragraph("ATD Kalman Only (No CV, Raw Proximity)", table_cell), Paragraph("0.5353", table_cell), Paragraph("0.0027", table_cell), Paragraph("0.7070", table_cell), Paragraph("1,915", table_cell), Paragraph("1.2 s", table_cell)],
        [Paragraph("<b>E2</b>", table_cell), Paragraph("E1 + Top-Hat CV Ball Candidate Detection", table_cell), Paragraph("0.5467", table_cell), Paragraph("0.0019", table_cell), Paragraph("0.7370", table_cell), Paragraph("3,920", table_cell), Paragraph("0.6 s", table_cell)],
        [Paragraph("<b>E3</b>", table_cell), Paragraph("E2 + RTS Backward Smoother", table_cell), Paragraph("0.5394", table_cell), Paragraph("0.0023", table_cell), Paragraph("0.7339", table_cell), Paragraph("2,964", table_cell), Paragraph("0.9 s", table_cell)],
        [Paragraph("<b>E4</b>", table_cell), Paragraph("E3 + Intelligent Dead-Ball Engine", table_cell), Paragraph("0.5611", table_cell), Paragraph("0.0024", table_cell), Paragraph("0.7273", table_cell), Paragraph("2,934", table_cell), Paragraph("0.8 s", table_cell)],
        [Paragraph("<b>E5</b>", table_cell), Paragraph("E4 + Controlled Possession (dwell=25, Argmax)", table_cell), Paragraph("0.7233", table_cell), Paragraph("0.0626", table_cell), Paragraph("0.9235", table_cell), Paragraph("2,492", table_cell), Paragraph("1.5 s", table_cell)],
        [Paragraph("<b>E6</b>", table_cell_bold), Paragraph("<b>Mama Doain Aku Sukses Ya (Full HMM Viterbi)</b>", table_cell_bold), Paragraph("<b>0.7843</b>", table_cell_bold), Paragraph("<b>0.4000</b>", table_cell_bold), Paragraph("<b>0.9416</b>", table_cell_bold), Paragraph("<b>358</b>", table_cell_bold), Paragraph("<b>10.5 s</b>", table_cell_bold)],
    ]
    t_abl = Table(ablation_data, colWidths=[28, 200, 52, 52, 58, 45, 50])
    t_abl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), light_bg),
        ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#EBF8FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_abl)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Known Limitations:</b> (1) Classical Top-Hat blob detection can trigger false candidates on white footwear or pitch markings in active ROIs; a domain-general CNN ball detector trained strictly on external games would improve visual precision. (2) Severe goalmouth occlusions exceeding 25 frames and planar 2D projections on high aerial duels remain noisy without broadcast multi-view geometry.",
        body_style,
    ))
    story.append(Spacer(1, 3))

    # Section 6: Reproduction
    story.append(Paragraph("6. Reproducibility Instructions", h1_style))
    story.append(Paragraph(
        "Clone the public repository, unpack the match assets into <code>./data</code> (or set <code>MTAH_DATA_DIR</code>), install exact pinned dependencies via <code>pip install -r requirements-pipeline.txt</code>, and run:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>python run.py --config configs/final.yaml</code><br/>"
        "Use <code>--force-recompute</code> to bypass caches or <code>--no-report</code> to skip Data Storytelling reports. Validate via <code>python evaluation/validate_submission.py outputs/Mama_Doain_Aku_Sukses_Ya.csv</code> and <code>pytest</code>. Exact deterministic output SHA-256: <code>59f0cff74f3fa39df74c9bae3f724c9d9ef3d4dc8f3ebdb695e0d9ba6190a914</code>.",
        body_style,
    ))

    doc.build(story)
    print(f"Publication PDF successfully generated at: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
