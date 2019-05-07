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
