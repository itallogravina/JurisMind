import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from src.extractor import extract_all_documents
from src.parser import extract_structured_data
from src.ai_service import generate_petition
from src.exporter import export_to_docx

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR.parent  # PDFs estão na pasta pai
TEMPLATE_PATH = BASE_DIR.parent / "documento.txt"
OUTPUTS_DIR = BASE_DIR / "outputs"


def _log(stage: str, status: str, execution_id: str):
    log.info(json.dumps({
        "executionId": execution_id,
        "stage": stage,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }))


def run_pipeline() -> Path:
    start = time.time()
    execution_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY não definida. Crie um arquivo .env com a chave.")

    client = OpenAI(api_key=api_key)

    # 1. Extração de texto dos PDFs
    _log("ocr", "started", execution_id)
    documents = extract_all_documents(DOCS_DIR)
    _log("ocr", "success", execution_id)
    log.info(f"Documentos extraídos: {list(documents.keys())}")

    # 2. Estruturação dos dados em JSON
    _log("parser", "started", execution_id)
    structured_data = extract_structured_data(documents, client)
    _log("parser", "success", execution_id)
    log.info(f"Dados estruturados:\n{json.dumps(structured_data, ensure_ascii=False, indent=2)}")

    # 3. Leitura do modelo de referência
    _log("template", "started", execution_id)
    reference_petition = TEMPLATE_PATH.read_text(encoding="utf-8")
    _log("template", "success", execution_id)

    # 4. Geração da petição via IA
    _log("ai_generation", "started", execution_id)
    petition_text = generate_petition(structured_data, reference_petition, client)
    _log("ai_generation", "success", execution_id)

    # 5. Exportação para DOCX
    _log("export", "started", execution_id)
    client_name = structured_data["cliente"]["nome"].replace(" ", "_")
    output_filename = f"Peticao_{client_name}_{datetime.now().strftime('%Y-%m-%d')}.docx"
    output_path = export_to_docx(petition_text, OUTPUTS_DIR / output_filename, client_name)
    _log("export", "success", execution_id)

    elapsed = round(time.time() - start, 2)
    log.info(f"Pipeline concluído em {elapsed}s — arquivo: {output_path}")

    return output_path


if __name__ == "__main__":
    output = run_pipeline()
    print(f"\nPetição gerada: {output}")
