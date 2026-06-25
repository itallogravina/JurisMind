from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
import copy


def export_from_template(
    template_path: str | Path,
    adapted_paragraphs: list[dict],
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = Document(template_path)

    body = doc.element.body
    existing = body.findall(qn("w:p"))

    # Garante que temos o mesmo número de parágrafos — adiciona ou remove conforme necessário
    diff = len(adapted_paragraphs) - len(existing)
    if diff > 0:
        last = existing[-1]
        for _ in range(diff):
            new_p = copy.deepcopy(last)
            body.append(new_p)
        existing = body.findall(qn("w:p"))
    elif diff < 0:
        for p_el in existing[len(adapted_paragraphs):]:
            body.remove(p_el)
        existing = body.findall(qn("w:p"))

    # Substitui o texto de cada parágrafo preservando o estilo do template
    for p_el, adapted in zip(existing, adapted_paragraphs):
        # Remove todos os runs existentes
        for r in p_el.findall(qn("w:r")):
            p_el.remove(r)
        # Remove hyperlinks que possam conter runs
        for hl in p_el.findall(qn("w:hyperlink")):
            p_el.remove(hl)

        new_text = adapted.get("text", "")
        is_bold = adapted.get("bold", False)

        if new_text:
            r_el = copy.deepcopy(_make_run(new_text, is_bold))
            p_el.append(r_el)

    doc.save(output_path)
    return output_path


def _make_run(text: str, bold: bool):
    from docx.oxml import OxmlElement
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if bold:
        b = OxmlElement("w:b")
        rpr.append(b)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r
