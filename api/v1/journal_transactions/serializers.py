from rest_framework import serializers
from engine.models import Posting, Journal, JournalTransactionType, Account, AssetType, OperationAccount, \
    PaymentRequest, DWHBalanceAccount, BankAccount, Instalment

from service_objects.errors import InvalidInputsError

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import model_to_dict
from engine.services.transfer_services import TransferToOperationAccountService
from engine.services.transaction_services import FinanceOperationByInvestmentTransaction, RequesterPaymentFromOperation, InstalmentPayment, InvestorPaymentFromOperation
from django.core.exceptions import ObjectDoesNotExist
from collection_module.services.collection_services import CreateCollectingRecordService, PayerRecordService
from django import forms


class FromAccountSerializer(serializers.Serializer):

    def validate(self, data):
        try:
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


            origin_account = Account.objects.get(external_account_id=data['from_account']['external_account_id'],
                                                 external_account_type_id=data['from_account']['external_account_type'])

            operation_account = Account.objects.get(external_account_id=data['to_operation_account'],
                                                    external_account_type_id=3)

            account_posting_amount = Posting.objects.filter(account=origin_account).aggregate(Sum('amount'))
            # posting = Posting(account)
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
        # TODO: pasar a un servicio independiente encargado de registrar las transacciones
        # Get data for proccess
        journal_transaction = JournalTransactionType.objects.get(id=validated_data['transaction_type'])
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

        # TODO: Validar que este financiado desde Motor y que no se sobre financie
        if to_account.financing_amount is not None and account_posting_operation_amount[
            'amount__sum'] is not None and to_account.financing_amount < account_posting_operation_amount[
            'amount__sum']:

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

                raise e

        return model_to_dict(journal);

    def update(self, instance, validated_data):
        pass


class BillingPropertiesSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        return validated_data

    def create(self, validated_data):
        return validated_data

    billable = serializers.BooleanField(required=True)
    billing_entity = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    #TODO: TAX, validar con Barbara si es necesario este campo para presentación de info en datos de Facturación


class SubAccountSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    account_type = serializers.IntegerField(required=True)
    account_name = serializers.CharField(required=True)


class DestinationAccountSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.IntegerField(required=True)
    #account_type = serializers.IntegerField(required=True)
    #account_name = serializers.CharField(required=True)
    #sub_account = SubAccountSerializer()


class AccountEnginePropertiesSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    destination_account = DestinationAccountSerializer()


class CostSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        return validated_data

    def create(self, validated_data):
        return validated_data

    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    billing_properties = BillingPropertiesSerializers(required=True)
    account_engine_properties = AccountEnginePropertiesSerializer(required=True)


class JournalOperationInvestmentTransactionSerializer(serializers.Serializer):
    investor_account_id = serializers.CharField(required=True)
    investor_account_type = serializers.IntegerField(required=True)
    external_operation_id = serializers.CharField(required=True)
    investment_id = serializers.IntegerField(required=True)
    total_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_cost = CostSerializer(many=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):


        investor_account = Account.objects.get(external_account_id=validated_data['investor_account_id'],
                                               external_account_type_id=validated_data['investor_account_type'])

        try:

            financing_response = FinanceOperationByInvestmentTransaction.execute(
                {
                    'account': investor_account.id,
                    'investment_id': validated_data['investment_id'],
                    'total_amount': validated_data['total_amount'],
                    'investment_amount': validated_data['investment_amount'],
                    'investment_costs': validated_data['investment_cost'],
                    'external_operation_id': validated_data['external_operation_id'],
                    # TODO: definir el asset_type según sistema con que interactura
                    'asset_type': 1
                }
            )
            return financing_response

        except Exception as e:
            raise e


class JournalRequesterPaymentFromOperationTransactionSerializer(serializers.Serializer):


    def positive_number(value):
        if value < Decimal(0):
            raise ValidationError("Must be positive")

    def validate(self, data):

        # Validar que los montos cuadren en total
        """
        total_cost = 0
        for requester_cost in data['requester_cost']:
            total_cost = total_cost + requester_cost['amount']

        if data['transfer_amount'] + total_cost != data['total_amount']:
            raise serializers.ValidationError("los montos a transferir y costos no coinciden con el total")
        """
        try:
            OperationAccount.objects.filter(external_account_type_id=data['external_operation_id'])

            requester_account = Account.objects.get(external_account_id=data['requester_account_id'],
                                                    external_account_type_id=data['requester_account_type'])

            bank_account = BankAccount.objects.filter(account=requester_account)[0:1].get()

        except BankAccount.DoesNotExist as e:
            raise serializers.ValidationError("No hay cuenta Bancaria asociada al solicitante")

        except Exception as e:
            raise serializers.ValidationError(str(e))

        return data

    requester_account_id = serializers.IntegerField(required=True)
    requester_account_type = serializers.IntegerField(required=True)
    external_operation_id = serializers.IntegerField(required=True)
    total_amount = serializers.DecimalField(allow_null=False, default=Decimal('0.00000'), max_digits=20,
                                            decimal_places=5, validators=[positive_number])
    transfer_amount = serializers.DecimalField(allow_null=False, default=Decimal('0.00000'), max_digits=20,
                                               decimal_places=5, validators=[positive_number])
    requester_cost = CostSerializer(many=True)


    def create(self, validated_data):
        requester_account = Account.objects.get(external_account_id=validated_data['requester_account_id'],
                                                external_account_type_id=validated_data['requester_account_type'])




        requester_payment_from_operation = RequesterPaymentFromOperation.execute(
            {
                "account": requester_account.id,
                "total_amount": validated_data['total_amount'],
                "transfer_amount": validated_data['transfer_amount'],
                "external_operation_id": validated_data['external_operation_id'],
                "asset_type": 1,
                "requester_costs": validated_data['requester_cost']
            }
        )

        return requester_payment_from_operation

    def update(self, instance, validated_data):
        pass


class InstalmentPaymentSerializers(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):




        return validated_data

    payer_account_id = serializers.IntegerField(required=True)
    payer_account_type = serializers.IntegerField(required=True)
    external_operation_id = serializers.IntegerField(required=True)
    instalment_id = serializers.IntegerField(required=True)
    instalment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    fine_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    pay_date = serializers.DateField(required=True)


class JournalInstalmentPaymentTransactionSerializer(serializers.Serializer):
    instalments = InstalmentPaymentSerializers(many=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        instalments = validated_data['instalments']
        instalment_list_to_services = []
        for instalment in instalments:
            payer_account = Account.objects.get(external_account_id=instalment['payer_account_id'],
                                                external_account_type_id=instalment['payer_account_type'])

            external_operation_id = instalment['external_operation_id']
            instalment_id = instalment['instalment_id']
            instalment_amount = instalment['instalment_amount']
            fine_amount = instalment['fine_amount']
            pay_date = instalment['pay_date']

            instalment_list_to_services.append(
                {
                    "payer_account_id":payer_account.id,
                    "external_operation_id":external_operation_id,
                    "instalment_id":instalment_id,
                    "instalment_amount":instalment_amount,
                    "fine_amount":fine_amount,
                    "pay_date": pay_date,
                    "asset_type": 1
                }
            )


        requester_payment_from_operation = InstalmentPayment.execute(
            {
                "instalment_list_to_pay": instalment_list_to_services,

            }
        )

        return requester_payment_from_operation


class PaymentToInvestor(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    investor_account_id = serializers.IntegerField(required=True)
    investor_account_type = serializers.IntegerField(required=True)
    investment_id = serializers.IntegerField(required=True)
    total_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_instalment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    investment_instalment_cost = CostSerializer(many=True)


class JournalInvestorPaymentFromInstalmentOperationSerializer(serializers.Serializer):


    def positive_number(value):
        if value < Decimal(0):
            raise ValidationError("Must be positive")

    # def validate(self, data):
    #
    #     # Validar que los montos cuadren en total
    #     """
    #     total_cost = 0
    #     for requester_cost in data['requester_cost']:
    #         total_cost = total_cost + requester_cost['amount']
    #
    #     if data['transfer_amount'] + total_cost != data['total_amount']:
    #         raise serializers.ValidationError("los montos a transferir y costos no coinciden con el total")
    #     """
    #     try:
    #         OperationAccount.objects.filter(external_account_type_id=data['external_operation_id'])
    #
    #         requester_account = Account.objects.get(external_account_id=data['requester_account_id'],
    #                                                 external_account_type_id=data['requester_account_type'])
    #
    #         bank_account = BankAccount.objects.filter(account=requester_account)[0:1].get()
    #
    #     except BankAccount.DoesNotExist as e:
    #         raise serializers.ValidationError("No hay cuenta Bancaria asociada al solicitante")
    #
    #     except Exception as e:
    #         raise serializers.ValidationError(str(e))
    #
    #     return data

    instalment_id = serializers.IntegerField(required=True)
    instalment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=2)
    external_operation_id = serializers.IntegerField(required=True)
    investors = PaymentToInvestor(many=True, required=True)

    def validate_external_operation_id(self, value):
        """
               Check that the blog post is about Django.
               """
        operation = OperationAccount.objects.filter(external_account_id=value)
        if operation.exists():
            return value
        raise serializers.ValidationError("la operación no existe")



    def create(self, validated_data):
        # requester_account = Account.objects.get(external_account_id=validated_data['requester_account_id'],
        #                                         external_account_type_id=validated_data['requester_account_type'])


        operation = OperationAccount.objects.get(external_account_id=validated_data['external_operation_id'])


        new_instalment = Instalment()
        new_instalment.amount = validated_data['instalment_amount']
        new_instalment.id = validated_data['instalment_id']
        new_instalment.operation = operation


        requester_payment_from_operation = InvestorPaymentFromOperation.execute(
            {
                "instalment": new_instalment,
                "investors": validated_data['investors'],
                "asset_type" : 1
            }
        )

        return requester_payment_from_operation

    def update(self, instance, validated_data):
        pass


