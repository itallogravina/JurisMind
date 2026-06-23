import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def extract_all_documents(docs_dir: str | Path) -> dict[str, str]:
    docs_dir = Path(docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {docs_dir}")

    return {pdf.name: extract_text_from_pdf(pdf) for pdf in pdfs}
