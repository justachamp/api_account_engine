from rest_framework import serializers
from engine.models.journal import AssetType


class AssetTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetType
        fields = "__all__"
