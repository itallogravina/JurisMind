# JurisMind

Gerador automatizado de petições previdenciárias. Envia PDFs do cliente, o sistema extrai os dados via OCR, classifica o benefício, pesquisa a base jurídica e monta a petição em DOCX.

## Pipeline

```
OCR → Validação Documental → Estruturação → Classificação → Base Jurídica → Petição DOCX
```

## Pré-requisitos

- Python 3.11+
- `poppler-utils` e `libreoffice` instalados no sistema (para PDF e conversão)
- Chave da OpenAI

## Configuração

```bash
cp .env.example .env
# edite .env e preencha OPENAI_API_KEY
```

**.env mínimo:**
```
OPENAI_API_KEY=sk-...
```

**Integrações opcionais:**
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
NOTION_TOKEN=...
NOTION_PARENT_PAGE_ID=...
```

## Instalação local

```bash
pip install -r requirements.txt
```

## Modos de uso

### Interface web
```bash
streamlit run app.py
```
Acesse `http://localhost:8501`. Faça upload dos PDFs e escolha o formato de exportação (DOCX, PDF, Google Docs, Notion).

### CLI (sem interface)
Coloque os PDFs do cliente em `inputs/` e execute:
```bash
python main.py
```
A petição gerada aparece em `outputs/`.

### Docker — interface web
```bash
docker compose up web
```
Acesse `http://localhost:8501`.

### Docker — CLI
```bash
docker compose run cli
```
Lê de `./inputs/` e salva em `./outputs/` via volume.

## Estrutura

```
inputs/          # PDFs do cliente (RG, laudo, CNIS etc.)
outputs/         # Petições geradas
templates/       # Template DOCX da petição
src/
  pipeline.py    # Orquestração do pipeline
  extractor.py   # OCR com GPT-4o Vision
  validator.py   # Validação dos documentos
  parser.py      # Extração estruturada de dados
  classifier.py  # Classificação do benefício (B91/B94/B31/BPC)
  legal_basis.py # Busca de base jurídica
  ai_service.py  # Geração da petição via IA
  exporters/     # DOCX, PDF, Google Docs, Notion
app.py           # Interface Streamlit
main.py          # Entrypoint CLI
```

## Documentos obrigatórios

| Documento | Obrigatório |
|---|---|
| RG ou documento de identificação | ✅ |
| Comprovante de residência | ✅ |
| Carta de indeferimento INSS | ✅ |
| Laudo médico | ✅ |
| CNIS | ✅ |

O sistema alerta sobre documentos faltantes mas não interrompe o processo.
