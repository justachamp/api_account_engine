import logging
from decimal import Decimal

from service_objects.fields import MultipleFormField
from service_objects.services import Service
from django import forms
from engine.models import Journal_transaction_type, Journal, Posting, AssetType, Account, OperationAccount
from django.forms.models import model_to_dict
from sqs_services.services import SqsService



class CumploService(Service):
    pass


class GetClientTransaction(CumploService):

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


class GetClientVirtualTransaction(Service):
    journal_transaction = forms.IntegerField(required=True)
    from_account = forms.CharField(required=True)
    to_account = forms.CharField(required=True)
    asset_type = forms.IntegerField(required=True)
    amount = forms.DecimalField(required=True)

    def process(self):
        print("Transaction")
        journal_transaction_input = self.cleaned_data['journal_transaction']
        from_account_input = self.cleaned_data['from_account']
        to_account_input = self.cleaned_data['to_account']
        amount_input = self.cleaned_data['amount']
        asset_type_input = self.cleaned_data['asset_type']

        # Get Data for proccess
        journal_transaction_data=Journal_transaction_type.objects.get(id=journal_transaction_input)
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


class GetClientRealTransaction(Service):
    journal_transaction = forms.IntegerField(
        required=True)  # Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
    from_account = forms.CharField(required=True)  # Account.objects.get(id=validated_data['from_account'])
    to_account = forms.CharField(required=True)  # Account.objects.get(id=validated_data['to_account'])
    asset_type = forms.IntegerField(required=True)  # AssetType.objects.get(id=validated_data['asset_type'])
    amount = forms.DecimalField(required=True)  # AssetType.objects.get(id=validated_data['asset_type'])

    def process(self):
        journal_transaction_input = self.cleaned_data['journal_transaction']
        from_account_input = self.cleaned_data['from_account']
        to_account_input = self.cleaned_data['to_account']
        amount_input = self.cleaned_data['amount']
        asset_type_input = self.cleaned_data['asset_type']

        # Get Data for proccess
        journal_transaction_data = Journal_transaction_type.objects.get(id=journal_transaction_input)
        from_account_data = Account.objects.get(external_account_id=from_account_input)
        to_operation_account_data = OperationAccount.objects.get(external_account_id=to_account_input)
        asset_type_data = AssetType.objects.get(id=asset_type_input)

        # Generate Data
        journal_for_operation_transfer = Journal.objects.create(batch=None, gloss=journal_transaction_data.description,
                                                                journal_transaction=journal_transaction_data)
        posting_from = Posting.objects.create(account=from_account_data, asset_type=asset_type_data,
                                              journal=journal_for_operation_transfer,
                                              amount=(Decimal(amount_input) * -1))

        posting_to = Posting.objects.create(account=to_operation_account_data, asset_type=asset_type_data,
                                            journal=journal_for_operation_transfer,
                                            amount=Decimal(amount_input))

        # Create collecting record

        return {"from": posting_from, "to": posting_to}


class InvestmentCostForm(forms.Form):
    type = forms.IntegerField(required=True)
    amount = forms.DecimalField(required=True)


class FinanceOperationByInvestmentTransaction(Service):
    account = forms.IntegerField(required=True)
    investment_id = forms.IntegerField(required=True)
    total_amount = forms.DecimalField(required=True)
    investment_amount = forms.DecimalField(required=True)
    investment_cost = MultipleFormField(InvestmentCostForm)


    def process(self):
        account = self.cleaned_data['account']
        investment_id = self.cleaned_data['investment_id']
        total_amount = self.cleaned_data['total_amount']
        investment_amount = self.cleaned_data['investment_amount']
        investment_cost = self.cleaned_data['investment_cost']

        sqs = SqsService(json_data={"result": True,
                                    "message" : "TODO OK",
                                    "investment_id":3,
                                    "investor_type":1
                                    })
        sqs.push('response-engine-pay-investment')




        #account = Account.objects.get(external_account_id=account)

        return 123
