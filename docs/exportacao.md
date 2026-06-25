# Exportação

Após gerar a petição em DOCX, o sistema oferece quatro destinos de exportação.

---

## DOCX

Disponível sempre. Download direto na interface web ou arquivo salvo em `outputs/` no CLI.

Nome do arquivo gerado: `Peticao_NOME_DO_CLIENTE_YYYY-MM-DD.docx`

---

## PDF

Requer `libreoffice` instalado no sistema (incluído na imagem Docker).

```bash
# Verificar instalação
libreoffice --version
```

Na interface web, o botão "Download PDF" aparece automaticamente se a conversão for bem-sucedida.

---

## Google Docs

Faz upload do DOCX para o Google Drive do usuário como Google Doc nativo.

**Configuração:**

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto e habilite a **Google Drive API**
3. Em "Credenciais", crie um **OAuth 2.0 Client ID** do tipo *Web application*
4. Adicione `http://localhost:8501` como URI de redirecionamento autorizado
5. Copie o Client ID e Client Secret para o `.env`:

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

6. Na interface web, clique em "Conectar com Google" na barra lateral e autorize o acesso.

---

## Notion

Cria uma página no Notion com o conteúdo da petição em blocos de texto.

**Configuração:**

1. Acesse [notion.so/my-integrations](https://www.notion.so/my-integrations) e crie uma integração
2. Copie o token interno
3. Abra a página do Notion onde deseja criar as petições, clique em "..." → "Conexões" → adicione sua integração
4. Copie o ID da página da URL: `notion.so/<workspace>/<PAGE_ID>`
5. Adicione ao `.env`:

```
NOTION_TOKEN=secret_...
NOTION_PARENT_PAGE_ID=...
```
