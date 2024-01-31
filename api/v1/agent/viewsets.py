from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from api.models import Agent
from api.v1.agent.serializers import AgentSerializer, AgentLoginSerializer


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    http_method_names = ['get','put']
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    http_method_names = ['post']


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = AgentLoginSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'status': 'success', 'message': 'Login successful',
            'token': token.key}, status=status.HTTP_200_OK
            )