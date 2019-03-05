from service_objects.services import Service
from django import forms
from collection_module.models import Payment, Payer
from django.forms.models import model_to_dict


class CreatePaymentService(Service):
    payer_external_id = forms.CharField(required=True, max_length=20)
    amount = forms.DecimalField(required=True, decimal_places=5, max_digits=20)
    external_operation_id = forms.DecimalField(required=True, decimal_places=5, max_digits=20)

    def process(self):
        payer_external_id_input = self.cleaned_data['payer_external_id']
        amount_input = self.cleaned_data['amount']
        external_operation_id_input = self.cleaned_data['external_operation_id']


        # Get Data
        payer = Payer.objects.get(id=payer_external_id_input)

        # Create collecting record
        Payment.objects.create(
            payment_payer=payer,
            amount=amount_input,
            external_operation_id=external_operation_id_input
        )

        payments = Payment.objects.filter(external_operation_id=external_operation_id_input)

        payment_list=[]
        for payment in payments:
            payment_list.append(model_to_dict(payment))

        return {'payment_to_operation': payment_list}
