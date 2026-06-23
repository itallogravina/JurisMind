import json
from openai import OpenAI


EXTRACTION_PROMPT = """Você é um extrator de dados jurídicos e médicos.

A seguir estão os textos extraídos dos documentos de um cliente previdenciário.
Extraia as informações e retorne APENAS um JSON válido, sem texto adicional.

Documentos:
{documents}

Retorne o JSON neste formato exato:
{{
  "cliente": {{
    "nome": "",
    "cpf": "",
    "rg": "",
    "data_nascimento": "",
    "naturalidade": "",
    "filiacao": ""
  }},
  "endereco": {{
    "logradouro": "",
    "cidade": "",
    "uf": "",
    "cep": ""
  }},
  "profissao": "",
  "beneficio": {{
    "tipo": "",
    "numero_beneficio": "",
    "data_requerimento": "",
    "data_pericia": "",
    "motivo_indeferimento": ""
  }},
  "saude": {{
    "cid": "",
    "diagnostico": "",
    "historico_acidente": "",
    "sequelas": "",
    "impacto_laboral": "",
    "medico": "",
    "crm": "",
    "data_laudo": ""
  }}
}}"""


def extract_structured_data(documents: dict[str, str], client: OpenAI) -> dict:
    docs_text = "\n\n".join(
        f"=== {name} ===\n{text}" for name, text in documents.items()
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(documents=docs_text),
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)
