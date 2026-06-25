from pathlib import Path
from datetime import datetime
from openai import OpenAI

from src.extractor import extract_all_documents
from src.validator import validate_documents
from src.parser import extract_structured_data
from src.classifier import classify_benefit
from src.legal_basis import search_legal_basis
from src.template_reader import read_template_structure
from src.ai_service import generate_petition_from_template
from src.exporter import export_from_template


def run_pipeline(
    docs_dir: str | Path,
    template_path: str | Path,
    output_path: str | Path,
    client: OpenAI,
    on_stage=None,
) -> dict:
    """
    Executa o pipeline completo de geração de petição.
    on_stage(stage, status, data) é chamado a cada etapa para feed de progresso.
    Retorna dict com output_path, validation, structured_data, classification.
    """

    def notify(stage: str, status: str, data=None):
        if on_stage:
            on_stage(stage, status, data or {})

    # 1. OCR
    notify("ocr", "started")
    documents = extract_all_documents(docs_dir, client)
    notify("ocr", "success", {"arquivos": list(documents.keys())})

    # 2. Validação documental
    notify("validation", "started")
    validation = validate_documents(documents, client)
    notify("validation", "success", validation)

    # 3. Parser — estruturação JSON
    notify("parser", "started")
    structured_data = extract_structured_data(documents, client)
    notify("parser", "success", structured_data)

    # 4. Classificação do benefício
    notify("classification", "started")
    classification = classify_benefit(structured_data, client)
    notify("classification", "success", classification)

    # 5. Base jurídica
    notify("legal_basis", "started")
    legal_basis = search_legal_basis(classification, structured_data, client)
    notify("legal_basis", "success", legal_basis)

    # 6. Leitura do template
    notify("template", "started")
    template_paragraphs = read_template_structure(template_path)
    notify("template", "success", {"paragrafos": len(template_paragraphs)})

    # 7. Montagem da petição
    notify("ai_generation", "started")
    adapted_paragraphs = generate_petition_from_template(
        template_paragraphs, structured_data, client,
        classification=classification,
        legal_basis=legal_basis,
    )
    notify("ai_generation", "success", {"paragrafos": len(adapted_paragraphs)})

    # 8. Exportação DOCX
    notify("export", "started")
    result_path = export_from_template(template_path, adapted_paragraphs, output_path)
    notify("export", "success", {"arquivo": str(result_path)})

    return {
        "output_path": result_path,
        "validation": validation,
        "structured_data": structured_data,
        "classification": classification,
        "legal_basis": legal_basis,
    }


def output_filename(structured_data: dict) -> str:
    nome = structured_data.get("cliente", {}).get("nome", "CLIENTE").replace(" ", "_")
    data = datetime.now().strftime("%Y-%m-%d")
    return f"Peticao_{nome}_{data}.docx"
