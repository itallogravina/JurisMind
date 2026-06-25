# Pipeline — Detalhes de cada etapa

## 1. OCR (`src/extractor.py`)

Converte cada PDF em imagens (200 dpi via `pdf2image`) e envia para o GPT-4o Vision em base64. Retorna um `dict[filename, texto_extraído]`.

Dependência de sistema: `poppler-utils`.

---

## 2. Validação Documental (`src/validator.py`)

Recebe o texto extraído e usa o GPT-4o para:

- Identificar o tipo de cada documento pelo conteúdo (não pelo nome do arquivo)
- Verificar presença dos 5 documentos obrigatórios
- Avaliar qualidade (`ok` / `ilegível` / `incompleto`)
- Detectar datas e assinaturas
- Emitir alertas de anomalias (documentos vencidos, datas inconsistentes etc.)

O prompt inclui a data de hoje para evitar falsos positivos de "data futura".

**Documentos obrigatórios:** RG, Comprovante de residência, Carta de indeferimento INSS, Laudo médico, CNIS.

Documentos faltantes geram apenas alerta — o pipeline continua.

**Retorno:**
```json
{
  "status": "completo" | "incompleto",
  "documentos": { "<arquivo>": { "tipo", "qualidade", "datas_encontradas", "assinatura" } },
  "faltantes": [],
  "alertas": []
}
```

---

## 3. Estruturação (`src/parser.py`)

Extrai dados do cliente em JSON estruturado a partir do texto OCR.

**Campos extraídos:** nome, CPF, RG, data de nascimento, endereço, profissão, dados do benefício INSS, CID, histórico médico e dados da carta de indeferimento.

---

## 4. Classificação do Benefício (`src/classifier.py`)

Com base nos dados estruturados, determina:

| Código | Benefício |
|---|---|
| B91 | Auxílio por incapacidade temporária |
| B94 | Aposentadoria por incapacidade permanente |
| B31 | Aposentadoria por tempo de contribuição |
| BPC | Benefício de Prestação Continuada (LOAS) |

Retorna benefício principal, subsidiário (quando aplicável) e justificativa.

---

## 5. Base Jurídica (`src/legal_basis.py`)

Pesquisa os fundamentos legais aplicáveis ao caso:

- Leis e artigos (ex: Lei 8.213/91)
- Decretos regulamentadores
- Súmulas do STJ/STF
- Temas de repercussão geral (TNU)
- Jurisprudência relevante
- Base constitucional (art. 201/203 CF)

---

## 6. Geração da Petição (`src/ai_service.py`)

Lê o template DOCX parágrafo a parágrafo via `src/template_reader.py` e envia para o GPT-4o junto com todos os dados coletados nas etapas anteriores. A IA substitui os dados do modelo pelos dados reais do cliente, mantendo o estilo jurídico.

**Tolerância de parágrafos:** aceita até ±20% de diferença em relação ao template original para acomodar variações naturais da IA.

O DOCX final é montado via `python-docx`, preservando formatação e estilos do template.

---

## 7. Exportação (`src/exporters/`)

| Módulo | Destino | Dependência |
|---|---|---|
| `pdf_exporter.py` | PDF local | `libreoffice --headless` |
| `google_docs.py` | Google Drive (Google Doc) | OAuth2 (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) |
| `notion_exporter.py` | Página no Notion | `NOTION_TOKEN`, `NOTION_PARENT_PAGE_ID` |
