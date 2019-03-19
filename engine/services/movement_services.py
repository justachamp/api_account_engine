import logging
from decimal import Decimal

from service_objects.fields import MultipleFormField
from service_objects.services import Service
from django import forms
from engine.models import Journal_transaction_type, Journal, Posting, AssetType, Account, OperationAccount
from django.forms.models import model_to_dict


class FinancingOperationTransaction(Service):

    external_account_id = forms.CharField(required=True, max_length=150)
    external_account_type = forms.IntegerField(required=True)

    def process(self):

        external_account_id_input = self.cleaned_data['external_account_id']
        external_account_type_input = self.cleaned_data['external_account_type']

        # Get Data for proccess
        account = Account.objects.get(external_account_id=external_account_id_input,external_account_type_id=external_account_type_input)
        account_posting= Posting.objects.filter(account=account)

        # Create collecting record
        list_posting=[]
        for posting in account_posting:
            list_posting.append(model_to_dict(posting))

        return list_posting


# Get data for proccess
journal_transaction = Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
from_account = Account.objects.get(external_account_id=validated_data['from_account']['external_account_id'],
                                   external_account_type_id=validated_data['from_account'][
                                       'external_account_type'])
to_account = OperationAccount.objects.get(external_account_id=validated_data['to_operation_account'],
                                          external_account_type_id=3)
asset_type = AssetType.objects.get(id=validated_data['asset_type'])

account_posting_operation_amount = Posting.objects.filter(account=to_account).aggregate(Sum('amount'))
posting_operation_amount = Posting.objects.filter(account=to_account)

# Create data for proccess
journal = Journal.objects.create(batch=None, gloss="", journal_transaction=journal_transaction)
posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal,
                                      amount=(Decimal(validated_data['amount']) * -1))
posting_to = Posting.objects.create(account=to_account, asset_type=asset_type, journal=journal,
                                    amount=Decimal(validated_data['amount']))