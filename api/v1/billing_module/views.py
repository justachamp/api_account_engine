from rest_framework.viewsets import ModelViewSet
from billing_module.models.billing import BillingReason, BillingPayer, HistoricBillingContact
from billing_module.serializers.serializers import BillingReasonSerializers, BillingTransactionSerializers, \
    HistoricBillingContactSerializers, BillingContactPayerSerializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.forms.models import model_to_dict


class BillingReasonViewSet(ModelViewSet):
    queryset = BillingReason.objects.all()
    serializer_class = BillingReasonSerializers


class BillingPayerView(APIView):
    """
       List all batches or create a new batch with journals
       """

    def get(self, request, pk):
        # pk=self.kwargs['pk']
        print(pk)
        print(request)

        glass_json = self.get_serialized(pk)
        print(glass_json)

        return request  # Response(serializer.data)

    def get_serialized(self, pk):
        billing_payer = BillingPayer.objects.filter(id=pk).get()
        billing_contact_payer = HistoricBillingContact.objects.filter(base_contact=billing_payer).order_by('-id')[
                                0:1].get()
        serializer = HistoricBillingContactSerializers(data=billing_contact_payer)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            return data["json"]
        else:
            return serializer.errors

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
        serializer = BillingContactPayerSerializers(data=request.data)

        if serializer.is_valid():
            json_data = serializer.save()

            return Response(model_to_dict(json_data), status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = BillingContactPayerSerializers(data=request.data)

        if serializer.is_valid():
            json_data = serializer.save()

            return Response(model_to_dict(json_data), status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BillingTransaction(APIView):
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
        serializer = BillingTransactionSerializers(data=request.data)

        if serializer.is_valid():
            print("Estructura valida para JournalTransaction")
            # TODO: validar transacciones por doble partida, No aplica

            # TODO: Validar que las cuentas no sean la misma

            # TODO: Validar transacciones por Materialización

            print("Iniciando el Servicio!!")
            json_data = serializer.save()

            print("Flag 2 Se terminó el servicio")

            return Response(json_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
