from rest_framework import serializers
from engine.models.postings import Posting


class PostingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Posting
        fields = "__all__"
