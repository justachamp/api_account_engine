from django.db import models
from engine.models import AbstractModel


class BillingReason(AbstractModel):
    description = models.CharField(null=False, max_length=150)


class BillingPayer(AbstractModel):
    document_number = models.CharField(unique=True, null=False, max_length=11)


class HistoricBillingContact(AbstractModel):
    base_contact = models.ForeignKey(BillingPayer, null=False, on_delete=models.PROTECT)
    name = models.CharField(null=False, max_length=350)
    email = models.EmailField(max_length=200)
    address_number = models.IntegerField()
    street_address = models.CharField(max_length=350)
    adition_info_address = models.CharField(max_length=350)


class BillingTransaction(AbstractModel):
    billing_contact_for_billing = models.ForeignKey(HistoricBillingContact, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    external_operation_id = models.CharField(null=False, max_length=150)
