from rest_framework import serializers
from collection_module.models import GuaranteeDocument, Payment
from collection_module.services.payment_services import CreatePaymentService


class GuaranteeDocumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = GuaranteeDocument
        fields = "__all__"


class PaymentSerializers(serializers.Serializer):
    payer_external_id = serializers.IntegerField(required=True)
    external_operation_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)

    # def validate(self, data):
    #
    #     if data['from_account'] == data['to_account']:
    #         raise serializers.ValidationError("las cuentas de destino y origen son iguales")
    #
    #     try:
    #         Account.objects.get(id=data['to_account'])
    #
    #         account_posting_amount = Posting.objects.filter(account=data['from_account']).aggregate(Sum('amount'))
    #         # posting = Posting(account)
    #         print(account_posting_amount)
    #         if account_posting_amount['amount__sum'] is not None and account_posting_amount['amount__sum'] >= Decimal(
    #                 data['amount']):
    #             return data
    #         else:
    #             raise serializers.ValidationError("El monto no puede ser efectuado por saldo insuficiente")
    #     except ObjectDoesNotExist as e:
    #         raise serializers.ValidationError("la cuenta de destino debe ser una cuenta de operación")

    def create(self, validated_data):
        print("FLAG 1 CREATE ")
        print(validated_data)
        payment = CreatePaymentService.execute(
            {
                'payer_external_id': validated_data['payer_external_id'],
                'amount': validated_data['amount'],
                'external_operation_id': validated_data['external_operation_id'],
            }
        )

        return payment
