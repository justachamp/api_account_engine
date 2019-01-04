from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from .accounts.views import AccountViewSet
from .income_types.views import IncomeTypeViewSet
from .journals.views import JournalViewSet, AssetTypeViewSet
from .batches.views import BatchStateViewSet, BatchDetail, BatchList
from .postings.views import PostingViewSet


router = routers.DefaultRouter()

# CAPA DE DATOS
router.register(r'accounts', AccountViewSet)
router.register(r'income_types', IncomeTypeViewSet)
router.register(r'asset_types', AssetTypeViewSet)
router.register(r'batch_states', BatchStateViewSet)
router.register(r'journals', JournalViewSet)
router.register(r'postings', PostingViewSet)

# CAPA LOGICA
urlpatterns = [
    path('batches/', BatchList.as_view(), name='batch-list'),
    path('batches/<int:pk>/', BatchDetail.as_view(), name='batch-detail'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
api_urlpatterns = router.urls + urlpatterns
