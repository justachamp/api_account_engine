from django.db import models


class AbstractModel(models.Model):
    """
    Abstract base model for all models, to simplify the addiction of the fields created and updated

    Attributes:
        created (DateTimeField): Date time when the object was created
        updated (DateTimeField): Date time of the last update of the object

    """

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
