from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from .accounts.views import AccountViewSet, OperationAccountViewSet
#from .income_types.views import IncomeTypeViewSet
from .journals.views import JournalViewSet,JournalTransactionTypeViewSet
from .journal_transactions.views import JournalTransaction, JournalOperationTransaction



from .batches.views import BatchStateViewSet, BatchDetail, BatchList
from .postings.views import PostingViewSet, AssetTypeViewSet
from .virtual_account.views import VirtualAccountDeposit
from .collection_module.views import GuaranteeDocumentViewSet, PaymentTransaction
from .billing_module.views import BillingReasonViewSet, BillingTransaction, BillingPayerView


router = routers.DefaultRouter()

# CAPA DE DATOS MOTOR DE CUENTAS
router.register(r'accounts', AccountViewSet)
router.register(r'operation_account', OperationAccountViewSet)
#router.register(r'income_types', IncomeTypeViewSet)
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
    path('batches/', BatchList.as_view(), name='batch-list'),
    path('batches/<int:pk>/', BatchDetail.as_view(), name='batch-detail'),
    path('journal_transactions/', JournalTransaction.as_view(), name='journal-transaction'),
    path('journal_transactions/operation', JournalOperationTransaction.as_view(), name='journal-transaction/operation'),
    path('virtual_account_deposit/', VirtualAccountDeposit.as_view(), name='virtual-account-deposit'),

    #Modulo de cobranza y pagos
    path('payment_services/', PaymentTransaction.as_view(), name='payment-transaction'),

    #Modulo de Facturación
    path('billing/add_billing_transaction', BillingTransaction.as_view(), name='add-billing-transaction'),
    path('billing/billing_payer/', BillingPayerView.as_view()),
    path('billing/billing_payer/<int:pk>/', BillingPayerView.as_view()),





]
urlpatterns = format_suffix_patterns(urlpatterns)
api_urlpatterns = router.urls + urlpatterns

