from rest_framework import serializers
from engine.models.postings import Posting, AssetType



class AssetTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetType
        fields = "__all__"
