from django.test import TestCase
from datetime import date

# Create your tests here.




class MakeBillingTransactionServiceTest(TestCase):


    def test_create_payer(self):
        input = {

        }

    def test_make_billing_transaction(self):
        inputs = {

        }

    def set_billing_state(self):
        input={

        }
    # billing_contact_number = forms.IntegerField(required=True)
    # name = forms.CharField(required=True)
    # email = forms.EmailField(required=True)
    # address_number = forms.CharField(required=True)
    # street_address = forms.CharField(required=True)
    # adition_info_address = forms.CharField(required=True)
    # amount = forms.DecimalField(required=True, max_digits=20, decimal_places=5)
    # billing_reason = forms.IntegerField(required=True) #DecimalField(required=True, max_digits=20, decimal_places=5)
    # external_operation_id = forms.IntegerField(required=True)
    #
    # @property
    # def process(self):
    #     billing_contact_number_input = self.cleaned_data['billing_contact_number']
    #     name_input = self.cleaned_data['name']
    #     email_input = self.cleaned_data['email']
    #     address_number_input = self.cleaned_data['address_number']
    #     street_address_input = self.cleaned_data['street_address']
    #     adition_info_address_input = self.cleaned_data['adition_info_address']
    #     amount_input = self.cleaned_data['amount']
    #     billing_reason_input = self.cleaned_data['billing_reason']
    #     external_operation_id_input = self.cleaned_data['external_operation_id']
    #
    #     # Get Data
    #     billing_reason_data = BillingReason.objects.get(id=billing_reason_input)
    #
    #     # Create collecting record
    #     billing_contact = BillingContact.objects.update_or_create(
    #         document_number=billing_contact_number_input,
    #     )
    #
    #     billing_contact_data = BillingContact.objects.filter(document_number=billing_contact_number_input).get()
    #
    #     billing_reason_data=model_to_dict(billing_reason_data)
    #
    #     print(billing_reason_data)
    #
    #     return {billing_reason_data}



