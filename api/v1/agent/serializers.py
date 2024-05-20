# serializers.py
import re

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from api.models import Agent, AgentBankDetails
from django.core.validators import FileExtensionValidator, RegexValidator


class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for Agent model.

    This serializer handles serialization and deserialization of Agent objects.
    It includes validation rules for various fields like first name, last name, email, phone, and password.

    **Fields:**

    * id (ReadOnly): The unique identifier of the Agent object.
    * first_name: The first name of the agent.
    * username: The username of the agent for login (required).
    * last_name: The last name of the agent.
    * email: The email address of the agent (required).
    * phone: The phone number of the agent.
    * password (WriteOnly): The password of the agent (write-only field, not returned in responses).
    * profile_image: The profile image of the agent (optional).
    * agent_uid: Unique agent identifier (optional).
    * agent_name: Agent's full name (optional).
    * company_id: ID of the company the agent belongs to (optional).
    * company_name: Name of the company the agent belongs to (optional).
    * company_site: Company website (optional).
    * message: Message from the agent (optional).
    * account_verification_status: Account verification status of the agent (optional, read-only).

    **Validation:**

    * First name: Must be at least 3 characters, contain only letters, and no spaces.
    * Last name: Must contain only alphabets and spaces.
    * Email: Must be in a valid email format.
    * Phone number: Must be less than 13 characters and contain only digits.
    * Password: Must be at least 8 characters, include one capital letter, and symbols.

    **Methods:**

    * **create:** Creates a new Agent object, hashing the password before saving.
    * **update:** Updates an existing Agent object, hashing the password if it's provided in the update data.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'},required=False)
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=True)
    account_verification_status = serializers.CharField(required=False)

    class Meta:
        """Meta info."""

        model = Agent
        fields = [ "id", "first_name", "username", "last_name", "email",
                  "phone", "password", "confirm_password","profile_image","agent_uid","agent_name",
                  "company_id", "company_name", "company_site", "message",
                  "account_verification_status"]

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
    
    def validate(self, data):
        # Ensure password and confirm_password match
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(AgentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # Hash the password during the update
        if 'password' in validated_data:
            validated_data.pop('confirm_password')
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

        try:
            # Authenticate user using either email or username
            user = authenticate(username=username_or_email, email=username_or_email, password=password, model=Agent)

            # If user is not authenticated, raise AuthenticationFailed exception
            if user is None:
                raise AuthenticationFailed('Invalid username or email, or incorrect password')

            # Check if Agent exists and has an approved stage
            try:
                agent = Agent.objects.get(email=user.email)
                if agent.stage != 'approved':
                    if agent.stage == 'rejected':
                        raise AuthenticationFailed('Agent is rejected by admin')
                    else:
                        raise AuthenticationFailed('Agent not approved by admin')
            except Agent.DoesNotExist:
                raise AuthenticationFailed('Agent not found')

            # Generate token and construct response
            token, created = Token.objects.get_or_create(user=user)
            return token.key

        except AuthenticationFailed as e:
            raise e  # Re-raise AuthenticationFailed exceptions as they are already specific
        except Exception as e:
            # Handle any other exceptions that may occur during authentication
            raise AuthenticationFailed('Invalid username or email, or incorrect password')


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[RegexValidator(regex=(
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})"), message="Password must have minimum 8 characters, alphanumeric with at least one uppercase, one lowercase and one special character.", code='invalid_password')])
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"message": "Passwords do not match."})
        return data

class BookingAgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ["id","agent_uid","username",'agent_name',"phone","email", "profile_image"]


class AgentBankDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for Agent Bank Details model.

    This serializer defines the fields that can be included when serializing or 
    deserializing AgentBankDetails objects.
    The `agent` field is marked as read-only as it's automatically set based 
    on the authenticated user.

    **Fields:**

    * id (ReadOnly): The unique identifier of the AgentBankDetails object.
    * agent (ReadOnly): The Agent associated with the bank details.
        agent will automatically fetched from token.
    * account_holder_name: The name of the account holder.
    * account_number: The account number of the bank account.
    * ifsc_code: The IFSC code of the bank branch.
    * cancelled_cheque: The uploaded cancelled cheque image (optional).
    """
    class Meta:
        model = AgentBankDetails
        fields = ['id', 'agent', 'account_holder_name', 'bank_name',
                  'account_number', 'ifsc_code', 'cancelled_cheque']
        read_only_fields = ['agent']  # Mark 'agent' field as read-only

    def create(self, validated_data):
        # Get the current logged-in user from the context
        user = self.context['request'].user
        # Set the 'agent' field to the current user's agent
        validated_data['agent'] = user.agent
        # Create and return the AgentBankDetails instance
        return AgentBankDetails.objects.create(**validated_data)