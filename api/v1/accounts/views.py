from rest_framework.viewsets import ModelViewSet
from engine.models.accounts import Account, OperationAccount, AccountType
from .serializers import AccountSerializer, OperationAccountSerializer,AccountTypeSerializer, BankRegistrySerializer
from rest_framework.views import APIView
from engine.services.account_services import BalanceAccountService, PositiveBalanceAccountService
from rest_framework.response import Response
from rest_framework import status


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class AccountTypeViewSet(ModelViewSet):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer


class OperationAccountViewSet(ModelViewSet):
    queryset = OperationAccount.objects.all()
    serializer_class = OperationAccountSerializer


class OperationAccount(APIView):

    def post(self, request, format=None):
        """
        Create a new Batch with this format
        {
            "transaction_type":1,
            "from_account":1,
            "to_account":2,
            "amount":9900,
            "asset_type":1
        }

        :return: a new journal
        """

        serializer= OperationAccountSerializer(data=request.data)
        if serializer.is_valid():
            json_data=serializer.save()
            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BalanceAccount(APIView):

    def get(self, request, ext_account_id, ext_account_type  ):
        try:
            balance_account = BalanceAccountService.execute(
                 {
                     "external_account_id": ext_account_id,
                     "external_account_type_id":ext_account_type
                 }
            )

            return Response(balance_account, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class PositiveBalanceAccount(APIView):

    def get(self, request, entity_type=None):

        try:
            positive_balance_data = PositiveBalanceAccountService.execute({
                "entity_type": entity_type
            })
            return Response(positive_balance_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class BankRegistry(APIView):

    def get(self, request, entity_type=None):

        try:
            positive_balance_data = PositiveBalanceAccountService.execute({
                "entity_type": entity_type
            })

            return Response(positive_balance_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        """
        Create a new Bank Registry to account with this format
        {
           "account_notification_email": "cumplo@cumplo.com",
            "external_account_id": 2,
            "external_account_type": 4,
            "bank_code": 1,
            "account_bank_type": 1,
            "bank_account_number": "65868962",
            "account_holder_name" : "Juan papa",
            "account_holder_document_number": "15828916-4"
        }

        :return: a new BankAccount
        """

        serializer = BankRegistrySerializer(data=request.data)
        if serializer.is_valid():
            json_data = serializer.save()
            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
