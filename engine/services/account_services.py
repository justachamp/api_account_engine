from service_objects.services import Service
from django import forms
from engine.models import JournalTransactionType, Journal, Posting, AssetType, Account, DWHBalanceAccount
from django.forms.models import model_to_dict
from django.db.models import Sum
import logging
from django.db.models import F


class RealToVirtualDepositService(Service):
    db_transaction = True
    real_account_id = forms.IntegerField(required=True)
    virtual_account_id = forms.IntegerField(required=True)
    asset_type_id = forms.IntegerField(required=True)
    amount = forms.DecimalField(required=True, max_digits=20, decimal_places=5)
    transaction_type = forms.IntegerField(required=True)
    deposit_date = forms.DateField(required=True)

    def process(self):
        try:

            real_account_id_input = self.cleaned_data['real_account_id']
            virtual_account_id_input = self.cleaned_data['virtual_account_id']
            asset_type_id_input = self.cleaned_data['asset_type_id']
            amount_input = self.cleaned_data['amount']
            transaction_type_input = self.cleaned_data['transaction_type']
            deposit_date_input = self.cleaned_data['deposit_date']

            # Get Datas
            transaction_type = JournalTransactionType.objects.filter(id=transaction_type_input)[0:1].get()
            asset_type = AssetType.objects.get(id=asset_type_id_input)
            account = Account.objects.get(id=virtual_account_id_input)

            # Create collecting record
            journal = Journal.objects.create(journal_transaction=transaction_type, gloss=transaction_type.description+", deposit date:"+str(deposit_date_input),
                                             batch=None)

            posting_data = Posting.objects.create(account=account, journal=journal, amount=amount_input,
                                                  asset_type=asset_type)

            logging.getLogger("error_logger").error("Se ha creado ");
            logging.getLogger("error_logger").info("creado el usuario");

            dwh_balance_account = Posting.objects.filter(account=account).aggregate(Sum('amount'))

            DWHBalanceAccount.objects.update_or_create(account=account, defaults={'balance_account_amount': dwh_balance_account['amount__sum']})

            return posting_data
        except Exception as e:
            raise e


class BalanceAccountService(Service):
    external_account_id = forms.CharField(required=True, max_length=150)
    external_account_type_id = forms.IntegerField(required=True)

    def process(self):
        try:
            external_account_id_input = self.cleaned_data['external_account_id']
            external_account_type_id_input = self.cleaned_data['external_account_type_id']

            # Get Datas
            account = Account.objects.get(external_account_id=external_account_id_input, external_account_type_id=external_account_type_id_input)

            balance_account = Posting.objects.filter(account=account).aggregate(
                Sum('amount'))

            return balance_account
        except Exception as e:
            raise e;


class PositiveBalanceAccountService(Service):
    entity_type = forms.IntegerField(required=False)

    def process(self):
        try:

            entity_type = self.cleaned_data['entity_type']
            if entity_type is not None:
            # Get Datas
                positive_balance_accounts = DWHBalanceAccount.objects.values( 'account__name',).filter(balance_account_amount__gt = 0, account__external_account_type=self.cleaned_data['entity_type']).annotate(account_id=F('account__external_account_id'), account_type=F('account__external_account_type'), balance_account=F('balance_account_amount')  )#.extra(select={'blablabla': 'account__external_account_id'})
            else:
                positive_balance_accounts = DWHBalanceAccount.objects.values( 'account__name',).filter(balance_account_amount__gt = 0).annotate(account_id=F('account__external_account_id'), account_type=F('account__external_account_type'), balance_account=F('balance_account_amount')  )#.extra(select={'blablabla': 'account__external_account_id'})


            return positive_balance_accounts
        except Exception as e:
            raise e


class DwhAccountAmountService(Service):

    account_id = forms.CharField(required=True, max_length=150)

    def process(self):
        account_id_input = self.cleaned_data['account_id']
        account_to_update = Account.objects.get(id=account_id_input)
        dwh_balance_account = Posting.objects.filter(account=account_to_update).aggregate(Sum('amount'))
        balance_update=DWHBalanceAccount.objects.update_or_create(account=account_to_update, defaults={
                'balance_account_amount': dwh_balance_account['amount__sum']})

        return balance_update






