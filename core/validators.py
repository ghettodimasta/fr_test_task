from django.core.exceptions import ValidationError


def validate_phone_number(value):
    if not value.startswith('7') or not value.isdigit() or len(value) != 11:
        raise ValidationError('Invalid phone number format. The phone number should start with 7 and consist of 11 digits.')