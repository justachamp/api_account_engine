from rest_framework import serializers
from engine.models.journals import IncomeType


class IncomeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomeType
        fields = "__all__"
