from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, ConversationMember, Message, MessageRead, UserBlock
from .serializers import ConversationSerializer, CreateConversationSerializer, MessageSerializer, BlockSerializer
from apps.orders.models import Order

User = get_user_model()

def blocked(a, b):
    return UserBlock.objects.filter(Q(blocker=a, blocked=b) | Q(blocker=b, blocked=a)).exists()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','patch','head','options']

    def get_queryset(self):
        return Conversation.objects.filter(members__user=self.request.user).prefetch_related('members__user','messages').distinct()

    def create(self, request, *args, **kwargs):
        ser = CreateConversationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target = None
        order = None
        if ser.validated_data.get('order_id'):
            order = get_object_or_404(Order, pk=ser.validated_data['order_id'])
            if request.user not in [order.buyer, order.seller]:
                raise PermissionDenied('Apenas comprador e vendedor podem abrir a conversa do pedido.')
            target = order.seller if request.user == order.buyer else order.buyer
            existing = Conversation.objects.filter(order=order).first()
            if existing:
                return Response(ConversationSerializer(existing, context={'request':request}).data)
        elif ser.validated_data.get('user_id'):
            target = get_object_or_404(User, pk=ser.validated_data['user_id'])
            if target == request.user: raise ValidationError('Não pode iniciar uma conversa consigo próprio.')
            if blocked(request.user, target): raise PermissionDenied('A comunicação entre estes utilizadores está bloqueada.')
            existing = Conversation.objects.filter(order__isnull=True, members=request.user).filter(members=target).first()
            if existing:
                return Response(ConversationSerializer(existing, context={'request':request}).data)
        else:
            raise ValidationError('Informe user_id ou order_id.')
        if blocked(request.user, target): raise PermissionDenied('A comunicação entre estes utilizadores está bloqueada.')
        with transaction.atomic():
            conv = Conversation.objects.create(order=order, title=ser.validated_data.get('title',''))
            ConversationMember.objects.bulk_create([ConversationMember(conversation=conv,user=request.user), ConversationMember(conversation=conv,user=target)])
        return Response(ConversationSerializer(conv, context={'request':request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def messages(self, request, pk=None):
        conv = self.get_object()
        member = conv.members.filter(user=request.user).first()
        if not member: raise PermissionDenied()
        serializer = MessageSerializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        target_users = list(conv.members.exclude(user=request.user).values_list('user_id', flat=True))
        if any(UserBlock.objects.filter(Q(blocker=request.user, blocked_id=u)|Q(blocker_id=u, blocked=request.user)).exists() for u in target_users):
            raise PermissionDenied('Não é possível enviar mensagens nesta conversa.')
        msg = serializer.save(conversation=conv, sender=request.user)
        conv.updated_at = timezone.now(); conv.save(update_fields=['updated_at'])
        return Response(MessageSerializer(msg, context={'request':request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages_list(self, request, pk=None):
        conv = self.get_object()
        return Response(MessageSerializer(conv.messages.filter(deleted_at__isnull=True).select_related('sender'), many=True, context={'request':request}).data)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        conv = self.get_object()
        member = conv.members.get(user=request.user)
        member.last_read_at = timezone.now(); member.save(update_fields=['last_read_at'])
        conv.messages.exclude(sender=request.user).filter(deleted_at__isnull=True).values_list('id', flat=True)
        return Response({'status':'ok','read_at':member.last_read_at})

    @action(detail=True, methods=['post'])
    def mute(self, request, pk=None):
        member = self.get_object().members.get(user=request.user)
        member.muted = not member.muted; member.save(update_fields=['muted'])
        return Response({'muted': member.muted})

class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','delete','head','options']
    def get_queryset(self): return UserBlock.objects.filter(blocker=self.request.user).select_related('blocked')
    def perform_create(self, serializer):
        target = serializer.validated_data['blocked']
        if target == self.request.user: raise ValidationError('Não pode bloquear a própria conta.')
        serializer.save(blocker=self.request.user)
