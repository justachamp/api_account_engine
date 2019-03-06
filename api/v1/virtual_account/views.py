from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from .serializers import VirtualAccountDepositSerializer
from rest_framework.response import Response
from django.forms.models import model_to_dict
from django.core import serializers
import json

class VirtualAccountDeposit(APIView):
    """
    List all batches or create a new batch with journals
    """
    def get(self, request, format=None):
        print("GET BATCH!!!")
        """
        List all batches
        """

        return request#Response(serializer.data)

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


        serializer= VirtualAccountDepositSerializer(data=request.data)
        if serializer.is_valid():
            print("Estructura valida para VirtualAccountDepositSerializer")
            #TODO: validar que el id de cuenta real y cuenta virtual estan vinculadas
           # if make_real_virtual_deposit_validation(serializer.data['real_account'], serializer.data['virtual_account'],serializer.data['amount']):
            #try:
            data = serializer.save()
            print("Journal Save")
            print(data)
            return Response(model_to_dict(data), status=status.HTTP_201_CREATED)
            #else:


        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



