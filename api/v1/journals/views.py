from rest_framework.viewsets import ModelViewSet
from engine.models.journals import Journal
from .serializers import JournalSerializer


class JournalViewSet(ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
