from django.contrib import admin
from .models import PaymentWebhookEvent, PaymentAttempt
admin.site.register(PaymentWebhookEvent)
admin.site.register(PaymentAttempt)
