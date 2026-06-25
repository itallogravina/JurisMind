import os
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/drive.file"]
REDIRECT_URI = "http://localhost:8501"


def _client_config() -> dict:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise EnvironmentError(
            "Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env"
        )
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }


def get_auth_url() -> str:
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    return auth_url


def exchange_code(code: str):
    """Troca o code OAuth pelo objeto de credenciais."""
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    return flow.credentials


def upload_to_drive(docx_path: str | Path, title: str, credentials) -> str:
    """
    Faz upload do DOCX para o Google Drive do usuário como Google Doc.
    Retorna a URL do documento criado.
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    drive = build("drive", "v3", credentials=credentials)

    media = MediaFileUpload(
        str(docx_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    uploaded = drive.files().create(
        body={
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        },
        media_body=media,
        fields="id, webViewLink",
    ).execute()

    return uploaded["webViewLink"]


def is_configured() -> bool:
    return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
