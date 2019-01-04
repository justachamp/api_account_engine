from rest_framework.viewsets import ModelViewSet
from engine.models.accounts import Account
from .serializers import AccountSerializer


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
