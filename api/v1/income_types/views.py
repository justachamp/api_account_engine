from rest_framework.viewsets import ModelViewSet
from engine.models.journals import IncomeType
from .serializers import IncomeTypeSerializer


class IncomeTypeViewSet(ModelViewSet):
    queryset = IncomeType.objects.all()
    serializer_class = IncomeTypeSerializer
