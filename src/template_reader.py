from pathlib import Path
from docx import Document


def read_template_structure(docx_path: str | Path) -> list[dict]:
    doc = Document(docx_path)
    paragraphs = []
    for p in doc.paragraphs:
        paragraphs.append({
            "style": p.style.name,
            "text": p.text,
            "bold": any(r.bold for r in p.runs if r.text.strip()),
        })
    return paragraphs
