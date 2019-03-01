from rest_framework import serializers
from engine.models.accounts import Account, OperationAccount


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"

class OperationAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationAccount
        fields = "__all__"
