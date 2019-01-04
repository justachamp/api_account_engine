from rest_framework.viewsets import ModelViewSet
from engine.models.postings import Posting
from .serializers import PostingSerializer


class PostingViewSet(ModelViewSet):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
