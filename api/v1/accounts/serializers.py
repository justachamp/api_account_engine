from rest_framework import serializers
from engine.models.accounts import Account, OperationAccount, AccountType
from engine.services.account_services import BalanceAccountService


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = "__all__"


class OperationAccountSerializer(serializers.Serializer):
    operation_id  = serializers.CharField(required=True, source='external_account_id', max_length=150)
    financing_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    requester_id = serializers.IntegerField(required=True, source='requester_account_id')


    def validate(self, data):
        try:
            Account.objects.get(external_account_id=data['requester_account_id'],
                                external_account_type_id=1)

            operation = OperationAccount.objects.filter(external_account_id=data['external_account_id'])
            if operation.exists():
                raise serializers.ValidationError("external_account_id ya ingresado")

            if data['financing_amount'] < 1:
                raise serializers.ValidationError("Monto de financiamiento Insuficiente ")

            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        print(str(validated_data))

        requester = Account.objects.get(external_account_id=validated_data['requester_account_id'],
                            external_account_type_id=1)

        name = "Operacion "+str(validated_data['external_account_id'])
        create_operation = OperationAccount.objects.create(external_account_id=validated_data['external_account_id'],
                                                           name=name,
                                                           requester_account=requester,
                                                           financing_amount=validated_data['financing_amount'],
                                                           external_account_type_id=3)
        return create_operation

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
