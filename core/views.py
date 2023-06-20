from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Client, Mailing, Message
from core.serializers import ClientSerializer, MailingSerializer, MessageSerializer
# Create your views here.


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    @action(detail=True, methods=['get'])
    def common_statistics(self, request, pk=None):
        mailing = self.get_object()
        message_stats = Message.objects.filter(mailing=mailing).values('delivery_status').annotate(count=Count('id'))
        return Response(message_stats)

    @action(detail=True, methods=['GET'])
    def message_statistics(self, request, pk=None):
        mailing = self.get_object()
        messages = mailing.message_set.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
