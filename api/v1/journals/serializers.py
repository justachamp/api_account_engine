from rest_framework import serializers
from engine.models.journals import Journal, AssetType


class AssetTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetType
        fields = "__all__"


class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = "__all__"
