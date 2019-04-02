from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers


from .accounts.views import AccountViewSet, OperationAccountViewSet, BalanceAccount, PositiveBalanceAccount, AccountTypeViewSet, BankRegistry
#from .income_types.views import IncomeTypeViewSet
from .journals.views import JournalViewSet, JournalTransactionTypeViewSet
from .journal_transactions.views import JournalTransaction, JournalOperationTransaction,\
    JournalOperationInvestmentTransaction, JournalRequesterPaymentFromOperation
from .engine_account_transactions.views import TransactionAccountDetail



from .batches.views import BatchStateViewSet, BatchDetail, BatchList
from .postings.views import PostingViewSet, AssetTypeViewSet
from .virtual_account.views import VirtualAccountDeposit
from .collection_module.views import GuaranteeDocumentViewSet, PaymentTransaction
from .billing_module.views import BillingReasonViewSet, BillingTransaction, BillingPayerView


router = routers.DefaultRouter()

# CAPA DE DATOS MOTOR DE CUENTAS
router.register(r'accounts', AccountViewSet)

router.register(r'operation_account', OperationAccountViewSet)
router.register(r'account_type', AccountTypeViewSet)

router.register(r'asset_types', AssetTypeViewSet)
router.register(r'batch_states', BatchStateViewSet)
router.register(r'journals', JournalViewSet)
router.register(r'postings', PostingViewSet)
router.register(r'journal_transaction_type', JournalTransactionTypeViewSet)


#CAPA DE DATOS MODULO DE COBRANZA
router.register(r'payment_request', GuaranteeDocumentViewSet)

#CAPA DE DATOS MODULO DE Facturacion (BillingModule)
router.register(r'billing_reazon', BillingReasonViewSet)





# CAPA LOGICA
urlpatterns = [

    #Motor de Cuentas
    path('batches/', BatchList.as_view(), name='batch-list'),
    path('batches/<int:pk>/', BatchDetail.as_view(), name='batch-detail'),
    path('journal_transactions/', JournalTransaction.as_view(), name='journal-transaction'),
    path('journal_transactions/operation', JournalOperationTransaction.as_view(), name='journal-transaction/operation'),
    path('journal_transactions/financing_operation/investment', JournalOperationInvestmentTransaction.as_view()),
    #Solicitud de pago a Solicitante
    path('journal_transactions/requester_payment_from_operation/', JournalRequesterPaymentFromOperation.as_view()),

    path('journal_transactions/requester_payment_from_operation/', JournalInstalmentPaymentTransaction.as_view()),


    path('virtual_account_deposit/', VirtualAccountDeposit.as_view(), name='virtual-account-deposit'),


    #S1
    path('account/balance/external_account_id/<str:ext_account_id>/external_account_type/<str:ext_account_type>/', BalanceAccount.as_view()),

    path('account/positive_balance/', PositiveBalanceAccount.as_view()),

    path('account/positive_balance/external_account_type/<int:entity_type>/', PositiveBalanceAccount.as_view()),

    #S2
    path('transaction/account_transaction/<str:external_account_id>/<int:external_account_type>/', TransactionAccountDetail.as_view()),

    #S3
    path('account/balance/<str:pk>/', BalanceAccount.as_view()),

    #S4
    #path('bank_transfer/last_transfer_account_data/<str:pk>/', .as_view()),




    #Modulo de cobranza y pagos
    path('payment_services/', PaymentTransaction.as_view(), name='payment-transaction'),

    #Modulo de Facturación
    path('billing/add_billing_transaction', BillingTransaction.as_view(), name='add-billing-transaction'),
    path('billing/billing_payer/', BillingPayerView.as_view()),
    path('billing/billing_payer/<int:pk>/', BillingPayerView.as_view()),


    #Modulo de Transferencias Bancarias
    path('account/billing_payer/<str:pk>/', BillingPayerView.as_view()),


    #modulo de Nóminas
    path('transaction/account_transaction/<str:pk>/', BillingPayerView.as_view()),


    #Bank Registry
    path('account/bank_registry/', BankRegistry.as_view())

]
urlpatterns = format_suffix_patterns(urlpatterns)
api_urlpatterns = router.urls + urlpatterns

