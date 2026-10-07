import uuid
from django.conf import settings
from django.db import models
class Notification(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications')
    type=models.CharField(max_length=80)
    title=models.CharField(max_length=180)
    message=models.CharField(max_length=500)
    payload=models.JSONField(default=dict,blank=True)
    read_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
