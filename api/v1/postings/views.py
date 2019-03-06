from rest_framework.viewsets import ModelViewSet
from engine.models.postings import Posting, AssetType
from .serializers import  AssetTypeSerializer
from engine.serializers.posting import PostingSerializer


class AssetTypeViewSet(ModelViewSet):
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer


class PostingViewSet(ModelViewSet):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
