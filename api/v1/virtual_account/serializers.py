from rest_framework import serializers
from engine.models.journals import Journal, Journal_transaction_type
from engine.models.postings import Posting,AssetType
from engine.models.accounts import Account


from ..postings.serializers import PostingSerializer
from rest_framework.renderers import JSONRenderer
import json

from django.db import IntegrityError
# from apiUserAdminMex.exceptions.cumplo_exception import *
from django.core.exceptions import ObjectDoesNotExist


class VirtualAccountDepositSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField(required=True)
    real_account = serializers.IntegerField(required=True)
    virtual_account = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)

    def create(self, validated_data):
        print("Flag 1")
        transaction_type = Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
        asset_type = AssetType.objects.get(id=validated_data['asset_type'])
        account = Account.objects.get(id=validated_data['virtual_account'])
        print("Flag 2")

        journal = Journal.objects.create(journal_transaction=transaction_type, gloss="", batch=None)
        print("Flag 3")
        print(str(journal))




        posting = Posting.objects.create(account=account, journal=journal, amount=validated_data['amount'], asset_type=asset_type)








        return journal




    def update(self, instance, validated_data):
        pass
