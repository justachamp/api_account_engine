from django.db import models
from engine.models import AbstractModel


class Transaction(AbstractModel):
    description = models.CharField(null=False, max_length=150)
    amount = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    gloss = models.CharField(null=False, max_length=150)
    transfer_request_date = models.DateTimeField(null=False)
    external_account_id=models.CharField(null=False, max_length=150)
    external_transacction_id = models.CharField(null=False, max_length=150)


class BankDestiny(AbstractModel):
    bank_name = models.CharField(null=False, max_length=150)
    bank_code = models.CharField(null=False, max_length=150)


class BankAccount(AbstractModel):
    number_account = models.CharField(null=False, max_length=150)
    destiny_account_type = models.CharField(null=False, max_length=150)
    bank_association = models.ForeignKey(BankDestiny, null=False, on_delete=models.PROTECT)


class DestinyAccount(AbstractModel):
    destiny_account_name = models.CharField(null=False, max_length=150)
    destiny_account_document_number = models.CharField(null=False, max_length=150)
    destiny_account_email = models.EmailField(null=False)
    bank_account = models.ForeignKey(BankAccount, null=False, on_delete=models.PROTECT)


class TransferConfirmation(AbstractModel):
    transfer_confirmation_date=models.DateTimeField(null=True)
    destiny_account = models.ForeignKey(DestinyAccount, null=False, on_delete=models.PROTECT)
