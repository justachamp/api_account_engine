from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status

from engine.models.batches import Batch, BatchState
from .serializers import BatchSerializer, BatchStateSerializer, BatchPutSerializer



class BatchStateViewSet(ModelViewSet):
    queryset = BatchState.objects.all()
    serializer_class = BatchStateSerializer


class BatchList(APIView):
    """
    List all batches or create a new batch with journals
    """
    def get(self, request, format=None):
        print("GET BATCH!!!")
        """
        List all batches
        """
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

        #try:
        print("Flag 1 POST Batch!!!")
        print(request)
        serializer = BatchSerializer(data=request.data, context={'request': request})
        print("Flag 2 POST Batch!!!")
        if serializer.is_valid():





            # Servicio de Pago entre cuentas



            # Si el servicio responde ok. Transacciones ok
            # Si el servicio responde fail, entonces retornar mensaje de error

            serializer.save()
            print("Flag 3 POST Batch!!!")
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #except:

            #return Response("Error", status=status.HTTP_400_BAD_REQUEST)


class BatchDetail(APIView):
    """
    Retrieve, Update a Batch object
    """

    def get_object(self, pk):
        """
        Find Batch object given a ID
        :param pk: id of a batch
        :return: Batch object
        """
        try:
            return Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Display a Batch object given a pk ID
        :param pk: Batch id
        :return: Batch data
        """
        batch = self.get_object(pk)
        serializer = BatchSerializer(batch, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """
        Update a Batch, only state is available
        :param pk: Batch id
        :return: Batch data or error if present
        """
        batch = self.get_object(pk)
        serializer = BatchPutSerializer(batch, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        NOT ALLOWED TO DELETE A BATCH
        :param request:
        :param pk: Batch id
        :param format:
        :return: Response 405
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
