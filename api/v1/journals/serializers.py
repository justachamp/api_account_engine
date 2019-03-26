from rest_framework import serializers
from engine.models.journals import Journal, JournalTransactionType



class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = "__all__"


class JournalTransactionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalTransactionType
        fields = "__all__"
