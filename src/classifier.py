import json
from openai import OpenAI

CLASSIFICATION_PROMPT = """Você é um advogado especialista em Direito Previdenciário brasileiro.

Com base nos dados estruturados do cliente abaixo, classifique o(s) benefício(s) previdenciários mais adequados ao caso.

Benefícios possíveis:
- B31 — Auxílio por Incapacidade Temporária (auxílio-doença): incapacidade temporária para o trabalho
- B91 — Aposentadoria por Incapacidade Permanente (invalidez): incapacidade total e permanente
- B94 — Auxílio-Acidente: sequela permanente decorrente de acidente que reduz a capacidade laboral
- BPC/LOAS — Benefício Assistencial: pessoa com deficiência sem contribuições suficientes

Retorne um JSON com a seguinte estrutura:
{{
  "beneficio_principal": {{
    "codigo": "B94",
    "nome": "Auxílio-Acidente",
    "fundamento_legal": "Art. 86, Lei nº 8.213/91",
    "justificativa": "..."
  }},
  "beneficio_subsidiario": {{
    "codigo": "B91",
    "nome": "Aposentadoria por Incapacidade Permanente",
    "fundamento_legal": "Art. 42, Lei nº 8.213/91",
    "justificativa": "..."
  }},
  "analise": "Análise sucinta do caso com base nos dados clínicos e laborais"
}}

Se não houver benefício subsidiário adequado, retorne null no campo "beneficio_subsidiario".

DADOS DO CLIENTE:
{dados_cliente}"""


def classify_benefit(structured_data: dict, client: OpenAI) -> dict:
    prompt = CLASSIFICATION_PROMPT.format(
        dados_cliente=json.dumps(structured_data, ensure_ascii=False, indent=2)
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
