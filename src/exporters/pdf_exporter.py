import subprocess
from pathlib import Path


def convert_to_pdf(docx_path: str | Path) -> Path:
    docx_path = Path(docx_path)
    output_dir = docx_path.parent

    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice falhou ao converter para PDF: {result.stderr}")

    pdf_path = output_dir / docx_path.with_suffix(".pdf").name
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não gerado em {pdf_path}")

    return pdf_path
