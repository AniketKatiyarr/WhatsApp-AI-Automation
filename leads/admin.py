from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("business", "name", "phone", "interest", "intent", "created_at")
    search_fields = ("name", "phone", "interest", "business__email", "business__business_name")
    list_filter = ("intent",)

