import json
from openai import OpenAI


ADAPTATION_PROMPT = """Você é um advogado especialista em Direito Previdenciário brasileiro.

Abaixo está a estrutura de uma petição previdenciária da cliente Maria, serializada como lista de parágrafos JSON.
Cada parágrafo tem: "style" (estilo do documento), "text" (conteúdo) e "bold" (negrito).

Sua tarefa é adaptar essa petição para o cliente JOÃO DA SILVA, usando os dados fornecidos.

REGRAS OBRIGATÓRIAS:
1. Mantenha EXATAMENTE a mesma quantidade de parágrafos e os mesmos valores de "style" e "bold".
2. Adapte o "text" de cada parágrafo para o caso do João — não copie os fatos da Maria.
3. Seções de fatos e fundamentação devem ser completamente reescritas para o caso específico do João:
   - Profissão: {profissao}
   - Acidente: {historico_acidente}
   - Sequela: {sequelas}
   - Impacto laboral: {impacto_laboral}
   - CID-10: {cid}
   - Benefício principal: {beneficio_principal}
   - Benefício subsidiário: {beneficio_subsidiario}
   - Motivo do indeferimento: {motivo_indeferimento}
4. Use a base jurídica fornecida para fundamentar os argumentos legais (leis, súmulas, temas TNU).
5. Seções boilerplate (gratuidade, mediação, coisa julgada, fungibilidade, reabilitação) podem manter
   o texto jurídico, apenas adaptando pronomes e referências ao cliente.
6. Pedidos devem ser adequados ao benefício classificado.
7. Retorne um JSON com a chave "paragraphs" contendo EXATAMENTE {total} objetos — um para cada parágrafo do template.
   Não omita, agrupe nem divida parágrafos. Todos os {total} parágrafos devem estar presentes na resposta.

DADOS DO CLIENTE:
{dados_cliente}

CLASSIFICAÇÃO DO BENEFÍCIO:
{classificacao}

BASE JURÍDICA:
{base_juridica}

ESTRUTURA DA PETIÇÃO DA MARIA (adapte parágrafo a parágrafo):
{template_paragraphs}"""


def generate_petition_from_template(
    template_paragraphs: list[dict],
    structured_data: dict,
    client: OpenAI,
    classification: dict | None = None,
    legal_basis: dict | None = None,
) -> list[dict]:
    saude = structured_data["saude"]
    beneficio = structured_data["beneficio"]

    beneficio_principal = (
        f"{classification['beneficio_principal']['nome']} ({classification['beneficio_principal']['codigo']}) — "
        f"{classification['beneficio_principal']['fundamento_legal']}"
        if classification else beneficio.get("tipo", "")
    )
    beneficio_subsidiario = (
        f"{classification['beneficio_subsidiario']['nome']} ({classification['beneficio_subsidiario']['codigo']}) — "
        f"{classification['beneficio_subsidiario']['fundamento_legal']}"
        if classification and classification.get("beneficio_subsidiario") else "Não aplicável"
    )

    prompt = ADAPTATION_PROMPT.format(
        profissao=structured_data.get("profissao", ""),
        historico_acidente=saude["historico_acidente"],
        sequelas=saude["sequelas"],
        impacto_laboral=saude["impacto_laboral"],
        cid=saude["cid"],
        beneficio_principal=beneficio_principal,
        beneficio_subsidiario=beneficio_subsidiario,
        motivo_indeferimento=beneficio["motivo_indeferimento"],
        dados_cliente=json.dumps(structured_data, ensure_ascii=False, indent=2),
        classificacao=json.dumps(classification or {}, ensure_ascii=False, indent=2),
        base_juridica=json.dumps(legal_basis or {}, ensure_ascii=False, indent=2),
        template_paragraphs=json.dumps(template_paragraphs, ensure_ascii=False, indent=2),
        total=len(template_paragraphs),
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
        max_tokens=16000,
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    paragraphs = result.get("paragraphs", [])

    expected = len(template_paragraphs)
    got = len(paragraphs)
    if got == 0:
        raise ValueError("IA retornou lista de parágrafos vazia")
    if abs(got - expected) > expected * 0.2:
        raise ValueError(f"IA retornou {got} parágrafos, esperado ~{expected} (diferença acima de 20%)")

    return paragraphs
