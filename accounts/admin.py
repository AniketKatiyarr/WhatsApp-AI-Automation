from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Business & Integrations",
            {
                "fields": (
                    "business_name",
                    "business_type",
                    "api_key",
                    "whatsapp_token",
                    "whatsapp_phone_number_id",
                )
            },
        ),
    )
    list_display = ("email", "business_name", "is_staff", "is_active")
    ordering = ("email",)

