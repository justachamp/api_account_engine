from service_objects.services import Service
from django import forms
from billing_module.models.billing import BillingReason, BillingTransaction, BillingPayer, HistoricBillingContact
from django.forms.models import model_to_dict


class MakeBillingTransactionService(Service):
    billing_contact_number = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    address_number = forms.CharField(required=True)
    street_address = forms.CharField(required=True)
    adition_info_address = forms.CharField(required=True)
    amount = forms.DecimalField(required=True, max_digits=20, decimal_places=5)
    billing_reason = forms.IntegerField(required=True)  # DecimalField(required=True, max_digits=20, decimal_places=5)
    external_operation_id = forms.IntegerField(required=True)

    @property
    def process(self):
        billing_contact_number_input = self.cleaned_data['billing_contact_number']
        name_input = self.cleaned_data['name']
        email_input = self.cleaned_data['email']
        address_number_input = self.cleaned_data['address_number']
        street_address_input = self.cleaned_data['street_address']
        adition_info_address_input = self.cleaned_data['adition_info_address']
        amount_input = self.cleaned_data['amount']
        billing_reason_input = self.cleaned_data['billing_reason']
        external_operation_id_input = self.cleaned_data['external_operation_id']

        # Get Datas
        billing_reason_data = BillingReason.objects.get(id=billing_reason_input)

        # Create collecting record
        billing_contact = BillingPayer.objects.update_or_create(
            document_number=billing_contact_number_input,
        )

        billing_contact_data = BillingPayer.objects.filter(document_number=billing_contact_number_input).get()

        billing_reason_data = model_to_dict(billing_reason_data)

        print(billing_reason_data)

        return {billing_reason_data}


class SaveBillingPayerService(Service):
    billing_payer_document_number = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    address_number = forms.CharField(required=True)
    street_address = forms.CharField(required=True)
    adition_info_address = forms.CharField(required=True)

    @property
    def process(self):
        billing_payer_document_number_input = self.cleaned_data['billing_payer_document_number']
        name_input = self.cleaned_data['name']
        email_input = self.cleaned_data['email']
        address_number_input = self.cleaned_data['address_number']
        street_address_input = self.cleaned_data['street_address']
        adition_info_address_input = self.cleaned_data['adition_info_address']

        # Get Data
        billing_payer = BillingPayer.objects.get(document_number=billing_payer_document_number_input)

        # Create collecting record
        billing_contact = BillingPayer.objects.update_or_create(
            document_number=billing_payer_document_number_input,
        )

        billing_contact_data = BillingPayer.objects.filter(document_number=billing_payer_document_number_input).get()

        billing_reason_data = model_to_dict(billing_contact_data)

        print(billing_reason_data)

        return {billing_reason_data}
