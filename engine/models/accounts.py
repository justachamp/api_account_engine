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


class Account(AbstractModel):
    name = models.CharField(max_length=150)


class BankAccount(AbstractModel):
    """ Bank account model, represent an account in a bank

    Attributes:
        number (CharField): the number of the bank account, this attribute can have numbers (0-9) and dash (-)
    """

    number = models.CharField(max_length=200)
    account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT)
    bank = models.ForeignKey(Bank, null=False, on_delete=models.PROTECT)