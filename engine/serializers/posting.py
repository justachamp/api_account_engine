from rest_framework import serializers
from engine.models.postings import Posting


class PostingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Posting
        fields = ['amount']
