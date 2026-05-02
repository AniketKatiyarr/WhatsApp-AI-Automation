from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import FAQViewSet

router = DefaultRouter()
router.register("faqs", FAQViewSet, basename="faqs")

urlpatterns = [path("", include(router.urls))]

