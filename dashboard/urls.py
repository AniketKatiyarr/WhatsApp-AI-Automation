from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.home, name="home"),
    path("faqs/", views.faqs_page, name="faqs"),
    path("leads/", views.leads_page, name="leads"),
]

