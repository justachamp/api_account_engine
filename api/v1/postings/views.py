from rest_framework.viewsets import ModelViewSet
from engine.models.postings import Posting, AssetType
from .serializers import PostingSerializer, AssetTypeSerializer


class AssetTypeViewSet(ModelViewSet):
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer


class PostingViewSet(ModelViewSet):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
