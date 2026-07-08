from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
import httpx
import os

load_dotenv(Path(__file__).parent.parent / ".env")

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
DEFAULT_ESCALATION_MESSAGE = (
    "Escalation da L'Oasi di Sabaudia\n\n"
    "L'assistente ha richiesto l'intervento del proprietario. "
    "Controlla la conversazione con l'ospite."
)


def _send_telegram_message(text: str) -> tuple[bool, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_CHAT_ID")

    if not token or not chat_id:
        return False, (
            "Configurazione Telegram mancante "
            "(TELEGRAM_BOT_TOKEN o TELEGRAM_OWNER_CHAT_ID)."
        )

    url = TELEGRAM_API_URL.format(token=token)
    try:
        response = httpx.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=10.0,
        )
        response.raise_for_status()
        return True, "Proprietario notificato su Telegram."
    except httpx.HTTPError as exc:
        return False, f"Errore invio Telegram: {exc}"


@tool
def escalation_tool() -> str:
    """Notifica il proprietario via Telegram per escalation: emergenze, richieste non gestibili o situazioni urgenti."""
    success, detail = _send_telegram_message(DEFAULT_ESCALATION_MESSAGE)
    return detail if success else f"Escalation non riuscita. {detail}"
