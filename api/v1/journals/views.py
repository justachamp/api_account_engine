from rest_framework.viewsets import ModelViewSet
from engine.models.journals import Journal, JournalTransactionType
from .serializers import JournalSerializer, JournalTransactionTypeSerializer

class JournalViewSet(ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer


class JournalTransactionTypeViewSet(ModelViewSet):
    queryset = JournalTransactionType.objects.all()
    serializer_class = JournalTransactionTypeSerializer


