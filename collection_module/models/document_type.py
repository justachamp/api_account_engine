from django.db import models
from engine.models import AbstractModel


class DocumentType(AbstractModel):
    description = models.CharField(max_length=150)