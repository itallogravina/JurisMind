import json
from datetime import date
from openai import OpenAI

OBRIGATORIOS = [
    "RG",
    "Comprovante de residência",
    "Carta de indeferimento INSS",
    "Laudo médico",
    "CNIS",
]

VALIDATION_PROMPT = """Você é um especialista em documentação previdenciária brasileira.

Data de hoje: {hoje}

Abaixo estão os textos extraídos por OCR de documentos de um cliente. Cada documento está identificado pelo nome do arquivo.

Sua tarefa é analisar cada documento e retornar um JSON com a seguinte estrutura:

{{
  "status": "completo" | "incompleto",
  "documentos": {{
    "<nome_do_arquivo>": {{
      "tipo": "<tipo identificado>",
      "qualidade": "ok" | "ilegível" | "incompleto",
      "datas_encontradas": ["<data1>", "<data2>"],
      "assinatura": true | false
    }}
  }},
  "faltantes": ["<tipo1>", "<tipo2>"],
  "alertas": ["<alerta1>", "<alerta2>"]
}}

Documentos obrigatórios para um processo previdenciário:
{obrigatorios}

Regras:
- Classifique cada arquivo em um dos tipos obrigatórios acima (ou "Outro" se não se encaixar).
- "qualidade": "ok" se o texto é legível e tem conteúdo suficiente; "ilegível" se o OCR extraiu muito pouco texto (menos de 50 caracteres); "incompleto" se faltam campos essenciais do tipo.
- "datas_encontradas": extraia todas as datas visíveis no formato original.
- "assinatura": true se há menção a assinatura, carimbo ou "assinado por"; false caso contrário.
- "faltantes": liste os tipos obrigatórios que não foram encontrados em nenhum dos arquivos.
- "alertas": documente qualquer anomalia (data inválida, documento vencido, assinatura ausente onde esperada, etc.).
- "status": "completo" somente se todos os obrigatórios estiverem presentes e com qualidade "ok".

DOCUMENTOS:
{documentos}"""


def validate_documents(documents: dict[str, str], client: OpenAI) -> dict:
    docs_text = "\n\n".join(
        f"=== {filename} ===\n{text}" for filename, text in documents.items()
    )

    prompt = VALIDATION_PROMPT.format(
        hoje=date.today().strftime("%d/%m/%Y"),
        obrigatorios="\n".join(f"- {d}" for d in OBRIGATORIOS),
        documentos=docs_text,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
