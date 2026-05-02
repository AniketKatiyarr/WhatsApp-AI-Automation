import hashlib
import hmac
import json
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Conversation, MessageLog
from .tasks import process_incoming_message


User = get_user_model()


def _verify_meta_signature(request) -> bool:
    """
    Meta sends X-Hub-Signature-256: sha256=<hex_digest>
    We validate against the raw request.body using META_APP_SECRET.
    """

    app_secret = settings.META_APP_SECRET
    if not app_secret:
        # If no secret configured, we can't validate. In production, require it.
        return True

    header = request.headers.get("X-Hub-Signature-256", "")
    if not header.startswith("sha256="):
        return False
    their_sig = header.split("sha256=", 1)[1].strip()
    mac = hmac.new(app_secret.encode("utf-8"), msg=request.body, digestmod=hashlib.sha256)
    our_sig = mac.hexdigest()
    return hmac.compare_digest(their_sig, our_sig)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    """
    Single endpoint per spec: /webhook/
    - GET: verification handshake (hub.challenge)
    - POST: receive inbound messages
    """

    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge or "", status=200)
        return HttpResponse("Verification failed", status=403)

    if not _verify_meta_signature(request):
        return HttpResponse("Invalid signature", status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponse("Invalid JSON", status=400)

    # Typical payload path:
    # entry[].changes[].value.metadata.phone_number_id
    # entry[].changes[].value.messages[] (inbound)
    try:
        change = payload["entry"][0]["changes"][0]["value"]
        metadata = change.get("metadata", {})
        phone_number_id = str(metadata.get("phone_number_id") or "")
    except Exception:
        return JsonResponse({"ok": True})  # Ignore unknown payloads safely

    business = None
    if phone_number_id:
        business = User.objects.filter(whatsapp_phone_number_id=phone_number_id).first()
    if not business:
        # If we can't map, accept (avoid webhook retries), but do not process.
        return JsonResponse({"ok": True, "ignored": "unknown_business"})

    messages = change.get("messages") or []
    if not messages:
        return JsonResponse({"ok": True, "ignored": "no_messages"})

    msg = messages[0]
    from_phone = str(msg.get("from") or "")
    text = (msg.get("text") or {}).get("body") or ""
    ts = msg.get("timestamp")
    try:
        ts_dt = datetime.fromtimestamp(int(ts), tz=timezone.utc) if ts else datetime.now(tz=timezone.utc)
    except Exception:
        ts_dt = datetime.now(tz=timezone.utc)

    conversation, _ = Conversation.objects.get_or_create(business=business, phone=from_phone)
    conversation.last_message_at = ts_dt
    conversation.save(update_fields=["last_message_at"])

    log = MessageLog.objects.create(
        business=business,
        conversation=conversation,
        phone=from_phone,
        inbound_message=text,
        outbound_response="",
        timestamp=ts_dt,
        raw_payload=payload,
        status="received",
    )
    process_incoming_message.delay(log.id)
    return JsonResponse({"ok": True})

