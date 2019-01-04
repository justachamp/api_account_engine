from rest_framework.viewsets import ModelViewSet
from engine.models.journal import AssetType
from .serializers import AssetTypeSerializer


class AssetTypeViewSet(ModelViewSet):
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer
