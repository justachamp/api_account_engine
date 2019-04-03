from service_objects.services import Service
from django import forms
from engine.models import JournalTransactionType, Journal, Posting, AssetType, Account, DWHBalanceAccount, BankAccount
from django.forms.models import model_to_dict
from service_objects.fields import MultipleFormField, ModelField
from django.db.models import Sum
import logging
from django.db.models import F


class BankRegistryService(Service):
    account = forms.IntegerField(required=True)
    bank_account_number = forms.IntegerField(required=True)
    account_notification_email = forms.EmailField(required=True)
    bank_code = forms.IntegerField(required=True)
    account_bank_type = forms.IntegerField(required=True)
    account_holder_name = forms.IntegerField(required=True)
    account_holder_document_number = forms.IntegerField(required=True)

    def process(self):

        # Get Datas
        account_id = self.cleaned_data['account']
        bank_account_number = self.cleaned_data['bank_account_number']
        account_notification_email = self.cleaned_data['account_notification_email']
        bank_code = self.cleaned_data['bank_code']
        account_bank_type = self.cleaned_data['account_bank_type']
        account_holder_name = self.cleaned_data['account_holder_name']
        account_holder_document_number = self.cleaned_data['account_holder_document_number']

        account = Account.objects.get(id=account_id)

        bank_account = BankAccount()
        bank_account.account = account
        bank_account.bank_account_number = bank_account_number
        bank_account.account_notification_email = account_notification_email
        bank_account.bank_code = bank_code
        bank_account.account_bank_type = account_bank_type
        bank_account.save()

        return model_to_dict(bank_account)


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







