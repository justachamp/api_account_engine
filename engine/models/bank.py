from django.db import models
from engine.models.abstract_model import AbstractModel

from engine.models.accounts import Account


class BankAccount(AbstractModel):
    """ Bank model, represents a banking institution

    """
    account = models.ForeignKey(Account,  null=False, on_delete=models.PROTECT)
    bank_account_number = models.IntegerField(null=False)
    account_notification_email = models.EmailField(null=False)
    bank_code = models.IntegerField(null=False)
    account_bank_type = models.IntegerField(null=False)
