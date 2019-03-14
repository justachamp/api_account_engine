from rest_framework import serializers
from engine.models.accounts import Account, OperationAccount, AccountType
from engine.services.account_services import BalanceAccountService


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class OperationAccountSerializer(serializers.Serializer):
    external_account_id = serializers.CharField(required=True, max_length=150)
    name = serializers.CharField(required=True, max_length=150)
    financing_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)

    #TODO: Ver tema de manejo de error como respuesta de Backend
    def create(self, validated_data):
        try:
            create_operation = OperationAccount.objects.create(external_account_id=validated_data['external_account_id'],
                                                               name=validated_data['name'],
                                                               financing_amount=validated_data['financing_amount'],
                                                               external_account_type_id=3)
            return create_operation
        except Exception as e:
            raise e

    def update(self, instance, validated_data):
        pass


class BalanceAccountSerializer(serializers.Serializer):
    external_account_id = transaction_type = serializers.CharField(required=True, max_length=150)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        balance_account = BalanceAccountService.execute(
            {
                "external_account_id": validated_data['external_account_id']
            }
        )
        return balance_account
