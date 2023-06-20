from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError
from timezone_field.rest_framework import TimeZoneSerializerField

from core.models import Client, Mailing, Message
from core.validators import validate_phone_number


class ClientSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(required=True)
    phone_number = serializers.CharField(max_length=11, validators=[validate_phone_number])

    class Meta:
        model = Client
        fields = '__all__'


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'

    def validate(self, data):
        if data['start_datetime'] >= data['end_datetime'] - timezone.timedelta(seconds=5):
            raise serializers.ValidationError("The end datetime should be at least 5 seconds greater than the start "
                                              "datetime.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

