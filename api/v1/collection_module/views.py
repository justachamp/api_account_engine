from rest_framework.viewsets import ModelViewSet
from engine.models.journals import Journal, Journal_transaction_type
from collection_module.models import GuaranteeDocument, Payment
from .serializers import GuaranteeDocumentSerializers, PaymentSerializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


class GuaranteeDocumentViewSet(ModelViewSet):
    queryset = GuaranteeDocument.objects.all()
    serializer_class = GuaranteeDocumentSerializers


class PaymentTransaction(APIView):
    """
    List all batches or create a new batch with journals
    """

    def get(self, request, format=None):
        print("GET BATCH!!!")
        """
        List all batches
        """

        return request  # Response(serializer.data)

    def post(self, request, format=None):
        """
        Create a new Payment with this format
        {
            "transaction_type":1,
            "from_account":1,
            "to_account":2,
            "amount":9900,
            "asset_type":1
        }

        :return: a new journal
        """
        serializer = PaymentSerializers(data=request.data)

        if serializer.is_valid():
            print("Estructura valida para JournalTransaction")
            # TODO: validar transacciones por doble partida, No aplica

            # TODO: Validar que las cuentas no sean la misma

            # TODO: Validar transacciones por Materialización

            print("Iniciando el Servicio!!")
            json_data=serializer.save()

            print("Flag 2 Se terminó el servicio")

            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
