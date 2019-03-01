from rest_framework import serializers
from engine.models.journals import Journal, Journal_transaction_type



class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = "__all__"


class JournalTransactionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal_transaction_type
        fields = "__all__"
