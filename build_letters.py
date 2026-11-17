"""Build Cover Letter and STROBE checklist docx via python-docx."""
import os, re
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

SUB = r"D:\CHARLS\DementiaTransition_W6\submission"
FONT = "Times New Roman"

def set_font(style, size=11):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")

def add_md_paragraph(doc, text):
    """Parse **bold** segments into runs."""
    p = doc.add_paragraph()
    parts = re.split(r"\*\*", text)
    for i, seg in enumerate(parts):
        if not seg:
            continue
        r = p.add_run(seg.replace("*", ""))
        r.bold = (i % 2 == 1)
        r.font.name = FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    return p

# ---------- Cover letter ----------
doc = Document()
set_font(doc.styles["Normal"], 11)
with open(r"D:\CHARLS\DementiaTransition_W6\manuscript\cover_letter.md", encoding="utf-8") as f:
    lines = f.read().splitlines()
for ln in lines:
    s = ln.strip()
    if not s or s == "---":
        continue
    if s.startswith("# "):
        h = doc.add_heading(s[2:], level=1)
        continue
    if re.match(r"^\d+\.\s", s):
        add_md_paragraph(doc, s)
        doc.paragraphs[-1].paragraph_format.left_indent = Inches(0.3)
        continue
    if s.startswith("*") and s.endswith("*") and len(s) > 2:
        p = doc.add_paragraph()
        r = p.add_run(s.strip("*")); r.italic = True
        continue
    add_md_paragraph(doc, s)
doc.save(os.path.join(SUB, "Cover_Letter.docx"))

# ---------- STROBE checklist ----------
strobe = [
    ("1. Title/abstract", "(a) Study design indicated (multi-state cohort analysis); abstract structured and balanced", "Title page; Abstract"),
    ("2. Background/rationale", "Scientific background and rationale explained", "Background, paras 1-3"),
    ("3. Objectives", "Specific objectives stated", "Background, final para"),
    ("4. Study design", "Cohort study with two-wave panel; key elements presented", "Methods - Study population"),
    ("5. Setting", "CHARLS setting, waves, dates, three-tranche fielding", "Methods - Study population"),
    ("6. Participants", "Eligibility criteria (age >= 60, 2018 interview, classifiable state); flow diagram", "Methods; Fig. 1"),
    ("7. Variables", "Outcomes (cognitive states, death), exposures (prevalent/incident stroke), confounders defined", "Methods - Cognitive status classification; Covariates"),
    ("8. Data sources/measurement", "Cognitive battery, IQCODE, interview dates, exit module described", "Methods"),
    ("9. Bias", "Survivor structure for incident stroke; misclassification; attrition; midpoint death imputation discussed", "Discussion - Limitations"),
    ("10. Study size", "n = 10,628 classifiable; panel 9,679; complete-case 8,178", "Results - Cohort; Fig. 1"),
    ("11. Quantitative variables", "Age z-scored; education 4-level; cut-offs given", "Methods - Covariates; Statistical analysis"),
    ("12. Statistical methods", "msm continuous-time Markov model; stratified multinomial; sensitivity analyses (cut-offs, strict CIND, multiple imputation); software stated", "Methods - Statistical analysis"),
    ("13. Participants flow", "Numbers at each stage; losses with reasons and characteristics", "Results - Cohort; Fig. 1; Suppl. Table S2"),
    ("14. Descriptive data", "Baseline characteristics by state; outcome events per state", "Table 1; Table 2"),
    ("15. Outcome data", "Transition counts, intensities, probabilities reported", "Tables 2-3; Figs. 2-4"),
    ("16. Main results", "Adjusted RRRs with 95% CI for all transitions", "Results; Table 4; Fig. 3"),
    ("17. Other analyses", "Cut-off, strict-definition, and multiple-imputation sensitivity analyses", "Suppl. Tables S1, S3, S4"),
    ("18. Key results", "Summarised with reference to objectives", "Discussion, para 1"),
    ("19. Limitations", "Direction and magnitude of potential biases discussed", "Discussion - Limitations"),
    ("20. Interpretation", "Cautious, considers objectives, limitations, and other evidence", "Discussion"),
    ("21. Generalisability", "Discussed (Chinese national cohort; external consistency with meta-analytic estimates)", "Discussion; Conclusions"),
    ("22. Funding", "Funding statement placeholder to be completed by authors", "Declarations"),
]
doc = Document()
set_font(doc.styles["Normal"], 10.5)
doc.add_heading("STROBE Statement - Checklist of items (cohort study)", level=1)
p = doc.add_paragraph()
p.add_run("Manuscript: " + "Cognitive state transitions and the stage-dependent role of "
          "stroke in older Chinese adults: a multi-state analysis of CHARLS "
          "2018\u20132023").italic = True
tbl = doc.add_table(rows=1, cols=3)
tbl.style = "Table Grid"
hdr = tbl.rows[0].cells
for i, t in enumerate(["Item", "Recommendation", "Location in manuscript"]):
    hdr[i].text = ""
    r = hdr[i].paragraphs[0].add_run(t); r.bold = True
for item, rec, loc in strobe:
    row = tbl.add_row().cells
    for i, t in enumerate([item, rec, loc]):
        row[i].text = t
        for pp in row[i].paragraphs:
            for rr in pp.runs:
                rr.font.name = FONT
                rr._element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
                rr.font.size = Pt(10)
doc.save(os.path.join(SUB, "STROBE_checklist.docx"))
print("cover letter + strobe done")
