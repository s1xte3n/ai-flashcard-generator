from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()

@router.get("/export/csv")
async def export_csv(flashcards: str):
    try:
        cards_list = __parse_flashcards_param(flashcards)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Question", "Answer", "Topic"])
    
    for card in cards_list:
        writer.writerow([card['question'], card['answer'], card.get('topic', '')])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flashcards.csv"}
    )

@router.get("/export/pdf")
async def export_pdf(flashcards: str):
    try:
        cards_list = __parse_flashcards_param(flashcards)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph("Generated Flashcards", styles['Title']))
    story.append(Spacer(1, 20))
    
    for i, card in enumerate(cards_list):
        if i > 0:
            story.append(Spacer(1, 15))
        
        q = Paragraph(f"<b>Q:</b> {card['question']}", styles['Normal'])
        a = Paragraph(f"<b>A:</b> {card['answer']}", styles['Normal'])
        
        story.append(q)
        story.append(Spacer(1, 5))
        story.append(a)
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=flashcards.pdf"}
    )

def __parse_flashcards_param(param: str):
    import json
    try:
        return json.loads(param)
    except json.JSONDecodeError:
        raise ValueError("Invalid flashcards parameter")
