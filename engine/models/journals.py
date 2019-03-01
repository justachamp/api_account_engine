from django.db import models
from engine.models.abstract_model import AbstractModel
from engine.models.batches import Batch
from engine.models.accounts import Account


#class IncomeType(AbstractModel):
#    description = models.CharField(max_length=150)
class Journal_transaction_type(AbstractModel):

    description = models.TextField(max_length=150)

class Journal(AbstractModel):
    batch = models.ForeignKey(Batch, null=True, on_delete=models.PROTECT, related_name='journals')
    gloss = models.TextField(max_length=350)
    journal_transaction = models.ForeignKey(Journal_transaction_type,default=None, null=False, on_delete=models.PROTECT)
    #from_account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT, related_name='from_account')
    #to_account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT, related_name='to_account')
    #amount = models.DecimalField(null=False, default=0, max_digits=20, decimal_places=5)
    #assetType = models.ForeignKey(AssetType, default=1, null=False, on_delete=models.PROTECT)
    #date = models.DateTimeField(editable=True)