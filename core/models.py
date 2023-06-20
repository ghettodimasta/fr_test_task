from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from timezone_field import TimeZoneField
from core.validators import validate_phone_number


# Create your models here.


class Mailing(models.Model):
    start_datetime = models.DateTimeField()
    message_text = models.TextField()
    client_filter_operator_code = models.CharField(max_length=10)
    client_filter_tag = models.CharField(max_length=255)
    end_datetime = models.DateTimeField()

    def clean(self):
        if self.start_datetime >= self.end_datetime - timezone.timedelta(seconds=5):
            raise ValidationError("The end datetime should be at least 5 seconds greater than the start datetime.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Client(models.Model):
    phone_number = models.CharField(max_length=11)
    operator_code = models.CharField(max_length=6)
    tag = models.CharField(max_length=255)
    timezone = TimeZoneField(default='Europe/Moscow')


class Message(models.Model):
    creation_datetime = models.DateTimeField()
    delivery_status = models.CharField(max_length=255)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


@receiver(post_save, sender=Mailing)
def pend_mailing(sender, instance, created, **kwargs):
    if created:
        now = timezone.now()
        from .tasks import send_messages
        if instance.start_datetime <= now <= instance.end_datetime:
            send_messages.delay(instance.id)
        elif instance.start_datetime > now:
            delay = instance.start_datetime - now
            send_messages.apply_async(args=[instance.id], eta=now + delay)

