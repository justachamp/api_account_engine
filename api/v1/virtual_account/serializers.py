from rest_framework import serializers
from engine.models.journals import Journal, JournalTransactionType
from engine.models.postings import Posting,AssetType
from engine.models.accounts import Account, AccountType
from engine.services.account_services import RealToVirtualDepositService


class VirtualAccountDepositSerializer(serializers.Serializer):
    real_account = serializers.CharField(required=True, max_length=150)
    external_account_id = serializers.CharField(required=True, max_length=150)
    external_account_type = serializers.CharField(required=True, max_length=150)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)
    deposit_date = serializers.DateField(required=True)

    def validate(self, data):
        try:
            Account.objects.get(external_account_id=data['external_account_id'], external_account_type_id=data['external_account_type'])
            AssetType.objects.get(id=data['asset_type'])
            return data
        except Exception as e:
            raise serializers.ValidationError(e)

    def create(self, validated_data):
        destiny_account = Account.objects.get(external_account_id=validated_data['external_account_id'],
                                              external_account_type_id=validated_data['external_account_type'])
        asset_type = AssetType.objects.get(id=validated_data['asset_type'])
        journal_transaction_type = JournalTransactionType.objects.get(id=validated_data['asset_type'])
        posting = RealToVirtualDepositService.execute(
            {
                "real_account_id": validated_data['real_account'],
                "virtual_account_id": destiny_account.id,
                "asset_type_id": asset_type.id,
                "transaction_type": 1,
                "amount": validated_data['amount'],
                "deposit_date" : validated_data['deposit_date']
            }
        )

        return posting

    def update(self, instance, validated_data):
        pass



