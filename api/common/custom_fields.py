from api.common.library import encode, decode
from rest_framework import serializers


class IdencodeField(serializers.CharField):
    """Encoded id field."""

    serializer = None
    related_model = None

    def __init__(self, serializer=None, related_model=None, *args, **kwargs):
        """Initializing field object."""
        self.serializer = serializer
        self.related_model = related_model
        super(IdencodeField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        """
        Override the returning method.

        This function will check if the serializer is supplied
        in case of foreign key field. In case of foreign key, the
        value will be and object. If it is  normal id then it is
        going to be type int.
        """
        if not value:
            return None
        if self.serializer:
            return self.serializer(value).data
        if isinstance(value, int):
            return encode(value)
        try:
            return encode(value.id)
        except:
            return None

    def to_internal_value(self, value):
        """To convert value for saving."""
        if self.related_model and isinstance(value, self.related_model):
            return value
        try:
            value = int(value)
        except:
            value = decode(value)
        if not value:
            raise serializers.ValidationError("Invalid id/pk format")
        related_model = self.related_model
        if not related_model:
            try:
                related_model = self.parent.Meta.model._meta.get_field(
                    self.source
                ).related_model
            except:
                raise serializers.ValidationError(
                    "Invalid key, the key should be same as the model. "
                )
        try:
            return related_model.objects.get(id=value)
        except:
            raise serializers.ValidationError("Invalid pk - object does not exist.")
