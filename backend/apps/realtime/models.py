from django.conf import settings
from django.db import models

class PushDevice(models.Model):
    PLATFORM_CHOICES = (("ANDROID", "Android"), ("IOS", "iOS"), ("WEB", "Web"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_devices")
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
