from django.db import models
from engine.models.abstract_model import AbstractModel
from engine.models.accounts import OperationAccount


class Instalment(AbstractModel):
    """

    """
    operation = models.ForeignKey(OperationAccount, default=None, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(null=False, default=0, max_digits=20, decimal_places=2)