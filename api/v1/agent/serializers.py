# serializers.py
import re
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

    def validate_first_name(self, value):
        # Validate that the first name contains only alphabets and is not less than 3 characters
        if not (value.isalpha() and len(value) >= 3):
            raise serializers.ValidationError("First name should contain only alphabets and be at least 3 characters long.")
        return value

    def validate_last_name(self, value):
        # Validate that the last name contains only alphabets
        if not value.isalpha():
            raise serializers.ValidationError("Last name should contain only alphabets.")
        return value

    def validate_email(self, value):
        # Validate that the email is in a valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_phone(self, value):
        # Validate that the phone number is less than 13 characters and contains only digits
        if not value.isdigit() or len(value) > 13:
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate_password(self, value):
        # Validate that the password is at least 8 characters, contains one capital letter, and symbols
        if len(value) < 8 or not any(char.isupper() for char in value) or not any(char in '!@#$%^&*()_-+=<>,.?/:;{}[]|' for char in value):
            raise serializers.ValidationError("Password should be at least 8 characters and contain one capital letter and symbols.")
        return value
    
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

        # Check if Agent exists and has an approved stage
        try:
            agent = Agent.objects.get(username=username)
            if agent.stage != 'approved':
                if agent.stage == 'rejected':
                    raise serializers.ValidationError({"message": "Agent is rejected by admin"})
                else:
                    raise serializers.ValidationError({"message": "Agent not approved by admin"})
        except Agent.DoesNotExist:
            raise serializers.ValidationError({"message": "Agent not found"})

        data['user'] = user
        return data
