from django.db import models
from django.contrib.auth.models import User
from engine.models.abstract_model import AbstractModel
from django.core.exceptions import ValidationError
from decimal import Decimal


def positive_number(value):
    if value < Decimal(0):
        raise ValidationError("Must be positive")


class BatchState(AbstractModel):
    description = models.CharField(max_length=150)


class Batch(AbstractModel):
    #user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    #state = models.ForeignKey(BatchState, null=False, on_delete=models.PROTECT, default=1)
    description = models.CharField(max_length=150)
    total_amount = models.DecimalField(null=False, default=Decimal('0.00000'), max_digits=20, decimal_places=5, validators=[positive_number])
    #date = models.DateTimeField(editable=True)
