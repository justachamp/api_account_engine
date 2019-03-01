from engine.models import Posting
from django.db.models import Sum
from decimal import Decimal

SERVICE_NAME = "virtual_payment_services"


def make_virtual_balance_validation( from_account_posting, to_account_posting ):
    print(from_account_posting)
    print(to_account_posting)


def make_virtual_payment_materialization(account, amount_to_materialize):

    account_posting_amount = Posting.objects.filter(account=account).aggregate(Sum('amount'))
    #posting = Posting(account)
    print(account_posting_amount)
    if account_posting_amount['amount__sum'] is not None and account_posting_amount['amount__sum'] >= Decimal(amount_to_materialize):
        return True
    else:
        return False


def get_virtual_balance_amount_account(account):
    print(account)


def make_real_virtual_deposit_validation(real_account_id, virtual_account_id, amount):
    """
    Valida que las cuenta virtual sea parte de la cuenta real
    :return: Boolean
    """
    #TODO: realizar los ajustes para relacionar cuentas virtuales y cuentas reales, probablemente, para que no se generen mezclas, sea apropiado que las cuentas reales esten en otro modelo
    return True




