from service_objects.services import Service
from django import forms
from engine.models import Journal_transaction_type, Journal, Posting, AssetType, Account
from django.forms.models import model_to_dict


class RealToVirtualDepositService(Service):
    db_transaction = True
    real_account_id = forms.IntegerField(required=True)
    virtual_account_id = forms.IntegerField(required=True)
    asset_type_id = forms.IntegerField(required=True)
    amount = forms.DecimalField(required=True, max_digits=20, decimal_places=5)
    transaction_type = forms.IntegerField(required=True)

    def process(self):
        real_account_id_input = self.cleaned_data['real_account_id']
        virtual_account_id_input = self.cleaned_data['virtual_account_id']
        asset_type_id_input = self.cleaned_data['asset_type_id']
        amount_input = self.cleaned_data['amount']
        transaction_type_input = self.cleaned_data['transaction_type']

        # Get Datas
        transaction_type = Journal_transaction_type.objects.filter(id=transaction_type_input)[0:1].get()
        asset_type = AssetType.objects.get(id=asset_type_id_input)
        account = Account.objects.get(id=virtual_account_id_input)

        # Create collecting record
        journal = Journal.objects.create(journal_transaction=transaction_type, gloss=transaction_type.description,
                                         batch=None)

        posting_data = Posting.objects.create(account=account, journal=journal, amount=amount_input,
                                              asset_type=asset_type)

        return posting_data


