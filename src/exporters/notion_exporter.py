import os
from pathlib import Path
from docx import Document


def _docx_to_blocks(docx_path: str | Path) -> list[dict]:
    """Converte parágrafos do DOCX em blocos Notion."""
    doc = Document(docx_path)
    blocks = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style = p.style.name.lower()

        if "heading 1" in style:
            block_type = "heading_1"
        elif "heading 2" in style:
            block_type = "heading_2"
        else:
            block_type = "paragraph"

        is_bold = any(r.bold for r in p.runs if r.text.strip())

        blocks.append({
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": text[:2000]},
                    "annotations": {"bold": is_bold},
                }]
            },
        })

    return blocks


def export_to_notion(docx_path: str | Path, title: str) -> str:
    """
    Cria uma página no Notion com o conteúdo da petição.
    Requer NOTION_TOKEN e NOTION_PARENT_PAGE_ID no .env.
    Retorna a URL da página criada.
    """
    try:
        from notion_client import Client
    except ImportError:
        raise ImportError("Instale notion-client: pip install notion-client")

    token = os.getenv("NOTION_TOKEN")
    parent_id = os.getenv("NOTION_PARENT_PAGE_ID")

    if not token:
        raise EnvironmentError("NOTION_TOKEN não definida no .env")
    if not parent_id:
        raise EnvironmentError("NOTION_PARENT_PAGE_ID não definida no .env")

    notion = Client(auth=token)
    blocks = _docx_to_blocks(docx_path)

    # Notion limita 100 blocos por request
    page = notion.pages.create(
        parent={"page_id": parent_id},
        properties={"title": {"title": [{"text": {"content": title}}]}},
        children=blocks[:100],
    )

    # Envia blocos restantes em lotes
    page_id = page["id"]
    for i in range(100, len(blocks), 100):
        notion.blocks.children.append(block_id=page_id, children=blocks[i:i + 100])

    return f"https://notion.so/{page_id.replace('-', '')}"
