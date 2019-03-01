from rest_framework.viewsets import ModelViewSet
from engine.models.accounts import Account, OperationAccount
from .serializers import AccountSerializer, OperationAccountSerializer
from django.http import Http404
from rest_framework.views import APIView


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class OperationAccountViewSet(ModelViewSet):
    queryset = OperationAccount.objects.all()
    serializer_class = OperationAccountSerializer



class AccountDetailList(APIView):
    """
    List all batches or create a new batch with journals
    """
    def get(self, request, format=None):
        """
        List all batches
        """
        AccountDetailList = Account.objects.all()
        batches = Batch.objects.all()
        serializer = BatchSerializer(batches, context={'request': request}, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create a new Batch with this format
        {
            "description": "a description",
            "total_amount": 2,
            "date": "2019-01-04 10:00:00",
            "journals": [
                {
                    "gloss": "first movement",
                    "amount": "1.00000",
                    "date": "2012-12-12T12:12:00Z",
                    "incomeType": 1,
                    "from_account": 1,
                    "to_account": 2,
                    "assetType": 1
                },
                {
                    "gloss": "second movement",
                    "amount": "1.00000",
                    "date": "2012-12-12T12:12:00Z",
                    "incomeType": 1,
                    "from_account": 2,
                    "to_account": 1,
                    "assetType": 1
                }
            ]
        }
        :return: a new batch
        """
        serializer = BatchSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


