import logging
from decimal import Decimal
from django.conf import settings

from service_objects.fields import MultipleFormField, ModelField
from service_objects.services import Service
from django import forms
from engine.models import JournalTransactionType, Journal, Posting, AssetType, Account, OperationAccount
from django.forms.models import model_to_dict
from django.db.models import Sum
from engine.services.account_services import DwhAccountAmountService
from sqs_services.services import SqsService
from enum import Enum

CUMPLO_COST_ACCOUNT = 1


class CumploService(Service):
    pass


class GetClientTransaction(CumploService):
    external_account_id = forms.CharField(required=True, max_length=150)
    external_account_type = forms.IntegerField(required=True)

    def process(self):
        external_account_id_input = self.cleaned_data['external_account_id']
        external_account_type_input = self.cleaned_data['external_account_type']

        # Get Data for proccess
        account = Account.objects.get(external_account_id=external_account_id_input,
                                      external_account_type_id=external_account_type_input)
        account_posting = Posting.objects.filter(account=account)

        # Create collecting record
        list_posting = []
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
        journal_transaction_data = JournalTransactionType.objects.get(id=journal_transaction_input)
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
        journal_transaction_data = JournalTransactionType.objects.get(id=journal_transaction_input)
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


Categories = (
    ('REQUESTER', 'REQUESTOR'),
    ('INVESTOR', 'INVESTOR'),
    ('PAYER', 'PAYER')
)


class BillinPropertiesForm(forms.Form):
    billable = forms.BooleanField(required=True)
    billing_entity = forms.ChoiceField(required=True, choices=Categories)


class SubAccountForm(forms.Form):
    account_type = forms.IntegerField(required=True)
    account_name = forms.CharField(required=True)


class DestinationAccountForm(forms.Form):
    account_type = forms.IntegerField(required=True)
    account_name = forms.CharField(required=True)
    sub_account = SubAccountForm()


class AccountEnginePropertiesForm(forms.Form):
    destination_account = DestinationAccountForm()


class CostForm(forms.Form):
    amount = forms.DecimalField(required=True)
    billing_properties = BillinPropertiesForm()
    #account_engine_properties = AccountEnginePropertiesForm


class FinanceOperationByInvestmentTransaction(Service):
    account = forms.IntegerField(required=True)
    investment_id = forms.IntegerField(required=True)
    total_amount = forms.DecimalField(required=True)
    investment_amount = forms.DecimalField(required=True)
    investment_costs = MultipleFormField(CostForm, required=False)
    external_operation_id = forms.IntegerField(required=True)
    asset_type = forms.IntegerField(required=True)

    def process(self):
        # TODO: modificar este valor en duro
        transaction_type = 4  # Financiamiento de operación por Inversión
        # Get Data
        account = self.cleaned_data['account']
        investment_id = self.cleaned_data['investment_id']
        total_amount = self.cleaned_data['total_amount']
        investment_amount = self.cleaned_data['investment_amount']
        investment_costs = self.cleaned_data['investment_costs']
        external_operation_id = self.cleaned_data['external_operation_id']
        asset_type = self.cleaned_data['asset_type']

        # Get and Process Data
        # TODO: definir transacción de financimiento
        journal_transaction = JournalTransactionType.objects.get(id=transaction_type)
        from_account = Account.objects.get(id=account)

        to_operation_account = OperationAccount.objects.get(external_account_id=external_operation_id)

        asset_type = AssetType.objects.get(id=asset_type)
        # Traigo la cuenta de cumplo asesorias
        cumplo_cost_account = Account.objects.get(id=CUMPLO_COST_ACCOUNT)

        # Create Data
        ################################################################################################################
        ################################################################################################################

        # Creacion de asiento
        journal = Journal.objects.create(batch=None, gloss=journal_transaction.description,
                                         journal_transaction=journal_transaction)

        # Descuento a la cuenta del inversionista
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

            # TODO: Llamar al modulo de facturación

            # if investment_cost.cleaned_data['type'] == 1:
            #
            #     posting_to = Posting.objects.create(account=cumplo_cost_account, asset_type=asset_type, journal=journal,
            #                                         amount=Decimal(investment_cost.cleaned_data['amount']))
            #
            # else:
            #     print("Error")

        DwhAccountAmountService.execute(
            {
                'account_id': from_account.id
            }
        )
        if settings.DEBUG and settings.DEBUG != True:
            print("Enviando a SQS")
            sqs = SqsService(json_data={"result": True,
                                        "message": "TODO OK",
                                        "investment_id": investment_id,
                                        "investor_type": 1
                                        })
            sqs.push('response-engine-pay-investment')
        else:
            print("No se envia a SQS")


        return model_to_dict(journal)


class RequesterPaymentFromOperation(Service):
    account = forms.IntegerField(required=True)
    total_amount = forms.DecimalField(required=True)
    transfer_amount = forms.DecimalField(required=True)
    external_operation_id = forms.IntegerField(required=True)
    asset_type = forms.IntegerField(required=True)
    requester_costs = MultipleFormField(CostForm, required=False)

    # Validaciones que implica la operacion de pagar al solicitane

    # 1- que la operacion esté financiada
    # 2- que la operacion tenga suficiente financiamiento para pagar al solicitante y todos los costos asociados
    # 3- que los costos mas el monto a transferir sean iguales a el monto total de la transferencia
    # 4- que los costos no sean mayor que el monto a transferir al solicitante

    def clean(self):
        cleaned_data = super().clean()

        total_amount = cleaned_data.get("total_amount")
        transfer_amount = cleaned_data.get("transfer_amount")
        external_operation_id = cleaned_data.get("external_operation_id")
        operation_data = OperationAccount.objects.get(external_account_id=external_operation_id)
        requester_costs = cleaned_data.get("requester_costs")

        operation_financing_total_amount = Posting.objects.filter(account=operation_data).aggregate(Sum('amount'))

        # 2- que la operacion tenga suficiente financiamiento para pagar al solicitante y todos los costos asociados

        if operation_financing_total_amount['amount__sum'] is None or operation_financing_total_amount[
            'amount__sum'] < total_amount:
            raise forms.ValidationError(
                "La operacion No tiene Financiamiento suficiente para pagar el total de la transacción")

        # 3- que los costos mas el monto a transferir sean iguales a el monto total de la transferencia
        total_amount_cost = 0
        for requester_cost in requester_costs:
        #     # asignacion de inversionista a costos cumplo

            requester_cost_amount = requester_cost.clean()
            print("!!!!!!!!!!!requester_cost['amount']")
            print(requester_cost_amount.get('amount'))

            total_amount_cost = total_amount_cost + requester_cost_amount.get('amount')

        if total_amount_cost + transfer_amount != total_amount:
            raise forms.ValidationError("Los montos no coinciden")

        # 4- que los costos no sean mayor que el monto a transferir al solicitante

        if total_amount_cost > transfer_amount:
            raise forms.ValidationError(
                "Los costos asociados al pago son mayores que el monto a transferir al solicitante")

    def process(self):
        # TODO: modificar este valor en duro

        if self.is_valid():
            transaction_type = 5  # Pago a solicitante
            # Get Data
            account = self.cleaned_data['account']
            total_amount = self.cleaned_data['total_amount']
            transfer_amount = self.cleaned_data['transfer_amount']
            external_operation_id = self.cleaned_data['external_operation_id']
            requester_costs = self.cleaned_data['requester_costs']
            asset_type = self.cleaned_data['asset_type']

            # Get and Process Data
            # TODO: definir transacción de Pago a solicitante
            journal_transaction = JournalTransactionType.objects.get(id=transaction_type)
            from_account = OperationAccount.objects.get(external_account_id=external_operation_id)

            to_requester_account = Account.objects.get(id=external_operation_id)

            asset_type = AssetType.objects.get(id=asset_type)

            # Traigo la cuenta de cumplo asesorias
            cumplo_cost_account = Account.objects.get(id=CUMPLO_COST_ACCOUNT)

            # Create Data
            ################################################################################################################
            ################################################################################################################

            # Creacion de asiento
            journal = Journal.objects.create(batch=None, gloss=journal_transaction.description,
                                             journal_transaction=journal_transaction)

            # Descuento a la cuenta de operacion por el monto total
            posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal,
                                                  amount=(Decimal(total_amount) * -1))

            # Asignacion de inversionista a operacion
            posting_to = Posting.objects.create(account=to_requester_account, asset_type=asset_type, journal=journal,
                                                amount=Decimal(transfer_amount))

            # TODO: Llamar al modulo de facturación
            # asignacion de inversionista a costos cumplo
            # total_amount_cost = 0
            for requester_cost in requester_costs:
                # asignacion de inversionista a costos cumplo
                #
                print(str(requester_cost))
                billing_properties = requester_cost.cleaned_data['billing_properties']
                print(str(billing_properties))
                billing_entity = billing_properties.cleaned_data['billing_entity']
            #
            #         posting_to = Posting.objects.create(account=cumplo_cost_account, asset_type=asset_type, journal=journal,
            #                                             amount=Decimal(requester_cost.cleaned_data['amount']))
            #
            #
            #     else:
            #         print("Error")
            #
            #     total_amount_cost = total_amount_cost + requester_cost.cleaned_data['amount']
            #
            # if total_amount_cost + transfer_amount != total_amount:
            #     raise Exception("Montos totales no coinciden")

            DwhAccountAmountService.execute(
                {
                    'account_id': from_account.id
                }
            )
            DwhAccountAmountService.execute(
                {
                    'account_id': to_requester_account.id
                }
            )

            # TODO: DEFINIR COLA PARA ENVIAR ENVIAR INFO DE PAGO A SOLICITANTE

            # sqs = SqsService(json_data={"result": True,
            #                             "message": "TODO OK",
            #                             "investment_id": investment_id,
            #                             "investor_type": 1
            #                             })
            # sqs.push('response-engine-pay-investment')

            return model_to_dict(journal_transaction)
        else:
            return self.errors
