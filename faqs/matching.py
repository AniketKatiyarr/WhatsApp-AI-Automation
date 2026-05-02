from difflib import SequenceMatcher

from .models import FAQ


def best_faq_match(*, business, message: str, threshold: float = 0.78):
    """
    Lightweight FAQ matching for MVP (no embeddings).
    Returns (faq, score) or (None, 0.0)
    """

    message_norm = (message or "").strip().lower()
    if not message_norm:
        return None, 0.0

    best = None
    best_score = 0.0
    for faq in FAQ.objects.filter(business=business).only("id", "question", "answer"):
        q = (faq.question or "").strip().lower()
        score = SequenceMatcher(None, message_norm, q).ratio()
        if score > best_score:
            best_score = score
            best = faq

    if best and best_score >= threshold:
        return best, best_score
    return None, best_score

