from django.contrib import admin
from .models import Conversation, ConversationMember, Message, MessageRead, UserBlock
admin.site.register(Conversation)
admin.site.register(ConversationMember)
admin.site.register(Message)
admin.site.register(MessageRead)
admin.site.register(UserBlock)
