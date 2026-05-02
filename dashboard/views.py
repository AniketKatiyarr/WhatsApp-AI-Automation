from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from leads.models import Lead
from messaging.models import MessageLog


def landing(request):
    return render(request, "dashboard/landing.html")


@login_required
def home(request):
    user = request.user
    total_messages = MessageLog.objects.filter(business=user).count()
    total_leads = Lead.objects.filter(business=user).count()
    recent_messages = (
        MessageLog.objects.filter(business=user).order_by("-timestamp").select_related("business")[:20]
    )
    return render(
        request,
        "dashboard/home.html",
        {
            "total_messages": total_messages,
            "total_leads": total_leads,
            "recent_messages": recent_messages,
        },
    )


@login_required
def faqs_page(request):
    return render(request, "dashboard/faqs.html")


@login_required
def leads_page(request):
    return render(request, "dashboard/leads.html")

