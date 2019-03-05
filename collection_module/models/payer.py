from django.db import models
from engine.models import AbstractModel


class Payer(AbstractModel):
    name = models.CharField(max_length=150)
    external_id = models.CharField(unique=True, max_length=150)
    contact_data = models.EmailField(max_length=150)
