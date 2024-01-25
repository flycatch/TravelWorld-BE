# serializers.py
from rest_framework import serializers
from api.models import Agent
from django.contrib.auth import authenticate
# from api.common.custom_fields import IdencodeField
from django.contrib.auth.hashers import make_password


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for user."""

    # id = IdencodeField(read_only=True)

    class Meta:
        """Meta info."""

        model = Agent
        fields = [ "id", "username", "first_name",
                  "last_name", "email", "phone", "password"]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(AgentSerializer, self).create(validated_data)


class AgentLoginSerializer(serializers.Serializer):
    """Serializer for agent login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def to_representation(self, instance):
        # Override the default representation to format the error message
        return {'credentials': instance}

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"message": "Invalid credentials"})

        # Check if Agent is approved and not rejected
        try:
            agent = Agent.objects.get(username=username)
            print(agent)
            if not agent.is_approved:
                raise serializers.ValidationError({"message": "Agent not approved"})
            if agent.is_rejected:
                raise serializers.ValidationError({"message": "Agent rejected"})
        except Agent.DoesNotExist:
            raise serializers.ValidationError({"message": "Agent not found"})

        data['user'] = user
        return data
