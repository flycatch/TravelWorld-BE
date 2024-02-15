from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email"]