import json
from openai import OpenAI


PETITION_PROMPT = """Você é um advogado especialista em Direito Previdenciário brasileiro.

Sua tarefa é redigir uma petição inicial previdenciária para um novo cliente, seguindo a estrutura,
linguagem e organização da petição de referência fornecida abaixo.

IMPORTANTE:
- NÃO copie os fatos da petição de referência. Eles pertencem a outro caso.
- Construa uma fundamentação jurídica específica para o caso de {nome}, considerando:
  * Profissão: {profissao}
  * Diagnóstico/Sequela: {diagnostico}
  * CID-10: {cid}
  * Motivo do indeferimento do INSS: {motivo_indeferimento}
  * Impacto laboral específico: {impacto_laboral}
- Use a mesma estrutura de seções da petição de referência.
- Adapte os fundamentos jurídicos ao tipo de benefício requerido: {tipo_beneficio}.
- Escreva em linguagem jurídica formal, como a petição de referência.

DADOS DO CLIENTE:
{dados_cliente}

PETIÇÃO DE REFERÊNCIA (use apenas como modelo de estrutura, linguagem e formatação):
{peticao_referencia}

Retorne a petição completa, pronta para revisão do advogado."""


def generate_petition(
    structured_data: dict,
    reference_petition: str,
    client: OpenAI,
) -> str:
    cliente = structured_data["cliente"]
    saude = structured_data["saude"]
    beneficio = structured_data["beneficio"]
    endereco = structured_data["endereco"]

    prompt = PETITION_PROMPT.format(
        nome=cliente["nome"],
        profissao=structured_data.get("profissao", ""),
        diagnostico=saude["diagnostico"],
        cid=saude["cid"],
        motivo_indeferimento=beneficio["motivo_indeferimento"],
        impacto_laboral=saude["impacto_laboral"],
        tipo_beneficio=beneficio["tipo"],
        dados_cliente=json.dumps(structured_data, ensure_ascii=False, indent=2),
        peticao_referencia=reference_petition,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )

    return response.choices[0].message.content
