from django.core.exceptions import ObjectDoesNotExist

from billing_module.models.billing import BillingPayer, BillingReason, BillingTransaction, HistoricBillingContact
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from billing_module.services.billing_services import MakeBillingTransactionService


class BillingReasonSerializers(serializers.ModelSerializer):
    class Meta:
        model = BillingReason
        fields = "__all__"


class HistoricBillingContactSerializers(ModelSerializer):

    class Meta:
        model = HistoricBillingContact
        fields = "__all__"


class BillingPayerSerializers(ModelSerializer):

    historic_billing_contact = HistoricBillingContactSerializers()

    class Meta:
        model = BillingPayer
        fields = ['document_number', 'historic_billing_contact']


class BillingContactPayerSerializers(serializers.Serializer):
    document_number= serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            BillingPayer.objects.get(document_number=data['document_number'])
            return data

        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        billing_payer = BillingPayer.objects.get(document_number=validated_data['document_number'])

        return billing_payer



class BillingTransactionSerializers(serializers.Serializer):
    billing_contact_number = serializers.IntegerField(required=True)
    contact_name = serializers.CharField(required=True)
    contact_email = serializers.EmailField(required=True)
    contact_address_number = serializers.CharField(required=True)
    contact_street_address = serializers.CharField(required=True)
    contact_adition_info_address = serializers.CharField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=5)
    billing_reason = serializers.IntegerField(required=True)
    external_operation_id = serializers.IntegerField(required=True)

    # TODO: Validaciones Pendientes en Modulo de Facturación
    def validate(self, data):
        return data

    def create(self, validated_data):
        print("FLAG 1 CREATE ")
        print(validated_data)
        payment = MakeBillingTransactionService.execute(
            {
                'billing_contact_number': validated_data['billing_contact_number'],
                'name': validated_data['contact_name'],
                'email': validated_data['contact_email'],

                'address_number': validated_data['contact_address_number'],
                'street_address': validated_data['contact_street_address'],
                'adition_info_address': validated_data['contact_adition_info_address'],
                'amount': validated_data['amount'],
                'billing_reason': validated_data['billing_reason'],
                'external_operation_id': validated_data['external_operation_id'],
            }
        )

        return payment

    def update(self, instance, validated_data):
        pass
