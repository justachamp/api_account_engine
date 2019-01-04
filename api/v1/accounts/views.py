from rest_framework.viewsets import ModelViewSet
from engine.models.users import User
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
