import os
import tempfile
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.pipeline import run_pipeline, output_filename
from src.exporters.pdf_exporter import convert_to_pdf
from src.exporters import google_docs as gdocs
from src.exporters.notion_exporter import export_to_notion

load_dotenv()

BASE_DIR = Path(__file__).parent
DEFAULT_TEMPLATE = BASE_DIR / "templates" / "Peticao_MODELO_Auxilio_Doenca_Maria da Silva_2026-06-22.docx"

STAGE_LABELS = {
    "ocr": "Extração de texto (OCR)",
    "validation": "Validação documental",
    "parser": "Estruturação dos dados",
    "classification": "Classificação do benefício",
    "legal_basis": "Base jurídica",
    "template": "Leitura do template",
    "ai_generation": "Montagem da petição",
    "export": "Exportação DOCX",
}

st.set_page_config(page_title="JurisMind", page_icon="⚖️", layout="wide")

# ── Captura callback OAuth do Google ─────────────────────────────────────────
params = st.query_params
if "code" in params and "google_creds" not in st.session_state:
    try:
        creds = gdocs.exchange_code(params["code"])
        st.session_state.google_creds = creds
    except Exception as e:
        st.session_state.google_auth_error = str(e)
    st.query_params.clear()
    st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚖️ JurisMind")
st.caption("Gerador automatizado de petições previdenciárias")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuração")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Sua chave da OpenAI. Armazene no .env para não precisar digitar.",
    )

    st.divider()
    st.subheader("Integrações")

    # Google Docs
    google_connected = "google_creds" in st.session_state
    if gdocs.is_configured():
        if google_connected:
            st.success("✅ Google Docs conectado")
            if st.button("Desconectar Google", use_container_width=True):
                del st.session_state["google_creds"]
                st.rerun()
        else:
            if st.session_state.get("google_auth_error"):
                st.error(f"Erro: {st.session_state.pop('google_auth_error')}")
            try:
                auth_url = gdocs.get_auth_url()
                st.link_button("🔗 Conectar com Google", auth_url, use_container_width=True)
            except Exception as e:
                st.error(str(e))
    else:
        st.markdown("❌ **Google Docs** — configure `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` no `.env`")

    st.divider()

    # Notion
    notion_configured = bool(os.getenv("NOTION_TOKEN") and os.getenv("NOTION_PARENT_PAGE_ID"))
    if notion_configured:
        st.success("✅ Notion configurado")
    else:
        st.markdown("❌ **Notion** — configure `NOTION_TOKEN` e `NOTION_PARENT_PAGE_ID` no `.env`")

# ── Upload ────────────────────────────────────────────────────────────────────
st.subheader("📂 Documentos do Cliente")
uploaded_pdfs = st.file_uploader(
    "Arraste os PDFs ou clique para selecionar",
    type=["pdf"],
    accept_multiple_files=True,
    help="RG, comprovante de residência, carta de indeferimento INSS, laudo médico, CNIS etc.",
)

st.subheader("📄 Template da Petição")
uploaded_template = st.file_uploader(
    "DOCX modelo (opcional — usa o padrão se não enviado)",
    type=["docx"],
)

st.divider()

# ── Processar ─────────────────────────────────────────────────────────────────
can_run = bool(uploaded_pdfs and api_key)
if st.button("🚀 Gerar Petição", type="primary", disabled=not can_run, use_container_width=True):

    client = OpenAI(api_key=api_key)
    tmp_dir = Path(tempfile.mkdtemp())

    try:
        for f in uploaded_pdfs:
            (tmp_dir / f.name).write_bytes(f.read())

        if uploaded_template:
            template_path = tmp_dir / uploaded_template.name
            template_path.write_bytes(uploaded_template.read())
        else:
            template_path = DEFAULT_TEMPLATE

        output_dir = BASE_DIR / "outputs"
        output_dir.mkdir(exist_ok=True)

        with st.status("Processando documentos...", expanded=True) as status_box:
            def on_stage(stage, status, data):
                if status == "success":
                    st.write(f"✅ {STAGE_LABELS.get(stage, stage)}")

            result = run_pipeline(
                docs_dir=tmp_dir,
                template_path=template_path,
                output_path=output_dir / "temp_output.docx",
                client=client,
                on_stage=on_stage,
            )
            status_box.update(label="✅ Petição gerada com sucesso!", state="complete")

        fname = output_filename(result["structured_data"])
        final_docx = output_dir / fname
        shutil.move(str(result["output_path"]), str(final_docx))
        st.session_state.final_docx = str(final_docx)
        st.session_state.result = result
        st.session_state.fname = fname

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

# ── Resultado (persiste entre reruns) ─────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state.result
    final_docx = Path(st.session_state.final_docx)
    fname = st.session_state.fname

    st.success(f"Petição gerada: **{fname}**")
    st.divider()

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.subheader("📋 Validação documental")
        validation = result["validation"]
        if validation.get("faltantes"):
            st.warning(f"Documentos faltantes: {', '.join(validation['faltantes'])}")
        for alerta in validation.get("alertas", []):
            st.info(f"⚠️ {alerta}")
        if not validation.get("faltantes") and not validation.get("alertas"):
            st.success("Todos os documentos validados.")
        for filename, doc_info in validation.get("documentos", {}).items():
            icon = "✅" if doc_info["qualidade"] == "ok" else "⚠️"
            st.markdown(f"{icon} **{doc_info['tipo']}** — {filename}")

    with res_col2:
        st.subheader("🎯 Classificação")
        classification = result["classification"]
        bp = classification.get("beneficio_principal", {})
        st.markdown(f"**Benefício principal:** {bp.get('nome')} ({bp.get('codigo')})")
        st.markdown(f"**Fundamento:** {bp.get('fundamento_legal')}")
        if classification.get("beneficio_subsidiario"):
            bs = classification["beneficio_subsidiario"]
            st.markdown(f"**Subsidiário:** {bs.get('nome')} ({bs.get('codigo')})")
        with st.expander("Ver análise completa"):
            st.write(classification.get("analise", ""))

    with st.expander("👤 Dados extraídos do cliente"):
        sd = result["structured_data"]
        c = sd.get("cliente", {})
        e = sd.get("endereco", {})
        st.json({
            "Nome": c.get("nome"),
            "CPF": c.get("cpf"),
            "RG": c.get("rg"),
            "Nascimento": c.get("data_nascimento"),
            "Profissão": sd.get("profissao"),
            "Endereço": f"{e.get('logradouro')}, {e.get('cidade')}/{e.get('uf')}",
            "Benefício": sd.get("beneficio", {}).get("tipo"),
            "CID": sd.get("saude", {}).get("cid"),
        })

    # ── Exportar ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📥 Abrir ou exportar como")
    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

    with exp_col1:
        with open(final_docx, "rb") as f:
            st.download_button(
                "⬇️ Download DOCX",
                data=f.read(),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

    with exp_col2:
        try:
            pdf_path = convert_to_pdf(final_docx)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    data=f.read(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as ex:
            st.error(f"PDF: {ex}")

    with exp_col3:
        if google_connected:
            if "gdocs_url" not in st.session_state:
                with st.spinner("Enviando para Google Docs..."):
                    try:
                        url = gdocs.upload_to_drive(
                            final_docx,
                            fname.replace(".docx", ""),
                            st.session_state.google_creds,
                        )
                        st.session_state.gdocs_url = url
                    except Exception as ex:
                        st.error(f"Google Docs: {ex}")
            if "gdocs_url" in st.session_state:
                st.link_button("☁️ Abrir no Google Docs", st.session_state.gdocs_url, use_container_width=True)
        else:
            st.button(
                "☁️ Google Docs",
                disabled=True,
                use_container_width=True,
                help="Conecte sua conta Google na barra lateral.",
            )

    with exp_col4:
        if notion_configured:
            if "notion_url" not in st.session_state:
                with st.spinner("Criando página no Notion..."):
                    try:
                        url = export_to_notion(final_docx, fname.replace(".docx", ""))
                        st.session_state.notion_url = url
                    except Exception as ex:
                        st.error(f"Notion: {ex}")
            if "notion_url" in st.session_state:
                st.link_button("📓 Abrir no Notion", st.session_state.notion_url, use_container_width=True)
        else:
            st.button(
                "📓 Notion",
                disabled=True,
                use_container_width=True,
                help="Configure NOTION_TOKEN e NOTION_PARENT_PAGE_ID no .env",
            )

elif not uploaded_pdfs:
    st.info("⬆️ Envie os documentos do cliente para começar.")
