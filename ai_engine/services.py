import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.conf import settings

from openai import OpenAI


@dataclass
class AIResult:
    reply: str
    intent: str
    lead: Dict[str, Any]


def _client_for_business(business) -> OpenAI:
    api_key = (getattr(business, "api_key", "") or "").strip() or (settings.OPENAI_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("Missing OpenAI API key (set user.api_key or OPENAI_API_KEY).")
    return OpenAI(api_key=api_key)


def build_system_prompt(business_type: str) -> str:
    return (
        f"You are a helpful assistant for a {business_type}. "
        "Answer professionally and help convert the user into a customer.\n\n"
        "Rules:\n"
        "- Be concise but helpful.\n"
        "- Ask a clarifying question if needed.\n"
        "- If user asks for booking, propose next steps.\n"
        "- If pricing, provide pricing guidance and offer to share details.\n"
    )


def generate_reply_and_lead(
    *,
    business,
    message_text: str,
    recent_context: str = "",
    model: Optional[str] = None,
) -> AIResult:
    """
    Single call that produces:
    - reply (string)
    - intent: inquiry / booking / pricing / general
    - lead: {name?, phone?, interest?}

    We ask for strict JSON output to keep parsing robust.
    """

    client = _client_for_business(business)
    model = model or settings.OPENAI_DEFAULT_MODEL

    system = build_system_prompt(getattr(business, "business_type", "business") or "business")
    user_payload = {
        "message": message_text,
        "recent_context": recent_context,
        "business_name": getattr(business, "business_name", "") or "",
    }

    prompt = (
        "Return ONLY valid JSON with this shape:\n"
        '{\n  "reply": string,\n  "intent": "inquiry"|"booking"|"pricing"|"general",\n'
        '  "lead": {"name": string|null, "phone": string|null, "interest": string|null}\n}\n\n'
        "Use a human WhatsApp tone. If user provides name/phone, capture it. "
        "If not, infer interest from the message.\n\n"
        f"INPUT:\n{json.dumps(user_payload, ensure_ascii=False)}"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    content = (resp.choices[0].message.content or "").strip()

    data: Dict[str, Any] = {}
    try:
        data = json.loads(content)
    except Exception:
        # Fallback: wrap into a minimal structure to avoid failing the pipeline.
        data = {"reply": content or "Thanks! Could you share a bit more detail?", "intent": "general", "lead": {}}

    reply = str(data.get("reply") or "").strip() or "Thanks! Could you share a bit more detail?"
    intent = str(data.get("intent") or "general").strip().lower()
    if intent not in {"inquiry", "booking", "pricing", "general"}:
        intent = "general"
    lead = data.get("lead") if isinstance(data.get("lead"), dict) else {}

    normalized_lead = {
        "name": lead.get("name"),
        "phone": lead.get("phone"),
        "interest": lead.get("interest"),
    }
    return AIResult(reply=reply, intent=intent, lead=normalized_lead)

