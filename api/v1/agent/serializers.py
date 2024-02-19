# serializers.py
import re

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.models import Agent
from django.core.validators import FileExtensionValidator, RegexValidator


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for user."""
    class Meta:
        """Meta info."""

        model = Agent
        fields = [ "id", "first_name", "username",
                  "last_name", "email", "phone", "password", "profile_image"]

    def validate_first_name(self, value):
        # Validate that the first name contains only alphabets and is not less than 3 characters
        if not (value.isalpha() and len(value) >= 3):
            raise serializers.ValidationError(
                "First name should contain only alphabets and be at least 3 characters long, \
                and no whitespace is allowed.")
        return value

    def validate_last_name(self, value):
        # Validate that the last name contains only alphabets and spaces
        if not all(char.isalpha() or char.isspace() for char in value):
            raise serializers.ValidationError("Last name should contain only alphabets and spaces.")
        return value

    def validate_email(self, value):
        # Validate that the email is in a valid format
        # r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
            raise serializers.ValidationError(
                "Password should be at least 8 characters and contain one capital letter and symbols.")
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(AgentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # Hash the password during the update
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        return super(AgentSerializer, self).update(instance, validated_data)


class AgentLoginSerializer(serializers.Serializer):
    """Serializer for agent login."""

    username_or_email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        username_or_email = validated_data.get('username_or_email')
        password = validated_data.get('password')

        # Authenticate user using either email or username
        user = authenticate(username=username_or_email, email=username_or_email, password=password)
        if not user:
            raise serializers.ValidationError({"message": "Invalid credentials"})

        # Check if Agent exists and has an approved stage
        try:
            agent = Agent.objects.get(email=user.email)
            if agent.stage != 'approved':
                if agent.stage == 'rejected':
                    raise serializers.ValidationError({"message": "Agent is rejected by admin"})
                else:
                    raise serializers.ValidationError({"message": "Agent not approved by admin"})
        except Agent.DoesNotExist:
            raise serializers.ValidationError({"message": "Agent not found"})

        # Generate token and construct response
        token, created = Token.objects.get_or_create(user=user)
        return {
            'status': 'success',
            'message': 'Login successful',
            'token': token.key
        }



class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[RegexValidator(regex=(
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})"), message="Password must have minimum 8 characters, alphanumeric with at least one uppercase, one lowercase and one special character.", code='invalid_password')])
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

class BookingAgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ["id","agent_uid","username","first_name","last_name","email"]