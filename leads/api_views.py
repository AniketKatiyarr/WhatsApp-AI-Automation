from rest_framework import permissions, viewsets

from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lead.objects.filter(business=self.request.user).order_by("-created_at")

