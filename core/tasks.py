import os

import requests
from celery import shared_task
from django.utils import timezone
from dotenv import load_dotenv

from core.models import Mailing, Client, Message
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
load_dotenv()


@shared_task
def send_messages(mailing_id):
    headers = {
        "Authorization": f"Bearer {os.environ['TOKEN']}"
    }
    try:
        mailing = Mailing.objects.get(id=mailing_id)

        if timezone.now() > mailing.end_datetime:
            logger.info("Mailing end time has passed. Stopping the send_messages task.")
            return

        clients = Client.objects.filter(
            operator_code=mailing.client_filter_operator_code,
            tag=mailing.client_filter_tag
        )

        for client in clients:
            message = Message.objects.create(
                creation_datetime=timezone.now(),
                delivery_status='Sending',
                mailing=mailing,
                client=client
            )

            try:
                response = requests.post(
                    url=f'https://probe.fbrq.cloud/v1/send/{message.id}',
                    json=dict(
                        id=message.id,
                        phone=client.phone_number,
                        text=mailing.message_text,
                    ),
                    headers=headers)
                logger.info(response.json())
                response.raise_for_status()

                message.delivery_status = 'Sent'
                message.save()

            except requests.exceptions.RequestException as e:
                message.delivery_status = 'Failed'
                message.save()
                logger.info(f"Failed to send message to client {client.id}: {str(e)}")

    except Mailing.DoesNotExist:
        logger.ERROR("Mailing does not exist.")