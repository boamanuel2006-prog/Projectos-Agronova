from django.utils import timezone
from rest_framework import serializers
from .models import Conversation, ConversationMember, Message, MessageRead, UserBlock

class MemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.profile.full_name', read_only=True)
    class Meta:
        model = ConversationMember
        fields = ['user','email','full_name','joined_at','last_read_at','muted']

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.profile.full_name', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','conversation','sender','sender_email','sender_name','message_type','body','attachment','attachment_url','reply_to','created_at','edited_at','deleted_at']
        read_only_fields = ['id','sender','created_at','edited_at','deleted_at','attachment_url']
    def get_attachment_url(self, obj):
        if not obj.attachment: return None
        request = self.context.get('request')
        url = obj.attachment.url
        return request.build_absolute_uri(url) if request else url
    def validate(self, attrs):
        body = (attrs.get('body') or '').strip()
        attachment = attrs.get('attachment')
        if not body and not attachment:
            raise serializers.ValidationError('A mensagem deve conter texto ou anexo.')
        if body:
            attrs['body'] = body
        return attrs

class ConversationSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    class Meta:
        model = Conversation
        fields = ['id','order','title','is_active','created_at','updated_at','members','last_message','unread_count']
        read_only_fields = ['id','created_at','updated_at','members','last_message','unread_count']
    def get_last_message(self, obj):
        msg = obj.messages.filter(deleted_at__isnull=True).select_related('sender').order_by('-created_at').first()
        return MessageSerializer(msg, context=self.context).data if msg else None
    def get_unread_count(self, obj):
        user = self.context['request'].user
        member = obj.members.filter(user=user).first()
        if not member: return 0
        qs = obj.messages.filter(deleted_at__isnull=True).exclude(sender=user)
        if member.last_read_at: qs = qs.filter(created_at__gt=member.last_read_at)
        return qs.count()

class CreateConversationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=False)
    order_id = serializers.UUIDField(required=False)
    title = serializers.CharField(max_length=180, required=False, allow_blank=True)

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBlock
        fields = ['blocked']
