from django.contrib import admin

from .models import Conversation, MessageLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("business", "phone", "last_message_at")
    search_fields = ("phone", "business__email", "business__business_name")


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("business", "phone", "timestamp", "status")
    search_fields = ("phone", "business__email", "inbound_message", "outbound_response")
    list_filter = ("status",)

