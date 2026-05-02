from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("business", "question", "updated_at")
    search_fields = ("question", "answer", "business__email", "business__business_name")

