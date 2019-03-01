from django.db import models
from engine.models.abstract_model import AbstractModel
from engine.models.accounts import Account,OperationAccount
from engine.models.postings import Posting



class PaymentRequest(Posting):
    """
    Cuenta por pagar
    """
    account_payer = models.ForeignKey(Account, default=None, null=False, on_delete=models.PROTECT, related_name='account_payer')




