from django.conf import settings
from django.db import models


class Lead(models.Model):
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leads")
    name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="", db_index=True)
    interest = models.CharField(max_length=255, blank=True, default="")
    intent = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    source_message_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_id}:{self.phone or 'unknown'}:{self.interest}"

