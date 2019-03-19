from rest_framework import serializers
from engine.models import Posting, Journal, Journal_transaction_type, Account, AssetType, OperationAccount, \
    PaymentRequest, DWHBalanceAccount
from decimal import Decimal
from django.db.models import Sum
from django.forms.models import model_to_dict
from engine.services.transfer_services import TransferToOperationAccountService
from engine.services.transaction_services import FinanceOperationByInvestmentTransaction
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
# from apiUserAdminMex.exceptions.cumplo_exception import *
from django.core.exceptions import ObjectDoesNotExist
import json
from collection_module.services.collection_services import CreateCollectingRecordService, PayerRecordService


class FromAccountSerializer(serializers.Serializer):

    def validate(self, data):
        try:
            print("flag -1")
            print(data)
            Account.objects.get(external_account_id=data['external_account_id'],
                                external_account_type_id=data['external_account_type'])
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    external_account_id = serializers.CharField(required=True, max_length=150)
    external_account_type = serializers.IntegerField(required=True)


class JournalTransactionsSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField(required=True)
    from_account = FromAccountSerializer
    to_operation_account = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)

    def validate(self, data):
        try:

            print("Flag -1")
            print(data['from_account'])

            origin_account = Account.objects.get(external_account_id=data['from_account']['external_account_id'],
                                                 external_account_type_id=data['from_account']['external_account_type'])

            operation_account = Account.objects.get(external_account_id=data['to_operation_account'],
                                                    external_account_type_id=3)

            account_posting_amount = Posting.objects.filter(account=origin_account).aggregate(Sum('amount'))
            # posting = Posting(account)
            print(account_posting_amount)
            if account_posting_amount['amount__sum'] is not None and account_posting_amount['amount__sum'] >= Decimal(
                    data['amount']):
                return data
            else:
                raise serializers.ValidationError("El monto no puede ser efectuado por saldo insuficiente")
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError("la cuenta de destino debe ser una cuenta de operación")

    def create(self, validated_data):

        posting_response = TransferToOperationAccountService.execute(
            {
                'journal_transaction': validated_data['transaction_type'],
                'from_account': validated_data['from_account'],
                'to_operation_account_data': validated_data['to_account'],
                'asset_type': validated_data['asset_type'],
                'amount': validated_data['amount'],
            }
        )

        return posting_response;

    def update(self, instance, validated_data):
        pass


class JournalOperationTransactionsSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField(required=True)
    from_account = FromAccountSerializer()
    to_operation_account = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)

    def validate(self, data):
        # data['from_account'] == data['to_account']
        #
        # if:
        #     raise serializers.ValidationError("las cuentas de destino y origen son iguales")
        print("Flag 1")
        print(data)
        try:
            from_account = Account.objects.get(external_account_id=data['from_account']['external_account_id'],
                                               external_account_type_id=data['from_account']['external_account_type'])
            account_posting_amount = Posting.objects.filter(account=from_account).aggregate(Sum('amount'))
            # posting = Posting(account)
            # print(account_posting_amount)
            if account_posting_amount['amount__sum'] is not None and account_posting_amount['amount__sum'] >= Decimal(
                    data['amount']):
                return data
            else:
                raise serializers.ValidationError("El monto no puede ser efectuado por saldo insuficiente: " + str(
                    account_posting_amount['amount__sum']))

        except ObjectDoesNotExist as e:
            raise serializers.ValidationError("la cuenta de destino debe ser una cuenta de operación")

    def create(self, validated_data):
        #TODO: pasar a un servicio independiente encargado de registrar las transacciones
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

        dwh_balance_account = Posting.objects.filter(account=from_account).aggregate(Sum('amount'))

        DWHBalanceAccount.objects.update_or_create(account=from_account, defaults={
            'balance_account_amount': dwh_balance_account['amount__sum']})

        print("flag 1!!!!")
        # TODO: Validar que este financiado desde Motor y que no se sobre financie
        if to_account.financing_amount is not None and account_posting_operation_amount[
            'amount__sum'] is not None and to_account.financing_amount < account_posting_operation_amount[
            'amount__sum']:

            print("Se Reconoce operacion Financiada!!!")
            list_post = []
            for posting_operation in posting_operation_amount:
                list_post.append(model_to_dict(posting_operation))

            # TODO Disponer en sistema de mensajeria amazon

            # TODO: ESTE ES EL ACTO DE REGISTRAR DEUDA DE OPERACION CON PAGADOR
            # REGISTRAR DOCUMENTO AVAL
            # FECHA DE COBRO
            # MONTO DEL COBRO
            # FECHA DE PAGO DE Documento
            # Id del documento, puede ser repetido
            # Identificador unico del socumento
            # Estado de cobranza: => Puede estar seteado al momento de ser creado!!!!
            try:

                # TODO Obtener quien es el solicitante del credito: Preguntar a API-Financing
                # Generar la orden de pago, debe contener
                #           operacion from_account
                #           y solicitante desde API-Financing para el to_account

                ########################################
                ########################################
                #   PAGO PENDIENTE A SOLICITANTE  ######
                ########################################
                ########################################

                journal = Journal.objects.create(gloss="Pago pendiente a solicitante", batch=None,
                                                 journal_transaction_id=1)

                # Registro de solicitud de pago a solicitante por operación financiada
                payment_request = PaymentRequest.objects.create(journal=journal,
                                                                amount=(to_account.financing_amount * -1),
                                                                account_payer=from_account, account=to_account)

                # Registro de solicitud de pago realizado a solicitante por operación financiada
                payment_request = PaymentRequest.objects.create(journal=journal, amount=to_account.financing_amount,
                                                                account_payer=from_account, account=to_account)

                ###################################################
                ###################################################
                #   SE ENVIA DATOS PARA GESTION DE COBRANZA  ######
                ###################################################
                ###################################################

                ##MODULO DE COBRANZA

                payer = PayerRecordService.execute({
                    'payer_name': from_account.name,
                    'external_payer_id': from_account.external_account_id,
                    'contact_data': 'blabla@gmail.com'
                })
                print(payer.external_id)
                print("Servicio crear pagador terminado")

                # recordServices = CreateCollectingRecordService.execute({
                #     'collecting_amount': to_account.financing_amount,
                #     'pay_date': '2001-01-01',
                #     'document_external_id': '222123123fds1',
                #     'document_type': 1,
                #     'operation_external_id': to_account.external_account_id,
                #     'external_payer_id': from_account.external_account_id,
                #     'document_description': '234234qqweqweqqq1',
                #
                # })

                ########################################
                ########################################
                #   PAGO REALIZADO A SOLICITANTE  ######
                ########################################
                ########################################

                # NOTA ::::

                # TODO: ESTE ES EL ACTO DE PAGAR a SOLICITANTE esto debiera ser un servicio
                journal = Journal.objects.create(batch=None, gloss="Pago a solicitante", journal_transaction_id=1)
                posting_from = Posting.objects.create(journal=journal, account=to_account,
                                                      amount=(to_account.financing_amount * -1))
                posting_to = Posting.objects.create(journal=journal, account=from_account,
                                                    amount=to_account.financing_amount)

                return {"payer": payer.external_id, "operation_account": model_to_dict(to_account),
                        "postings": list_post,
                        "payment_request": model_to_dict(payment_request),
                        "posting_payment": {"from": model_to_dict(posting_from), "to": model_to_dict(posting_to)}}



            except Exception as e:
                print(str(e))
                raise e

        print("flag 3!!!!")
        return model_to_dict(journal);

    def update(self, instance, validated_data):
        pass


class InvesmentCostSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    type = serializers.IntegerField(required=True)


class JournalOperationInvestmentTransactionSerializer(serializers.Serializer):
    investor_account_id = serializers.CharField(required=True)
    investor_account_type = serializers.IntegerField(required=True)
    external_operation_id = serializers.CharField(required=True)
    investment_id = serializers.IntegerField(required=True)
    total_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_cost = InvesmentCostSerializer(many=True)

    def validate(self, data):
        # Validar que los montos cuadren en total
        total_cost = 0
        for invesment_cost in data['investment_cost']:
            total_cost = total_cost + invesment_cost['amount']

        if data['investment_amount'] + total_cost != data['total_amount']:
            raise serializers.ValidationError("los montos de inversion y costos no coinciden con el total")
        try:
            OperationAccount.objects.filter(external_account_type_id=data['external_operation_id'])

        except Exception as e:
            raise serializers.ValidationError(str(e))

        return data

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):

        investor_account=Account.objects.get(external_account_id=validated_data['investor_account_id'], external_account_type_id=validated_data['investor_account_type'])

        print("validated_data['external_operation_id']")
        print(validated_data['external_operation_id'])
        algo = FinanceOperationByInvestmentTransaction.execute(
            {
                'account' : investor_account.id,
                'investment_id' : validated_data['investment_id'],
                'total_amount' : validated_data['total_amount'],
                'investment_amount' : validated_data['investment_amount'],
                'investment_costs' : validated_data['investment_cost'],
                'external_operation_id': validated_data['external_operation_id'],
                #TODO: definir el asset_type según sistema con que interactura
                'asset_type': 1
            }
        )
        return algo
