# Como rodar

## Pré-requisitos locais

```bash
# Ubuntu/Debian
sudo apt install poppler-utils libreoffice

# macOS
brew install poppler libreoffice
```

## 1. Interface web (Streamlit)

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha OPENAI_API_KEY
streamlit run app.py
```

Acesse `http://localhost:8501`, faça upload dos PDFs e clique em "Gerar Petição".

---

## 2. CLI (terminal, sem interface)

Coloque os PDFs em `inputs/` e execute:

```bash
python main.py
```

A petição gerada aparece em `outputs/`. O terminal exibe logs estruturados de cada etapa.

---

## 3. Docker — interface web

```bash
docker compose up web
```

Acesse `http://localhost:8501`. Os diretórios `inputs/` e `outputs/` são montados como volumes — os arquivos ficam na sua máquina.

---

## 4. Docker — CLI

```bash
# Coloque os PDFs em ./inputs/ antes de executar
docker compose run cli
```

---

## Template da petição

O template padrão fica em `templates/`. Para usar um template próprio:

- **Interface web:** faça upload do DOCX na seção "Template da Petição"
- **CLI:** substitua o arquivo em `templates/` ou altere `TEMPLATE_PATH` em `main.py`

O template deve conter texto de exemplo com a estrutura de uma petição real — a IA usa os parágrafos do modelo como guia de formato.

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Chave da API OpenAI |
| `GOOGLE_CLIENT_ID` | ❌ | OAuth Google Docs |
| `GOOGLE_CLIENT_SECRET` | ❌ | OAuth Google Docs |
| `NOTION_TOKEN` | ❌ | Token da integração Notion |
| `NOTION_PARENT_PAGE_ID` | ❌ | ID da página pai no Notion |
