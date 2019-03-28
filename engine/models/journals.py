from django.db import models
from engine.models.abstract_model import AbstractModel
from engine.models.batches import Batch
from engine.models.accounts import Account


class JournalTransactionType(AbstractModel):

    description = models.TextField(max_length=150)


class Journal(AbstractModel):
    batch = models.ForeignKey(Batch, null=True, on_delete=models.PROTECT, related_name='journals')
    gloss = models.TextField(max_length=350)
    journal_transaction = models.ForeignKey(JournalTransactionType, default=None, null=False, on_delete=models.PROTECT)