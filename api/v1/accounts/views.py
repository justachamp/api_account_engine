from rest_framework.viewsets import ModelViewSet
from engine.models.accounts import Account, OperationAccount, AccountType
from .serializers import AccountSerializer, OperationAccountSerializer,AccountTypeSerializer, BankRegistrySerializer
from django.http import Http404
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
            print("Estructura valida para JournalTransaction")

            json_data=serializer.save()
            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BalanceAccount(APIView):

    def get(self, request, ext_account_id, ext_account_type  ):

        print(ext_account_id)
        print(ext_account_type)



        try:
            balance_account = BalanceAccountService.execute(
                 {
                     "external_account_id": ext_account_id,
                     "external_account_type_id":ext_account_type
                 }
            )

            return Response(balance_account, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class PositiveBalanceAccount(APIView):

    def get(self, request, entity_type=None):

        try:
            positive_balance_data = PositiveBalanceAccountService.execute({
                "entity_type": entity_type
            })
            print(positive_balance_data)
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
         "external_account_type":2,
         "external_account_id":1234,
         "account_number": "2154",
         "email": "ro@cumplo.com",
         "default_account": false,
         "bank": "codigo_banco",
         "account_type": 2
        }

        :return: a new journal
        """

        serializer = BankRegistrySerializer(data=request.data)
        if serializer.is_valid():
            print("Estructura valida para JournalTransaction")

            json_data = serializer.save()
            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
#
# class AccountDetailList(APIView):
#     """
#     List all batches or create a new batch with journals
#     """
#     def get(self, request, format=None):
#         """
#         List all batches
#         """
#         AccountDetailList = Account.objects.all()
#         batches = Batch.objects.all()
#         serializer = BatchSerializer(batches, context={'request': request}, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         """
#         Create a new Batch with this format
#         {
#             "description": "a description",
#             "total_amount": 2,
#             "date": "2019-01-04 10:00:00",
#             "journals": [
#                 {
#                     "gloss": "first movement",
#                     "amount": "1.00000",
#                     "date": "2012-12-12T12:12:00Z",
#                     "incomeType": 1,
#                     "from_account": 1,
#                     "to_account": 2,
#                     "assetType": 1
#                 },
#                 {
#                     "gloss": "second movement",
#                     "amount": "1.00000",
#                     "date": "2012-12-12T12:12:00Z",
#                     "incomeType": 1,
#                     "from_account": 2,
#                     "to_account": 1,
#                     "assetType": 1
#                 }
#             ]
#         }
#         :return: a new batch
#         """
#         serializer = BatchSerializer(data=request.data, context={'request': request})
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
