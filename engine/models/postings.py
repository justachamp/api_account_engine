from django.db import models
from engine.models.abstract_model import AbstractModel
from engine.models.accounts import Account
from engine.models.journals import Journal, AssetType


class Posting(AbstractModel):
    account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT)
    journal = models.ForeignKey(Journal, null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(null=False, default=0, max_digits=20, decimal_places=5)
    assetType = models.ForeignKey(AssetType, default=1, null=False, on_delete=models.PROTECT)
    date = models.DateTimeField(editable=True)
