from django.urls import path

from .webhook_views import webhook

urlpatterns = [
    path("", webhook, name="webhook"),
]

