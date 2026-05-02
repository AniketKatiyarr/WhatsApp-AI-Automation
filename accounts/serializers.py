from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "business_name",
            "business_type",
            "api_key",
            "whatsapp_token",
            "whatsapp_phone_number_id",
        )
        extra_kwargs = {
            "api_key": {"write_only": True, "required": False, "allow_blank": True},
            "whatsapp_token": {"write_only": True, "required": False, "allow_blank": True},
        }

