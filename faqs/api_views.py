from rest_framework import permissions, viewsets

from .models import FAQ
from .serializers import FAQSerializer


class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FAQ.objects.filter(business=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(business=self.request.user)

