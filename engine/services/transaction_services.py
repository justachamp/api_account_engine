import logging
from decimal import Decimal
from django.conf import settings

from service_objects.fields import MultipleFormField, ModelField
from service_objects.services import Service
from django import forms

from accountengine.utils import generate_sns_topic
from engine.models import JournalTransactionType, Journal, Posting, AssetType, Account, OperationAccount, BankAccount, \
    Instalment
from django.forms.models import model_to_dict
from django.db.models import Sum
from engine.services.account_services import DwhAccountAmountService
from sqs_services.services import SqsService, SnsService
from sns_sqs_services.services import SnsService as SnsServiceLibrary
from engine.utils.InvalidInstalmentError import *

CUMPLO_COST_ACCOUNT = 1


def costTransaction(transaction_cost_list, payment_cost_account, journal, asset_type):

    for requester_cost in transaction_cost_list:

        # Descuento a la cuenta de operacion por el monto total
        cumplo_operation_asesorias = Account.objects.get(external_account_type_id=4, external_account_id=
        requester_cost.cleaned_data['account_engine_properties']['destination_account']['id'])
        posting_from = Posting.objects.create(account=payment_cost_account, asset_type=asset_type, journal=journal,
                                              amount=(Decimal(requester_cost.cleaned_data['amount']) * -1))
        # Asignacion de inversionista a operacion
        posting_to = Posting.objects.create(account=cumplo_operation_asesorias, asset_type=asset_type, journal=journal,
                                            amount=Decimal(requester_cost.cleaned_data['amount']))


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

        account_posting = Posting.objects.select_related('journal').values('journal__gloss', 'amount', ).filter(
            account=account)

        # Create collecting record
        list_posting = []
        for posting in account_posting:
            list_posting.append(posting)

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


class BillinPropertiesForm(forms.Field):
    billable = forms.BooleanField(required=True)
    billing_entity = forms.CharField(required=False)

    def clean(self, value):
        return value


class SubAccountForm(forms.Field):
    account_type = forms.IntegerField(required=True)
    account_name = forms.CharField(required=True)


class DestinationAccountForm(forms.Field):
    account_type = forms.IntegerField(required=True)
    account_name = forms.CharField(required=True)


class AccountEnginePropertiesForm(forms.Field):
    destination_account = DestinationAccountForm()

    def clean(self, value):
        return value


class CostForm(forms.Form):
    billing_properties = BillinPropertiesForm(required=True)
    account_engine_properties = AccountEnginePropertiesForm(required=True)
    amount = forms.DecimalField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class FinanceOperationByInvestmentTransaction(Service):
    account = forms.IntegerField(required=True)
    investment_id = forms.IntegerField(required=True)
    total_amount = forms.DecimalField(required=True)
    investment_amount = forms.DecimalField(required=True)
    investment_costs = MultipleFormField(CostForm, required=False)
    external_operation_id = forms.IntegerField(required=True)
    asset_type = forms.IntegerField(required=True)

    def clean(self):
        total_cost = 0
        cleaned_data = super().clean()
        investment_id = cleaned_data.get('investment_id')
        external_operation_id = cleaned_data.get('external_operation_id')
        account_id = cleaned_data.get('account')
        list_validation_investment_error = []

        for invesment_cost in cleaned_data.get('investment_costs'):
            total_cost = total_cost + invesment_cost.cleaned_data.get('amount')

        if cleaned_data.get('investment_amount') + total_cost != cleaned_data.get('total_amount'):
            investment_error = {
                "error": 'los montos de inversion y costos no coinciden con el total'
            }

            list_validation_investment_error.append(investment_error)
            # raise forms.ValidationError("los montos de inversion y costos no coinciden con el total")
        try:
            OperationAccount.objects.filter(external_account_type_id=external_operation_id)

            investor_account = Account.objects.get(id=account_id)

            investor_amount_to_pay = Posting.objects.filter(account_id=investor_account.id).aggregate(Sum('amount'))

            if investor_amount_to_pay['amount__sum'] is not None and investor_amount_to_pay['amount__sum'] >= Decimal(
                    cleaned_data.get('investment_amount') + total_cost):
                pass
            else:
                investment_error = {
                    "message": 'El inversionista no tiene monto suficiente para pagar el monto de la inversion:' + str(
                        investment_id) + "- Monto Actual en cuenta inversionista:" + str(
                        investor_amount_to_pay['amount__sum'])
                }
                list_validation_investment_error.append(investment_error)

            if len(list_validation_investment_error) > 0:

                sns = SnsService(json_data={
                    "message": str(list_validation_investment_error),
                    "investment_id": investment_id,
                })

                investor_type = ""
                if investor_account.external_account_type_id == 1:  # PERSONA
                    investor_type = "user"
                elif investor_account.external_account_type_id == 2:  # Empresa
                    investor_type = "enterprise"
                else:
                    raise ValueError("Investor Type Error")

                attribute = sns.make_attributes(investor_type, "response", "fail")

                sns.push('arn:aws:sns:us-east-1:002311116463:cl-staging-investment-payment', attribute)

                raise forms.ValidationError(list_validation_investment_error)

        except Exception as e:
            raise forms.ValidationError(str(e))

        return cleaned_data

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
            costTransaction(investment_costs, from_account, journal, asset_type)


        DwhAccountAmountService.execute(
            {
                'account_id': from_account.id
            }
        )
        # if settings.DEBUG and settings.DEBUG != True:
        print("Enviando a SNS")

        sns = SnsService(json_data={  # "result": True,
            "message": "OK",
            "investment_id": investment_id,
            # "investor_type": from_account.external_account_type_id
        })

        investor_type = ""
        if from_account.external_account_type_id == 1:  # PERSONA
            investor_type = "user"
        elif from_account.external_account_type_id == 2:  # Empresa
            investor_type = "enterprise"
        else:
            raise ValueError("Investor Type Error")

        attribute = sns.make_attributes(investor_type, "response", "success")

        sns.push('arn:aws:sns:us-east-1:002311116463:cl-staging-investment-payment', attribute)

        # sqs = SqsService(json_data={"result": True,
        #                             "message": "TODO OK",
        #                             "investment_id": investment_id,
        #                             "investor_type": from_account.external_account_type_id
        #                             })

        # sqs.push('response-engine-pay-investment')

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
        logging.getLogger("error_logger").error("clean flga 2")
        cleaned_data = super().clean()
        total_amount = cleaned_data.get("total_amount")
        transfer_amount = cleaned_data.get("transfer_amount")
        external_operation_id = cleaned_data.get("external_operation_id")
        operation_data = OperationAccount.objects.get(external_account_id=external_operation_id)
        operation_financing_total_amount = Posting.objects.filter(account=operation_data).aggregate(Sum('amount'))

        # 2- que la operacion tenga suficiente financiamiento para pagar al solicitante y todos los costos asociados

        if operation_financing_total_amount['amount__sum'] is None or operation_financing_total_amount[
            'amount__sum'] < total_amount:
            raise forms.ValidationError(
                "La operacion No tiene Financiamiento suficiente para pagar el total de la transacción")

        # 3- que los costos mas el monto a transferir sean iguales a el monto total de la transferencia
        total_amount_cost = 0
        # if requester_costs:
        for requester_cost in cleaned_data.get("requester_costs"):
            #     # asignacion de inversionista a costos cumplo

            requester_cost_amount = requester_cost.clean()

            total_amount_cost = total_amount_cost + requester_cost_amount['amount']

        if total_amount_cost + transfer_amount != total_amount:
            raise forms.ValidationError("Los montos no coinciden")

        # 4- que los costos no sean mayor que el monto a transferir al solicitante

        if total_amount_cost > transfer_amount:
            raise forms.ValidationError(
                "Los costos asociados al pago son mayores que el monto a transferir al solicitante")

        # 5- Validar cuentas bancarias

        return cleaned_data

    def process(self):
        logging.getLogger("error_logger").error("Process flga 3")
        SEND_SNS=True

        # TODO: modificar este valor en duro
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
        cumplo_operation_bank_account = Account.objects.get(external_account_type_id=4, external_account_id=2)

        to_requester_account = Account.objects.get(id=account)

        asset_type = AssetType.objects.get(id=asset_type)

        # Traigo la cuenta de cumplo asesorias
        cumplo_cost_account = Account.objects.get(id=CUMPLO_COST_ACCOUNT)

        # Create Data
        ################################################################################################################
        ################################################################################################################

        # TODO: Llamar al modulo de facturación
        # asignacion de inversionista a costos cumplo
        total_amount_cost = 0


        for requester_cost in requester_costs:
            total_amount_cost = total_amount_cost + requester_cost.cleaned_data['amount']

        if total_amount_cost + transfer_amount != total_amount:
            raise Exception("Montos totales no coinciden")
        # Creacion de asiento
        journal = Journal.objects.create(batch=None, gloss=journal_transaction.description,
                                         journal_transaction=journal_transaction)

        # Descuento a la cuenta de operacion por el monto total
        posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal,
                                              amount=(Decimal(total_amount) * -1))

        # Asignacion de inversionista a operacion
        posting_to = Posting.objects.create(account=to_requester_account, asset_type=asset_type, journal=journal,
                                            amount=Decimal(
                                                total_amount))  ## al solicitante se le gira el total delmonto y se le descuentan los costos con costTransaction

        #IR A CUENTA POR PAGAR DE CUMPLO V/S SOLICITANTE por

        to_requestor_account_bank = BankAccount.objects.filter(
            account=to_requester_account).order_by('-updated')[0:1]

        from_account_bank = BankAccount.objects.filter(
            account=cumplo_operation_bank_account).order_by('-updated')[0:1]

        if to_requestor_account_bank.exists():
            to_requestor_account_bank = to_requestor_account_bank.get()
        else:
            raise Exception("No hay cuenta bancaria registrada para el solicitante. Operación Cancelada!!")

        if from_account_bank.exists():
            from_account_bank = from_account_bank.get()
        else:
            raise Exception("No hay cuenta bancaria registrada para la cuenta de operación. Operación Cancelada!!")

        costTransaction(requester_costs, to_requester_account, journal, asset_type)

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

        logging.getLogger("error_logger").error("PREVIO ENVIO SNS")

        if SEND_SNS:

            # Send SNS to confirm the payment (to financing)
            sns = SnsServiceLibrary()

            sns_topic = generate_sns_topic(settings.SNS_LOAN_PAYMENT)

            arn = sns.get_arn_by_name(sns_topic)

            attribute = sns.make_attributes(type='response', status='success')

            payload = {'operation_id': external_operation_id}

            logging.getLogger("error_logger").error("SNS_LOAN_PAYMENT ::: payload")
            logging.getLogger("error_logger").error(str(payload))

            #sns.push(arn, attribute, payload)

            # Send to Treasury - Paysheet

            sns = SnsServiceLibrary()

            logging.getLogger("error_logger").error("SNS_TREASURY_PAYSHEET ::: sns_topic SNS_TREASURY_PAYSHEET")
            logging.getLogger("error_logger").error(settings.SNS_TREASURY_PAYSHEET)
            sns_topic = generate_sns_topic(settings.SNS_TREASURY_PAYSHEET)

            arn = sns.get_arn_by_name(sns_topic)

            attribute = {}#sns.make_attributes(type='response', status='success')

            logging.getLogger("error_logger").error("SNS_TREASURY_PAYSHEET ::: CREATE PAYLOAD")

            payload = {
                 "origin_account": from_account_bank.bank_account_number,
                 "beneficiary_name": to_requestor_account_bank.account_holder_name,
                 "document_number": to_requestor_account_bank.account_holder_document_number,
                 "email": to_requestor_account_bank.account_notification_email,
                 "message": "Pago a Solicitante",#journal_transaction.description,
                 "destination_account": to_requestor_account_bank.bank_account_number,
                 "transfer_amount": f'{transfer_amount:.2f}',#.format(transfer_amount)), #Decimal(transfer_amount, round(2))),
                 "currency_type": "CLP",
                 "paysheet_line_type": "requestor",
                 "bank_code" : to_requestor_account_bank.bank_code
            }
            logging.getLogger("error_logger").error("SNS_TREASURY_PAYSHEET ::: payload")
            logging.getLogger("error_logger").error(str(payload))


            sns.push(arn, attribute, payload)

        return model_to_dict(journal)


class InstalmentsForms(forms.Form):
    payer_account_id = forms.IntegerField(required=True)
    external_operation_id = forms.IntegerField(required=True)
    instalment_id = forms.IntegerField(required=True)
    instalment_amount = forms.DecimalField(required=True)  # Capital más interés
    fine_amount = forms.DecimalField(required=True)  # Multa
    pay_date = forms.DateField(required=True)
    asset_type = forms.IntegerField(required=True)

    def clean(self):
        pass
class InstalmentPayment(Service):
    instalment_list_to_pay = MultipleFormField(InstalmentsForms, required=True)

    # Validaciones que implica la operacion de pagar al solicitane

    # 1- que la operacion esté financiada
    # 2- que la operacion tenga suficiente financiamiento para pagar al solicitante y todos los costos asociados
    # 3- que los costos mas el monto a transferir sean iguales a el monto total de la transferencia
    # 4- que los costos no sean mayor que el monto a transferir al solicitante

    def clean(self):
        cleaned_data = super().clean()

        list_validation_payment_error = []

        for instalment in cleaned_data.get('instalment_list_to_pay'):

            payer_account_id = instalment.cleaned_data["payer_account_id"]
            instalment_amount = instalment.cleaned_data["instalment_amount"]
            fine_amount = instalment.cleaned_data["fine_amount"]
            instalment_id = instalment.cleaned_data["instalment_id"]
            pay_date = instalment.cleaned_data['pay_date']
            external_operation_id = instalment.cleaned_data['external_operation_id']
            payer_posting_amount = Posting.objects.filter(account_id=payer_account_id).aggregate(Sum('amount'))
            # posting = Posting(account)
            if payer_posting_amount['amount__sum'] is not None and payer_posting_amount['amount__sum'] >= Decimal(
                    instalment_amount + fine_amount):
                pass
            else:
                instalment_error = {
                    "id": instalment_id,
                    "pay_date": str(pay_date),
                    "message": 'El pagador no tiene monto suficiente para pagar el monto de Cuota ID:' + str(
                        instalment_id) + "- Monto Actual en cuenta pagador:" + str(payer_posting_amount['amount__sum'])
                }
                list_validation_payment_error.append(instalment_error)

        if len(list_validation_payment_error) > 0:

            sqs = SqsService(json_data={
                "result": "NOT-OK",
                "operation_id": external_operation_id,
                "instalments": list_validation_payment_error
            })
            sqs.push('sqs_account_engine_instalment_payment_notification')

            raise forms.ValidationError(list_validation_payment_error)
        else:
            return cleaned_data

    def process(self):
        # TODO: modificar este valor en duro

        transaction_type = 6  # Pago de cuotas
        # Get Data
        instalments_ok_for_notification = []
        for instalment in self.cleaned_data['instalment_list_to_pay']:
            payer_account_id = instalment.cleaned_data['payer_account_id']
            external_operation_id = instalment.cleaned_data['external_operation_id']
            instalment_id = instalment.cleaned_data['instalment_id']
            instalment_amount = instalment.cleaned_data['instalment_amount']
            fine_amount = instalment.cleaned_data['fine_amount']
            pay_date = instalment.cleaned_data['pay_date']
            asset_type = instalment.cleaned_data['asset_type']

            # Get and Process Data
            # TODO: definir transacción de Pago a solicitante
            journal_transaction = JournalTransactionType.objects.get(id=transaction_type)
            to_operation_account = OperationAccount.objects.get(external_account_id=external_operation_id)
            from_payer_account = Account.objects.get(id=payer_account_id)

            asset_type = AssetType.objects.get(id=asset_type)

            # Create Data
            ################################################################################################################
            ################################################################################################################

            # Creacion de asiento
            journal = Journal.objects.create(batch=None, gloss=journal_transaction.description,
                                             journal_transaction=journal_transaction)

            # Descuento a la cuenta de operacion por el monto total
            posting_from = Posting.objects.create(account=from_payer_account, asset_type=asset_type, journal=journal,
                                                  amount=(Decimal(instalment_amount + fine_amount) * -1))

            # Asignacion de inversionista a operacion
            posting_to = Posting.objects.create(account=to_operation_account, asset_type=asset_type, journal=journal,
                                                amount=Decimal(instalment_amount + fine_amount))

            DwhAccountAmountService.execute(
                {
                    'account_id': from_payer_account.id
                }
            )
            DwhAccountAmountService.execute(
                {
                    'account_id': to_operation_account.id
                }
            )
            instalments_ok_for_notification.append(
                {
                    "pay_date": str(pay_date),
                    "id": instalment_id
                }
            )

        # TODO: DEFINIR COLA PARA ENVIAR ENVIAR INFO DE PAGO A SOLICITANTE

        #

        # TODO: DEFINIR COLA PARA ENVIAR LA CONFIRMACION DEL PAGO DE LA CUOTA
        sqs = SqsService(json_data={
            "result": "OK",
            "operation_id": external_operation_id,
            "instalments": instalments_ok_for_notification,
        })
        sqs.push('sqs_account_engine_instalment_payment_notification')

        return model_to_dict(journal_transaction)


class PaymentToInvestorForm(forms.Form):
    investor_account_id = forms.IntegerField(required=True)
    investor_account_type = forms.IntegerField(required=True)

    investment_id = forms.IntegerField(required=True)
    total_amount = forms.DecimalField(required=True)
    investment_instalment_amount = forms.DecimalField(required=True)
    investment_instalment_cost = MultipleFormField(CostForm, required=False)

    def clean(self):
        pass


class InvestorPaymentFromOperation(Service):
    # external_operation_id = forms.IntegerField(required=True)
    instalment = ModelField(Instalment)
    asset_type = forms.IntegerField(required=True)

    investors = MultipleFormField(PaymentToInvestorForm, required=False)

    # Validaciones que implica la operacion de pagar al solicitane
    def clean(self):

        cleaned_data = super().clean()
        external_operation_id = cleaned_data.get("external_operation_id")
        instalment = cleaned_data.get("instalment")
        instalment_amount = cleaned_data.get("instalment_amount")
        instalment.save()
        investors = cleaned_data.get('investors')

        cumplo_operation_bank_account = Account.objects.get(external_account_type_id=4, external_account_id=2)
        from_account_bank = BankAccount.objects.filter(
            account=cumplo_operation_bank_account).order_by('-updated')[0:1]
        if from_account_bank.exists():
            from_account_bank = from_account_bank.get()
        else:
            raise forms.ValidationError(
                "No hay cuenta bancaria registrada para la cuenta de operación. Operación Cancelada!!")

        total_investment_instalment = 0
        for investor in investors:

            investor_account = Account.objects.get(
                external_account_id=investor.cleaned_data['investor_account_id'],
                external_account_type_id=investor.cleaned_data['investor_account_type'])

            investor_bank_account = BankAccount.objects.filter(account=investor_account).order_by('-updated')[0:1]
            if investor_bank_account.exists():
                investor_bank_account = investor_bank_account.get()
                if investor_bank_account.account_holder_document_number == "" or investor_bank_account.account_holder_document_number is None:
                    raise forms.ValidationError(
                        "account_holder_document_number Empty")

                if investor_bank_account.account_holder_name == "" or investor_bank_account.account_holder_name is None:
                    raise forms.ValidationError(
                        "account_holder_name Empty")

            else:
                raise forms.ValidationError(
                    "No hay cuenta bancaria registrada para la cuenta de operación. Operación Cancelada!!")

            ##################################

            investment_instalment_total_amount = investor.cleaned_data.get('total_amount')

            total_investment_instalment = total_investment_instalment + investment_instalment_total_amount

            investment_instalment_cost_amount = 0
            for inv_instal_cost in investor.cleaned_data.get('investment_instalment_cost'):
                investment_instalment_cost_amount = investment_instalment_cost_amount + inv_instal_cost.cleaned_data.get(
                    'amount')

            if investment_instalment_cost_amount > Decimal(investor.cleaned_data.get('total_amount') - investor.cleaned_data.get('investment_instalment_amount') ) or investment_instalment_cost_amount < Decimal(investor.cleaned_data.get('total_amount') - investor.cleaned_data.get('investment_instalment_amount')):
                raise forms.ValidationError("Montos de costos de InvestmentInstalments e invesment instalment No coinciden " + str(
                    investment_instalment_cost_amount)+", "+ str(Decimal(investor.cleaned_data.get('total_amount') - investor.cleaned_data.get('investment_instalment_amount'))))

        if total_investment_instalment > instalment.amount or total_investment_instalment < instalment.amount:
            raise forms.ValidationError("Montos de InvestmentInstalments e instalment No coinciden por " + str(
                total_investment_instalment - instalment.amount))


    def process(self):
        transaction_type = 7  # pago de investment instalment as inversionista
        investor_payments = self.cleaned_data['investors']
        instalment = self.cleaned_data['instalment']
        asset_type = self.cleaned_data['asset_type']
        logging.getLogger("error_logger").error("Services process:::" )
        logging.getLogger("error_logger").error("investor_payments:::"+str(investor_payments))
        logging.getLogger("error_logger").error("instalment:::"+str(instalment))


        #Datos de cuenta Cumplo
        cumplo_operation_bank_account = Account.objects.get(external_account_type_id=4, external_account_id=2)

        from_account_bank = BankAccount.objects.filter(
            account=cumplo_operation_bank_account).order_by('-updated')[0:1]
        if from_account_bank.exists():
            from_account_bank = from_account_bank.get()
        else:
            raise forms.ValidationError(
                "No hay cuenta bancaria registrada para la cuenta de operación. Operación Cancelada!!")

        # journal = Journal.objects.get(id=7)#Transaccion de pago a inversionista

        # Creacion de asiento
        journal_transaction = JournalTransactionType.objects.get(id=transaction_type)
        journal = Journal.objects.create(batch=None, gloss=journal_transaction.description,
                                         journal_transaction=journal_transaction)

        asset_type = AssetType.objects.get(id=asset_type)

        # POSTING ORIGEN
        origin_account_transaction = Posting()
        origin_account_transaction.amount = (instalment.amount * -1)
        origin_account_transaction.account = instalment.operation
        origin_account_transaction.journal = journal
        origin_account_transaction.asset_type = asset_type
        origin_account_transaction.save()

        # POSTING DESTINO
        for investor_payment in investor_payments:
            investor_account = Account.objects.get(
                external_account_id=investor_payment.cleaned_data['investor_account_id'],
                external_account_type_id=investor_payment.cleaned_data['investor_account_type'])

            # if investor_payment.cleaned_data['investment_instalment_amount'] == 100500001:
            #     raise ValueError("Simulando Error")
            investor_amount =Decimal(investor_payment.cleaned_data['total_amount'])
            investment_instalment_costs = investor_payment.cleaned_data['investment_instalment_cost']
            investor_account_transaction = Posting()
            investor_account_transaction.amount = investor_amount
            investor_account_transaction.account = investor_account
            investor_account_transaction.asset_type = asset_type
            investor_account_transaction.journal = journal
            investor_account_transaction.save()
            costTransaction(investment_instalment_costs, investor_account, journal, asset_type)

            DwhAccountAmountService.execute(
                {
                    'account_id': investor_account.id
                }
            )
            investor_bank_account = BankAccount.objects.filter(account=investor_account).order_by('-updated')[0:1]
            if investor_bank_account.exists():
                investor_bank_account = investor_bank_account.get()

            else:
                raise forms.ValidationError(
                    "No hay cuenta bancaria registrada para la cuenta de operación. Operación Cancelada!!")
            #### Send to Treasury Paysheet

            sns = SnsServiceLibrary()

            sns_topic = generate_sns_topic(settings.SNS_TREASURY_PAYSHEET)

            arn = sns.get_arn_by_name(sns_topic)

            attribute = {}  # sns.make_attributes(type='response', status='success')

            payload = {
                "origin_account": from_account_bank.bank_account_number,
                "beneficiary_name": investor_bank_account.account_holder_name,
                "document_number": investor_bank_account.account_holder_document_number,
                "email": investor_bank_account.account_notification_email,
                "message": "Pago a Inversionista",  # journal_transaction.description,
                "destination_account": investor_bank_account.bank_account_number,


                "transfer_amount": f'{investor_amount:.2f}',
                # .format(transfer_amount)), #Decimal(transfer_amount, round(2))),
                "currency_type": "CLP",
                "paysheet_line_type": "investor",

                "bank_code": investor_bank_account.bank_code
            }
            print(str(payload))

            sns.push(arn, attribute, payload)

        return model_to_dict(journal)
