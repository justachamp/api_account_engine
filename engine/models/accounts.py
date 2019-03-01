from django.db import models
from engine.models.abstract_model import AbstractModel


class Bank(AbstractModel):
    """ Bank model, represents a banking institution

    Attributes:
        name (CharField): Name of the bank
        external_code (CharField): Bank's code

    """
    name = models.CharField(max_length=200)
    external_code = models.CharField(max_length=10)


class RealAccount(AbstractModel):
    """ Real account with bank association model, represent an account in a bank

       Attributes:
           number (CharField): the number of the bank account, this attribute can have numbers (0-9) and dash (-)
       """
    bank = models.ForeignKey(Bank, null=False, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    document_number = models.CharField(max_length=150)
    email = models.CharField(max_length=150)


class Account(AbstractModel):
    name = models.CharField(max_length=150)
    real_account = models.ForeignKey(RealAccount, null=True, on_delete=models.PROTECT)


class OperationAccount(Account):
    financing_amount = models.DecimalField(null=False, decimal_places=5, default=0, max_digits=20)
    external_operacion_account_id= models.IntegerField(null=False, default=None, unique=True)



