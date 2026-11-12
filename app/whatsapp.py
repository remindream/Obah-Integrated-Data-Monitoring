import hashlib
import hmac

import httpx

from app import config


def signature_is_valid(body: bytes, header: str | None) -> bool:
    """Check Meta's X-Hub-Signature-256 header against the app secret."""
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(config.WA_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def send_text(to: str, text: str) -> None:
    url = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}/{config.WA_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:4096]},
    }
    response = httpx.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {config.WA_ACCESS_TOKEN}"},
        timeout=30,
    )
    response.raise_for_status()
