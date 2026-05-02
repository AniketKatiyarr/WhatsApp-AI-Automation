from django.conf import settings
from django.db import models


class Conversation(models.Model):
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    phone = models.CharField(max_length=32, db_index=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("business", "phone")

    def __str__(self):
        return f"{self.business_id}:{self.phone}"


class MessageLog(models.Model):
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_logs")
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages"
    )
    phone = models.CharField(max_length=32, db_index=True)
    inbound_message = models.TextField()
    outbound_response = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=32,
        default="received",
        choices=(
            ("received", "Received"),
            ("processing", "Processing"),
            ("responded", "Responded"),
            ("failed", "Failed"),
        ),
    )
    error = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.business_id}:{self.phone}@{self.timestamp.isoformat()}"

