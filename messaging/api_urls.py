from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import MessageLogViewSet

router = DefaultRouter()
router.register("messages", MessageLogViewSet, basename="messages")

urlpatterns = [path("", include(router.urls))]

