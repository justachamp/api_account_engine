from rest_framework import serializers
from engine.models.journals import Journal



class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = "__all__"
