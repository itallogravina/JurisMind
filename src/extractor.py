import base64
from pathlib import Path

from openai import OpenAI
from pdf2image import convert_from_path


OCR_PROMPT = (
    "Transcreva todo o texto visível nesta página do documento. "
    "Preserve a estrutura original: títulos, campos e valores. "
    "Não adicione interpretações — apenas o texto como aparece no documento."
)


def _pdf_to_base64_images(pdf_path: Path) -> list[str]:
    images = convert_from_path(pdf_path, dpi=200)
    result = []
    for img in images:
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        result.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
    return result


def extract_text_from_pdf(pdf_path: str | Path, client: OpenAI) -> str:
    pages_b64 = _pdf_to_base64_images(Path(pdf_path))

    page_texts = []
    for page_b64 in pages_b64:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{page_b64}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": OCR_PROMPT},
                    ],
                }
            ],
            max_tokens=1000,
            temperature=0,
        )
        page_texts.append(response.choices[0].message.content.strip())

    return "\n".join(page_texts)


def extract_all_documents(docs_dir: str | Path, client: OpenAI) -> dict[str, str]:
    docs_dir = Path(docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {docs_dir}")

    return {pdf.name: extract_text_from_pdf(pdf, client) for pdf in pdfs}
