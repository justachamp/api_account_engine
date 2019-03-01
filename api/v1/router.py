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


router = routers.DefaultRouter()

# CAPA DE DATOS
router.register(r'accounts', AccountViewSet)
router.register(r'operation_account', OperationAccountViewSet)
#router.register(r'income_types', IncomeTypeViewSet)
router.register(r'asset_types', AssetTypeViewSet)
router.register(r'batch_states', BatchStateViewSet)
router.register(r'journals', JournalViewSet)
router.register(r'postings', PostingViewSet)
router.register(r'journal_transaction_type', JournalTransactionTypeViewSet)

# CAPA LOGICA
urlpatterns = [
    path('batches/', BatchList.as_view(), name='batch-list'),
    path('batches/<int:pk>/', BatchDetail.as_view(), name='batch-detail'),
    path('journal_transactions/', JournalTransaction.as_view(), name='journal-transaction'),
    path('journal_transactions/operation', JournalOperationTransaction.as_view(), name='journal-transaction/operation'),
    path('virtual_account_deposit/', VirtualAccountDeposit.as_view(), name='virtual-account-deposit'),

]
urlpatterns = format_suffix_patterns(urlpatterns)
api_urlpatterns = router.urls + urlpatterns
