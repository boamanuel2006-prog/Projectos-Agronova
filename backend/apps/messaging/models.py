import uuid
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField('orders.Order', null=True, blank=True, on_delete=models.SET_NULL, related_name='conversation')
    title = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at']

class ConversationMember(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    muted = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['conversation', 'user'], name='unique_conversation_member')]

class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'TEXT', 'Texto'
        SYSTEM = 'SYSTEM', 'Sistema'
        IMAGE = 'IMAGE', 'Imagem'
        FILE = 'FILE', 'Ficheiro'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    body = models.TextField(max_length=5000, blank=True)
    attachment = models.FileField(upload_to='messages/%Y/%m/', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','webp','pdf','doc','docx','xls','xlsx'])])
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['conversation', '-created_at'])]

class MessageRead(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['message','user'], name='unique_message_read')]

class UserBlock(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_created')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_received')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['blocker','blocked'], name='unique_user_block')]
