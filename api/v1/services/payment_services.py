from engine.models import Posting

SERVICE_NAME = "virtual_payment_services"

def make_virtual_balance_validation( from_account_posting, to_account_posting ):
    print(from_account_posting)
    print(to_account_posting)



def make_virtual_payment_materialization(account, amount):

    posting = Posting(account)
    print(amount)

def get_virtual_balance_amount_account(account):
    print(account)

