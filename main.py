
from fastapi import FastAPI, Response
from pydantic import BaseModel, Field
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime
import io

app = FastAPI(title="DCA PDF API", version="1.0.0")

class Section(BaseModel):
    titre: str
    contenu: str

class ScoreRow(BaseModel):
    actif: str
    score: int = Field(ge=0, le=5)
    commentaire: Optional[str] = ""

class Analyse(BaseModel):
    sections: List[Section]
    scoring_table: Optional[List[ScoreRow]] = []

class GeneratePdfRequest(BaseModel):
    mois: str
    analyse: Analyse

def build_pdf(mois: str, analyse: Analyse) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=16)
    section_title = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceBefore=10, spaceAfter=6)
    normal = ParagraphStyle('Body', parent=styles['Normal'], leading=15)

    elements.append(Paragraph(f"Analyse DCA ETF Mensuelle — {mois}", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y')}", normal))
    elements.append(Spacer(1, 12))

    for s in analyse.sections:
        elements.append(Paragraph(s.titre, section_title))
        elements.append(Paragraph(s.contenu.replace("\n", "<br/>"), normal))
        elements.append(Spacer(1, 8))

    if analyse.scoring_table:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Tableau de scoring synthétique", section_title))
        data = [["Actif", "Score (0–5)", "Commentaire"]]
        for r in analyse.scoring_table:
            data.append([r.actif, str(r.score), r.commentaire or ""])
        table = Table(data, colWidths=[150, 80, 280])
        ts = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
        for i, r in enumerate(analyse.scoring_table, start=1):
            bg = colors.lightgreen if r.score >= 4 else (colors.orange if r.score >= 2 else colors.red)
            ts.add('BACKGROUND', (1, i), (1, i), bg)
        table.setStyle(ts)
        elements.append(table)

    doc.build(elements)
    pdf = buf.getvalue()
    buf.close()
    return pdf

@app.get("/")
def root():
    return {"status": "ok", "message": "API de génération PDF DCA prête."}

@app.post("/generate_pdf")
def generate_pdf(payload: GeneratePdfRequest):
    pdf = build_pdf(payload.mois, payload.analyse)
    filename = f"Analyse_DCA_{payload.mois.replace(' ', '_')}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
