import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _is_heading(line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,4})\s+(.+)$", line)
    if match:
        level = len(match.group(1))
        text = match.group(2).strip()
        return level, text
    return None


def _strip_markdown_bold(text: str) -> list[tuple[str, bool]]:
    """Split text into (segment, is_bold) pairs."""
    parts = re.split(r"\*\*(.+?)\*\*", text)
    result = []
    for i, part in enumerate(parts):
        result.append((part, i % 2 == 1))
    return result


def export_to_docx(petition_text: str, output_path: str | Path, client_name: str) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(1.18)
        section.bottom_margin = Inches(1.18)
        section.left_margin = Inches(1.38)
        section.right_margin = Inches(1.18)

    # Default paragraph style
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(12)

    lines = petition_text.split("\n")

    for line in lines:
        line = line.rstrip()

        heading = _is_heading(line)
        if heading:
            level, text = heading
            word_level = min(level, 4)
            p = doc.add_heading(text, level=word_level)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.runs[0] if p.runs else p.add_run(text)
            run.font.name = "Arial"
            run.font.size = Pt(12)
            continue

        if line.strip() == "":
            doc.add_paragraph("")
            continue

        # Remove leading list markers
        clean_line = re.sub(r"^[a-z]\)\s+", "", line)
        clean_line = re.sub(r"^[-*]\s+", "", clean_line)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        segments = _strip_markdown_bold(clean_line)
        for text_seg, is_bold in segments:
            if text_seg:
                run = p.add_run(text_seg)
                run.bold = is_bold
                run.font.name = "Arial"
                run.font.size = Pt(12)

    doc.save(output_path)
    return output_path
