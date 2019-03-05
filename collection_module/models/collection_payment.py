from django.db import models
from engine.models import AbstractModel
from .payer import Payer


class Payment(AbstractModel):
    payment_payer = models.ForeignKey(Payer, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    external_operation_id = models.CharField(null=False, max_length=150)