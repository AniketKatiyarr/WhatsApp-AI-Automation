from rest_framework import serializers

from .models import MessageLog


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = (
            "id",
            "phone",
            "inbound_message",
            "outbound_response",
            "timestamp",
            "status",
            "error",
        )

