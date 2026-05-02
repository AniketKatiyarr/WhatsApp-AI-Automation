from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include("messaging.api_urls")),
    path("api/", include("faqs.api_urls")),
    path("api/", include("leads.api_urls")),
    path("api/auth/", include("accounts.api_urls")),
    path("webhook/", include("messaging.webhook_urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

