from django.db import models
from engine.models import AbstractModel
from .collection_state import CollectionState
from .document_type import DocumentType
from .payer import Payer


class GuaranteeDocument(AbstractModel):
    state = models.ForeignKey(CollectionState, null=False, on_delete=models.PROTECT)
    document_type = models.ForeignKey(DocumentType, null=False, on_delete=models.PROTECT)
    payer = models.ForeignKey(Payer,  null=False, on_delete=models.PROTECT)

    payment_date = models.DateField(null=False,)
    payment_amount = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    external_id = models.CharField(unique=True, max_length=150)
    external_operation_id = models.CharField(max_length=150)

    #fines = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    document_description = models.CharField(max_length=350)

