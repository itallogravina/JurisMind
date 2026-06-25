# Arquitetura

## Visão geral

JurisMind é uma aplicação Python que automatiza a geração de petições previdenciárias a partir de documentos do cliente. Tem dois pontos de entrada: uma interface web (Streamlit) e um CLI, ambos executando o mesmo pipeline interno.

```
┌─────────────┐     ┌──────────────┐
│   app.py    │     │   main.py    │
│  (web UI)   │     │    (CLI)     │
└──────┬──────┘     └──────┬───────┘
       │                   │
       └────────┬──────────┘
                ▼
        src/pipeline.py
                │
    ┌───────────┼────────────┐
    ▼           ▼            ▼
extractor   validator     parser
  (OCR)    (validação)  (estrutura)
                │
    ┌───────────┼────────────┐
    ▼           ▼            ▼
classifier  legal_basis  ai_service
(benefício) (jurídico)  (petição)
                │
         exporters/
     DOCX │ PDF │ Google Docs │ Notion
```

## Fluxo do pipeline

| # | Etapa | Módulo | O que faz |
|---|---|---|---|
| 1 | OCR | `extractor.py` | Converte PDFs em imagens e extrai texto via GPT-4o Vision |
| 2 | Validação | `validator.py` | Classifica cada doc, identifica faltantes e emite alertas |
| 3 | Estruturação | `parser.py` | Extrai dados do cliente em JSON estruturado |
| 4 | Classificação | `classifier.py` | Define o benefício (B91/B94/B31/BPC) e fundamento legal |
| 5 | Base jurídica | `legal_basis.py` | Busca leis, decretos, súmulas e jurisprudência aplicáveis |
| 6 | Petição | `ai_service.py` | Preenche o template DOCX parágrafo a parágrafo via IA |
| 7 | Exportação | `exporters/` | Gera DOCX, PDF, Google Docs ou página no Notion |

## Callback de progresso

O pipeline expõe um callback `on_stage(stage, status, data)` que a interface web usa para atualizar o progresso em tempo real e o CLI usa para logging estruturado.

```python
def on_stage(stage: str, status: str, data: dict):
    # stage: "ocr" | "validation" | "parser" | "classification" | ...
    # status: "success" | "error"
    # data: resultado da etapa
    ...
```
