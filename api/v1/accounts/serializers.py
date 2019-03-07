from rest_framework import serializers
from engine.models.accounts import Account, OperationAccount
from engine.services.account_services import BalanceAccountService


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"


class OperationAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationAccount
        fields = "__all__"


class BalanceAccountSerializer(serializers.Serializer):
    external_account_id = transaction_type = serializers.CharField(required=True, max_length=150)


    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        balance_account=BalanceAccountService.execute(
            {
                "external_account_id": validated_data['external_account_id']
            }
        )
        return balance_account





