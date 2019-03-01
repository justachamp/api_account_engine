from rest_framework import serializers
from engine.models import Posting, Journal, Journal_transaction_type, Account, AssetType, OperationAccount, PaymentRequest
from decimal import Decimal
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
# from apiUserAdminMex.exceptions.cumplo_exception import *
from django.core.exceptions import ObjectDoesNotExist
import json


class JournalTransactionsSerializer(serializers.Serializer):
    transaction_type = serializers.IntegerField(required=True)
    from_account = serializers.IntegerField(required=True)
    to_account = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    asset_type = serializers.IntegerField(required=True)

    def validate(self, data):

        if data['from_account'] == data['to_account']:
            raise serializers.ValidationError("las cuentas de destino y origen son iguales")

        try:
            Account.objects.get(id=data['to_account'])

            account_posting_amount = Posting.objects.filter(account=data['from_account']).aggregate(Sum('amount'))
            # posting = Posting(account)
            print(account_posting_amount)
            if account_posting_amount['amount__sum'] is not None and account_posting_amount['amount__sum'] >= Decimal(data['amount'] ):
                return data
            else:
                raise serializers.ValidationError("El monto no puede ser efectuado por saldo insuficiente")
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError("la cuenta de destino debe ser una cuenta de operación")

    def create(self, validated_data):
        journal_transaction = Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
        from_account = Account.objects.get(id=validated_data['from_account'])
        to_account = Account.objects.get(id=validated_data['to_account'])
        asset_type = AssetType.objects.get(id=validated_data['asset_type'])
        journal = Journal.objects.create(batch=None, gloss="", journal_transaction=journal_transaction)
        posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal, amount=(Decimal(validated_data['amount'])* -1))
        posting_to = Posting.objects.create(account=to_account, asset_type=asset_type, journal=journal, amount=Decimal(validated_data['amount']))
        return journal;


    def update(self, instance, validated_data):
        pass


class JournalOperationTransactionsSerializer(JournalTransactionsSerializer):

    def validate(self, data):
        try:
            OperationAccount.objects.get(id=data['to_account'])
            return data

        except ObjectDoesNotExist as e:
            raise serializers.ValidationError("la cuenta de destino debe ser una cuenta de operación")

    def create(self, validated_data):
        journal_transaction = Journal_transaction_type.objects.get(id=validated_data['transaction_type'])
        from_account = Account.objects.get(id=validated_data['from_account'])
        to_account = OperationAccount.objects.get(id=validated_data['to_account'])
        asset_type = AssetType.objects.get(id=validated_data['asset_type'])

        account_posting_operation_amount = Posting.objects.filter(account=validated_data['to_account']).aggregate(Sum('amount'))
        posting_operation_amount = Posting.objects.filter(account=validated_data['to_account'])


        journal = Journal.objects.create(batch=None, gloss="", journal_transaction=journal_transaction)
        posting_from = Posting.objects.create(account=from_account, asset_type=asset_type, journal=journal, amount=(Decimal(validated_data['amount'])* -1))
        posting_to = Posting.objects.create(account=to_account, asset_type=asset_type, journal=journal, amount=Decimal(validated_data['amount']))


        print("flag 1!!!!")
        # TODO: Validar que este financiado desde Motor y que no se sobre financie
        if to_account.financing_amount is not None and account_posting_operation_amount['amount__sum'] is not None and to_account.financing_amount < account_posting_operation_amount['amount__sum']:
            print("Operacion Financiada")
            list_post=[]
            for posting_operation in posting_operation_amount:
                list_post.append(model_to_dict(posting_operation))
                #TODO Disponer en sistema de mensajeria amazon
                #TODO Obtener quien es el solicitante del credito: Preguntar a API-Financing
                #Generar la orden de pago, debe contener
                #           operacion from_account
                #           y solicitante desde API-Financing para el to_account

                payment_request = PaymentRequest.objects.create( amount= ( to_account.financing_amount * -1),  origin_account= to_account , destiny_account= from_account)

                payment_request = PaymentRequest.objects.create( amount=(to_account.financing_amount),
                                                                origin_account=from_account, destiny_account=to_account)



                #TODO: ESTE ES EL ACTO DE PAGAR a SOLICITANTE esto debiera ser un servicio
                journal= Journal.objects.create(batch=None, gloss="Pago a solicitante", journal_transaction_id=1)
                posting_from= Posting.objects.create(journal=journal,account= to_account, amount=( to_account.financing_amount * -1))
                posting_to= Posting.objects.create(journal=journal,account= from_account, amount=to_account.financing_amount)

                # TODO: ESTE ES EL ACTO DE REGISTRAR DEUDA DE OPERACION CON PAGADOR
                # REGISTRAR DOCUMENTO AVAL
                # FECHA DE COBRO
                # MONTO DEL COBRO
                # FECHA DE PAGO DE Documento
                # Id del documento, puede ser repetido
                # Identificador unico del socumento
                # Estado de cobranza: => Puede estar seteado al momento de ser creado!!!!

                # TODO: Registro de Pago a Pago a Solicitante
                journal = Journal.objects.create(batch=None, gloss="Pago a solicitante", journal_transaction_id=1)
                posting_from = Posting.objects.create(journal=journal, account=to_account,
                                                      amount=(to_account.financing_amount * -1))

                posting_to = Posting.objects.create(journal=journal, account=from_account,
                                                    amount=to_account.financing_amount)



            return {"operation_account": model_to_dict(to_account), "postings":list_post,"payment_request":model_to_dict(payment_request),"posting_payment":{"from":model_to_dict(posting_from), "to":model_to_dict(posting_to)}}

        print("flag 3!!!!")
        return model_to_dict(journal);

    def update(self, instance, validated_data):
        pass