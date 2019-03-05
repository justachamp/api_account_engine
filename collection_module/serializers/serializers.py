from collection_module.models import Payer, GuaranteeDocument
from rest_framework import serializers


class PayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payer
        fields = (
            'name',
            'external_id',
            'contact_data',
        )


class GuaranteeDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GuaranteeDocument
        fields = (
            'state',
            'document_type',
            'payer',
            'payment_date',
            'payment_amount',
            'external_id',
            'external_operation_id',
            'document_description',
        )
