from rest_framework import serializers
from engine.models.journals import Journal, Journal_transaction_type
from engine.models.postings import Posting,AssetType
from engine.models.accounts import Account
from engine.services.account_services import RealToVirtualDepositService


class VirtualAccountDepositSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField(required=True)
    real_account = serializers.CharField(required=True, max_length=150)
    external_account_id = serializers.CharField(required=True, max_length=150)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)

    def validate(self, data):
        Account.objects.get(external_account_id=data['external_account_id'])
        AssetType.objects.get(id=data['asset_type'])
        return data

    def create(self, validated_data):
        destiny_account = Account.objects.get(external_account_id=validated_data['external_account_id'])
        asset_type = AssetType.objects.get(id=validated_data['asset_type'])
        journal_transaction_type = Journal_transaction_type.objects.get(id=validated_data['asset_type'])

        posting = RealToVirtualDepositService.execute(
            {
                "real_account_id": validated_data['real_account'],
                "virtual_account_id": destiny_account.id,
                "asset_type_id": asset_type.id,
                "transaction_type": journal_transaction_type.id,
                "amount": validated_data['amount']
            }
        )

        return posting

    def update(self, instance, validated_data):
        pass
