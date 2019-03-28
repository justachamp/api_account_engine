from decimal import Decimal

from service_objects.services import Service
from django import forms
from engine.models import JournalTransactionType, Journal, Posting, AssetType, Account, OperationAccount
from django.forms.models import model_to_dict


class TransferToOperationAccountService(Service):
    journal_transaction = forms.IntegerField(required=True)#Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
    from_account = forms.CharField(required=True)#Account.objects.get(id=validated_data['from_account'])
    to_account = forms.CharField(required=True)#Account.objects.get(id=validated_data['to_account'])
    asset_type = forms.IntegerField(required=True)#AssetType.objects.get(id=validated_data['asset_type'])
    amount = forms.DecimalField(required=True)#AssetType.objects.get(id=validated_data['asset_type'])

    def process(self):
        journal_transaction_input = self.cleaned_data['journal_transaction']
        from_account_input = self.cleaned_data['from_account']
        to_account_input = self.cleaned_data['to_account']
        amount_input = self.cleaned_data['amount']
        asset_type_input = self.cleaned_data['asset_type']

        # Get Data for proccess
        journal_transaction_data=JournalTransactionType.objects.get(id=journal_transaction_input)
        from_account_data= Account.objects.get(external_account_id=from_account_input)
        to_operation_account_data = OperationAccount.objects.get(external_account_id=to_account_input)
        asset_type_data = AssetType.objects.get(id=asset_type_input)

        #Generate Data
        journal_for_operation_transfer = Journal.objects.create(batch=None, gloss=journal_transaction_data.description, journal_transaction=journal_transaction_data)
        posting_from = Posting.objects.create(account=from_account_data, asset_type=asset_type_data, journal=journal_for_operation_transfer,
                                              amount=(Decimal(amount_input)*-1))

        posting_to = Posting.objects.create(account=to_operation_account_data, asset_type=asset_type_data, journal=journal_for_operation_transfer,
                                            amount=Decimal(amount_input))

        # Create collecting record

        return {"from":posting_from, "to":posting_to}




