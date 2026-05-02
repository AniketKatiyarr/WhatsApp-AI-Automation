from rest_framework import permissions, viewsets

from .models import MessageLog
from .serializers import MessageLogSerializer


class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageLog.objects.filter(business=self.request.user).order_by("-timestamp")

