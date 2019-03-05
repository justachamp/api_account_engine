from django.db import models
from engine.models import AbstractModel


class CollectionState(AbstractModel):
    state_description = models.CharField(max_length=150)