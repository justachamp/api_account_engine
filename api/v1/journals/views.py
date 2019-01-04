from rest_framework.viewsets import ModelViewSet
from engine.models.journals import Journal, AssetType
from .serializers import JournalSerializer, AssetTypeSerializer


class AssetTypeViewSet(ModelViewSet):
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer


class JournalViewSet(ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
