# Avaliação do projeto

## Ferramentas utilizadas

| Ferramenta | Papel |
|---|---|
| GPT-4o Vision | OCR dos PDFs e geração da petição |
| GPT-4o | Validação documental, classificação do benefício, base jurídica |
| python-docx | Leitura do template e montagem do DOCX final |
| pdf2image + poppler | Conversão de PDF em imagens para o OCR |
| LibreOffice headless | Conversão de DOCX para PDF |
| Streamlit | Interface web com upload e exportação |
| google-auth-oauthlib | Autenticação OAuth2 para Google Docs |
| notion-client | Integração com Notion |
| python-dotenv | Gerenciamento de variáveis de ambiente |
| Docker | Empacotamento da aplicação |

---

## O que funcionou bem

**OCR com GPT-4o Vision**
A abordagem de converter o PDF em imagens e enviar para o modelo de visão foi significativamente mais robusta do que soluções tradicionais de OCR (Tesseract, etc.). O modelo entendeu documentos com layouts complexos, tabelas e texto manuscrito sem configuração adicional.

**Separação entre modelo e dados**
Usar a petição da Maria como template estrutural — e não como texto a ser copiado — garantiu que a petição de João tivesse fundamentação própria. O pipeline classifica o benefício e busca a base jurídica antes de gerar o texto, o que força a IA a raciocinar sobre o caso específico em vez de fazer substituição simples de nomes.

**Pipeline com callback de progresso**
Extrair o pipeline para `src/pipeline.py` com um callback `on_stage` permitiu reutilizar exatamente o mesmo código no CLI e na interface web, sem duplicação.

**Validação documental com data atual**
Injetar a data de hoje no prompt do validador evitou falsos positivos de "data futura" em documentos recentes — um detalhe que só aparece em uso real.

**Múltiplos destinos de exportação**
Entregar DOCX, PDF, Google Docs e Notion na mesma interface cobre o fluxo de trabalho de diferentes perfis de usuário sem exigir passos extras.

---

## O que melhoraria com mais tempo

**Qualidade do DOCX gerado**
A montagem parágrafo a parágrafo preserva o conteúdo mas perde formatação avançada do template (negrito inline, recuos específicos, numeração de itens). Com mais tempo, implementaria uma abordagem de substituição de variáveis por marcadores no template (`{{nome_cliente}}`, `{{cid}}`) em vez de regenerar todos os parágrafos via IA.

**Retry e resiliência**
O pipeline falha completamente se qualquer chamada à OpenAI retornar erro ou timeout. Adicionaria retry com backoff exponencial e a possibilidade de retomar o pipeline a partir da última etapa concluída, salvando os resultados intermediários em disco.

**Validação do DOCX gerado**
Não há verificação automática de que a petição gerada está juridicamente coerente — apenas que tem o número certo de parágrafos. Um passo adicional de revisão automática (pedir para a IA avaliar o próprio output) aumentaria a confiabilidade antes da revisão humana.

**Autenticação e multiusuário**
A aplicação atual não tem autenticação. Em produção, seria necessário isolar os documentos e petições por usuário/advogado, com controle de acesso e histórico de casos.

**Custo por execução**
Cada pipeline consome várias chamadas ao GPT-4o (OCR por página, validação, estruturação, classificação, base jurídica, geração). Valeria cachear os resultados das etapas intermediárias e avaliar se etapas como classificação e base jurídica podem usar modelos menores (GPT-4o-mini) sem perda relevante de qualidade.

**Testes automatizados**
O projeto não tem testes. Com mais tempo, escreveria testes unitários para as etapas de parsing e classificação (com fixtures de OCR pré-gravado) e um teste de integração end-to-end com um caso de documento sintético.
