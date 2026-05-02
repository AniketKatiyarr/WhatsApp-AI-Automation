import requests


class WhatsAppSendError(RuntimeError):
    pass


def send_whatsapp_text_message(*, whatsapp_token: str, phone_number_id: str, to_phone: str, text: str) -> dict:
    """
    Sends a text message via Meta WhatsApp Cloud API.

    API docs: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages
    """

    token = (whatsapp_token or "").strip()
    if not token:
        raise WhatsAppSendError("Missing WhatsApp token for business.")
    if not phone_number_id:
        raise WhatsAppSendError("Missing WhatsApp phone_number_id for business.")

    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}
    if resp.status_code >= 400:
        raise WhatsAppSendError(f"WhatsApp send failed ({resp.status_code}): {data}")
    return data

