import logging
from decimal import Decimal

from service_objects.fields import MultipleFormField
from service_objects.services import Service
from django import forms
from engine.models import Journal_transaction_type, Journal, Posting, AssetType, Account, OperationAccount
from django.forms.models import model_to_dict
from engine.services.account_services import DwhAccountAmountService
from sqs_services.services import SqsService

CUMPLO_COST_ACCOUNT= 1

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
    investment_costs = MultipleFormField(InvestmentCostForm, required=False)
    external_operation_id = forms.IntegerField(required=True)
    asset_type = forms.IntegerField(required=True)

    def process(self):
        #TODO: modificar este valor en duro
        transaction_type = 4 #Financiamiento de operación por Inversión
        #Get Data
        account = self.cleaned_data['account']
        investment_id = self.cleaned_data['investment_id']
        total_amount = self.cleaned_data['total_amount']
        investment_amount = self.cleaned_data['investment_amount']
        investment_costs = self.cleaned_data['investment_costs']
        external_operation_id  = self.cleaned_data['external_operation_id']
        asset_type = self.cleaned_data['asset_type']


        #Get and Process Data
        #TODO: definir transacción de financimiento
        journal_transaction = Journal_transaction_type.objects.get(id=transaction_type)
        from_account = Account.objects.get(id=account)

        to_operation_account = OperationAccount.objects.get(external_account_id=external_operation_id)

        asset_type = AssetType.objects.get(id=asset_type)
        #Traigo la cuenta de cumplo asesorias
        cumplo_cost_account = Account.objects.get(id=CUMPLO_COST_ACCOUNT)



        #Create Data
        ################################################################################################################
        ################################################################################################################


        #Creacion de asiento
        journal = Journal.objects.create(batch=None, gloss=journal_transaction.description, journal_transaction=journal_transaction)


        #Descuento a la cuenta del inversionista
        posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal,
                                              amount=(Decimal(total_amount) * -1))


        # Asignacion de inversionista a operacion
        posting_to = Posting.objects.create(account=to_operation_account, asset_type=asset_type, journal=journal,
                                            amount=Decimal(investment_amount))


        # asignacion de inversionista a costos cumplo
        if investment_costs:
            for investment_cost in investment_costs:
                # asignacion de inversionista a costos cumplo
                print("investment_cost")
                print(investment_cost)

                if investment_cost.cleaned_data['type'] == 1:

                    posting_to = Posting.objects.create(account=cumplo_cost_account, asset_type=asset_type, journal=journal,
                                                    amount=Decimal(investment_cost.cleaned_data['amount']))

                else:
                    print("Error")

            DwhAccountAmountService.execute(
                {
                    'account_id': from_account.id
                }
            )

            sqs = SqsService(json_data={"result": True,
                                        "message": "TODO OK",
                                        "investment_id": investment_id,
                                        "investor_type": from_account.external_account_type.id
                                        })
            sqs.push('response-engine-pay-investment')

        return model_to_dict(journal)