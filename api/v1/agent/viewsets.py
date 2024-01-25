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
    http_method_names = ['get']
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

# class AgentViewSet(viewsets.ModelViewSet):
#     queryset = Agent.objects.all()
#     serializer_class = AgentSerializer

#     @action(detail=False, methods=['post'])
#     def register(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             agent = serializer.save()
#             return Response(AgentSerializer(agent).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, methods=['post'])
#     def login(self, request):
#         serializer = AgentLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             password = serializer.validated_data['password']
#             agent = authenticate(request, username=username, password=password)

#             if agent:
#                 login(request, agent)
#                 return Response(AgentSerializer(agent).data, status=status.HTTP_200_OK)

#         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)