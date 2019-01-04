from rest_framework import serializers
from engine.models.account import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"
