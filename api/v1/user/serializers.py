import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction

from api.models import *


class UserBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email","profile_image"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        """Meta info."""

        model = User
        fields = [ "id", "first_name", "last_name",
                  "username", "email","password", "profile_image","user_uid","mobile"]

    def validate_first_name(self, value):
        # Validate that the first name contains only alphabets and is not less than 3 characters
        if not (value.isalpha() and len(value) >= 3):
            raise serializers.ValidationError(
                "The first name must be at least 3 characters long, contain only letters, and no spaces.")
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
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # Hash the password during the update
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        return super(UserSerializer, self).update(instance, validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for agent login."""

    mobile_or_email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        try:
            mobile_or_email = validated_data.get('mobile_or_email')
            password = validated_data.get('password')

            # Authenticate user using either email or username
            print("h1")
            user = authenticate(username=None, email=mobile_or_email, password=password, model=User,mobile=mobile_or_email)
         
            if not user:
                raise serializers.ValidationError("Invalid mobile or email, or incorrect password")

            token, created = Token.objects.get_or_create(user=user)
            return token.key

        except Exception as error_message:
            raise serializers.ValidationError(error_message)
