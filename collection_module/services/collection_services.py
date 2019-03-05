from service_objects.services import Service
from django import forms
from collection_module.serializers.serializers import GuaranteeDocumentSerializer, PayerSerializer
from collection_module.models import *
from django.forms.models import model_to_dict


class CreateCollectingRecordService(Service):
    collecting_amount = forms.DecimalField(required=True, decimal_places=5, max_digits=20)
    pay_date = forms.DateField(required=True)
    document_external_id = forms.CharField(required=True, max_length=20)
    document_type = forms.CharField(required=True, max_length=20)
    operation_external_id = forms.CharField(required=True, max_length=20)
    external_payer_id = forms.CharField(required=True, max_length=20)
    document_description = forms.CharField(required=True, max_length=350)

    def process(self):
        collecting_amount_input = self.cleaned_data['collecting_amount']
        pay_date_input = self.cleaned_data['pay_date']
        document_external_id_input = self.cleaned_data['document_external_id']
        document_type_input = self.cleaned_data['document_type']
        operation_external_id_input = self.cleaned_data['operation_external_id']
        external_payer_id_input = self.cleaned_data['external_payer_id']
        document_description_input = self.cleaned_data['document_description']

        # Get Data
        payer = Payer.objects.filter(external_id=external_payer_id_input).get()
        document_type = DocumentType.objects.get(id=document_type_input)
        state = CollectionState.objects.get(id=1)
        # Create collecting record

        GuaranteeDocument.objects.update_or_create(state=state,
                                                   document_description=document_description_input,
                                                   payer=payer,
                                                   payment_date=pay_date_input,
                                                   payment_amount=collecting_amount_input,
                                                   external_id=document_external_id_input,
                                                   external_operation_id=operation_external_id_input,
                                                   document_type=document_type)

        guarantee_document = GuaranteeDocument.objects.get(external_id=document_external_id_input)
        return guarantee_document

        # payment_record = GuaranteeDocumentSerializer(data={
        #     'state': state,  # TODO: sacar state de la base de datos
        #     'document_type': document_type,
        #     'payer': payer,
        #     'payment_date': pay_date_input,
        #     'payment_amount' : collecting_amount_input,
        #     'external_id': document_external_id_input,
        #     'external_operation_id': operation_external_id_input,
        #     'document_description': document_description_input
        # })
        #
        #
        # if payment_record.is_valid():
        #     payment_record.save()
        #     return payment_record
        # print(payment_record.errors)
        # raise payment_record.errors

        # Send verification email (check out django-herald)
        # VerifyEmailNotification(booking).send()


class PayerRecordService(Service):
    payer_name = forms.CharField(required=True, max_length=250)
    external_payer_id = forms.CharField(max_length=150)
    contact_data = forms.CharField(max_length=150)

    def process(self):
        payer_name = self.cleaned_data['payer_name']
        external_payer_id = self.cleaned_data['external_payer_id']
        contact_data = self.cleaned_data['contact_data']

        Payer.objects.update_or_create(name=payer_name, external_id=external_payer_id,
                                                             contact_data=contact_data)

        payer_up_or_created=Payer.objects.get(external_id=external_payer_id)


        print('payer_up_or_created')
        print(str(payer_up_or_created.external_id))

        return payer_up_or_created
        # Update or Create pay  er
        # payer = PayerSerializer(data={
        #     'name' : payer_name,
        #     'external_id': external_payer_id,
        #     'contact_data': contact_data
        # })
        # if payer.is_valid():
        #     payer
        #     return payer
        # print(payer.errors)
        # raise payer.errors


class SetStateCollectionPaymentService(Service): #DEBIERA ESTAR???? debiera contrarestar con un payment
    document_external_id = forms.CharField(required=True, max_length=20)
    document_type = forms.CharField(required=True, max_length=20)
    operation_external_id = forms.CharField(required=True, max_length=20)
    new_state = forms.CharField(required=True, max_length=20)

    def process(self):
        document_external_id_input = self.cleaned_data['document_external_id']
        document_type_input = self.cleaned_data['document_type']
        operation_external_id_input = self.cleaned_data['operation_external_id']
        new_state_input = self.cleaned_data['new_state']

        # Get Data
        document_type = DocumentType.objects.get(document_type_input)
        new_state = CollectionState.objects.get(new_state_input)

        # Create booking
        update_state = GuaranteeDocument.objects.filter(
            document_external_id=document_external_id_input,
            document_type=document_type,
            external_operation_id=operation_external_id_input,

        ).update(state=new_state, )

        # Send verification email (check out django-herald)
        # VerifyEmailNotification(booking).send()

        return model_to_dict(update_state)


class GetCollectionPaymentService(Service):
    document_external_id = forms.CharField(required=True, max_length=20)
    document_type = forms.CharField(required=True, max_length=20)
    operation_external_id = forms.CharField(required=True, max_length=20)

    def process(self):
        document_external_id_input = self.cleaned_data['document_external_id']
        document_type_input = self.cleaned_data['document_type']
        operation_external_id_input = self.cleaned_data['operation_external_id']

        # Get Data
        document_type = DocumentType.objects.get(document_type_input)

        # Create booking
        get_collection = GuaranteeDocument.objects.filter(
            document_external_id=document_external_id_input,
            document_type=document_type,
            external_operation_id=operation_external_id_input
        )

        return get_collection
