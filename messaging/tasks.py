from __future__ import annotations

from celery import shared_task
from django.db import transaction

from ai_engine.services import generate_reply_and_lead
from faqs.matching import best_faq_match
from leads.models import Lead

from .models import MessageLog
from .whatsapp import send_whatsapp_text_message


def _recent_context_for_log(log: MessageLog, limit: int = 6) -> str:
    if not log.conversation_id:
        return ""
    qs = (
        MessageLog.objects.filter(conversation_id=log.conversation_id)
        .order_by("-timestamp")
        .only("inbound_message", "outbound_response", "timestamp")
    )[:limit]
    lines = []
    for m in reversed(list(qs)):
        if m.inbound_message:
            lines.append(f"User: {m.inbound_message}")
        if m.outbound_response:
            lines.append(f"Assistant: {m.outbound_response}")
    return "\n".join(lines)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 5})
def send_whatsapp_reply(self, message_log_id: int, reply_text: str):
    log = MessageLog.objects.select_related("business").get(id=message_log_id)
    business = log.business
    return send_whatsapp_text_message(
        whatsapp_token=business.whatsapp_token,
        phone_number_id=business.whatsapp_phone_number_id,
        to_phone=log.phone,
        text=reply_text,
    )


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def process_incoming_message(self, message_log_id: int):
    log = MessageLog.objects.select_related("business").get(id=message_log_id)
    business = log.business

    MessageLog.objects.filter(id=log.id).update(status="processing", error="")

    try:
        faq, score = best_faq_match(business=business, message=log.inbound_message)
        if faq:
            reply = faq.answer
            intent = "general"
            lead_data = {"interest": faq.question, "name": None, "phone": log.phone}
        else:
            context = _recent_context_for_log(log)
            ai = generate_reply_and_lead(business=business, message_text=log.inbound_message, recent_context=context)
            reply = ai.reply
            intent = ai.intent
            lead_data = ai.lead or {}
            if not lead_data.get("phone"):
                lead_data["phone"] = log.phone

        with transaction.atomic():
            MessageLog.objects.filter(id=log.id).update(outbound_response=reply, status="responded")

            interest = (lead_data.get("interest") or "").strip()
            name = (lead_data.get("name") or "").strip()
            phone = (lead_data.get("phone") or "").strip()
            if interest or name or phone:
                Lead.objects.create(
                    business=business,
                    name=name,
                    phone=phone,
                    interest=interest,
                    intent=intent,
                    source_message_id=log.id,
                )

        send_whatsapp_reply.delay(log.id, reply)
        return {"ok": True}
    except Exception as e:
        MessageLog.objects.filter(id=log.id).update(status="failed", error=str(e))
        raise

