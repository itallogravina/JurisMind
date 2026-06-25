import os
import json
import time
import logging
from datetime import datetime, UTC
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from src.pipeline import run_pipeline, output_filename

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "inputs"
TEMPLATE_PATH = BASE_DIR / "templates" / "Peticao_MODELO_Auxilio_Doenca_Maria da Silva_2026-06-22.docx"
OUTPUTS_DIR = BASE_DIR / "outputs"


def _log(stage: str, status: str, execution_id: str, data: dict = None):
    log.info(json.dumps({
        "executionId": execution_id,
        "stage": stage,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        **(data or {}),
    }))


def cli_pipeline():
    start = time.time()
    execution_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY não definida. Crie um arquivo .env com a chave.")

    client = OpenAI(api_key=api_key)
    OUTPUTS_DIR.mkdir(exist_ok=True)

    def on_stage(stage, status, data):
        _log(stage, status, execution_id, data)
        if stage == "validation" and status == "success":
            faltantes = data.get("faltantes", [])
            if faltantes:
                log.warning(f"Documentação incompleta — faltantes: {faltantes}")

    result = run_pipeline(
        docs_dir=DOCS_DIR,
        template_path=TEMPLATE_PATH,
        output_path=OUTPUTS_DIR / "temp_output.docx",
        client=client,
        on_stage=on_stage,
    )

    fname = output_filename(result["structured_data"])
    final_path = OUTPUTS_DIR / fname
    result["output_path"].rename(final_path)

    elapsed = round(time.time() - start, 2)
    log.info(f"Pipeline concluído em {elapsed}s — arquivo: {final_path}")
    return final_path


if __name__ == "__main__":
    output = cli_pipeline()
    print(f"\nPetição gerada: {output}")
