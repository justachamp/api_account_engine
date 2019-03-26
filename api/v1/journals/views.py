from rest_framework.viewsets import ModelViewSet
from engine.models.journals import Journal, JournalTransactionType
from .serializers import JournalSerializer, JournalTransactionTypeSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


class JournalViewSet(ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer


class JournalTransactionTypeViewSet(ModelViewSet):
    queryset = JournalTransactionType.objects.all()
    serializer_class = JournalTransactionTypeSerializer


