import json
from openai import OpenAI

LEGAL_BASIS_PROMPT = """Você é um advogado especialista em Direito Previdenciário brasileiro.

Com base na classificação do benefício e nos dados do cliente abaixo, compile a base jurídica completa e atualizada para fundamentar a petição.

Retorne um JSON com a seguinte estrutura:
{{
  "leis": [
    {{
      "diploma": "Lei nº 8.213/91",
      "artigos": ["Art. 86", "Art. 19", "Art. 21"],
      "relevancia": "Fundamento do auxílio-acidente e conceito de acidente de trabalho"
    }}
  ],
  "decretos": [
    {{
      "diploma": "Decreto nº 3.048/99",
      "artigos": ["Art. 104"],
      "relevancia": "Regulamentação do auxílio-acidente"
    }}
  ],
  "sumulas": [
    {{
      "referencia": "Súmula 111 do STJ",
      "enunciado": "Os honorários advocatícios, nas ações previdenciárias, não incidem sobre as prestações vencidas após a sentença.",
      "aplicacao": "Pedido de honorários"
    }}
  ],
  "temas_tnu": [
    {{
      "tema": "Tema 217 da TNU",
      "tese": "...",
      "aplicacao": "Fungibilidade entre benefícios por incapacidade"
    }}
  ],
  "jurisprudencia": [
    {{
      "tribunal": "TRF1",
      "referencia": "AC 0001234-11.2025.4.01.3800",
      "relevancia": "..."
    }}
  ],
  "constituicao": [
    {{
      "artigo": "Art. 201, I",
      "relevancia": "Cobertura constitucional dos eventos de doença, invalidez e acidente"
    }}
  ]
}}

CLASSIFICAÇÃO DO BENEFÍCIO:
{classificacao}

DADOS DO CLIENTE:
{dados_cliente}"""


def search_legal_basis(classification: dict, structured_data: dict, client: OpenAI) -> dict:
    prompt = LEGAL_BASIS_PROMPT.format(
        classificacao=json.dumps(classification, ensure_ascii=False, indent=2),
        dados_cliente=json.dumps(structured_data, ensure_ascii=False, indent=2),
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
