from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion, uuid
class Migration(migrations.Migration):
 initial=True; dependencies=[('accounts','0001_initial')]
 operations=[migrations.CreateModel(name='Notification',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('type',models.CharField(max_length=80)),('title',models.CharField(max_length=180)),('message',models.CharField(max_length=500)),('payload',models.JSONField(blank=True,default=dict)),('read_at',models.DateTimeField(blank=True,null=True)),('created_at',models.DateTimeField(auto_now_add=True)),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='notifications',to=settings.AUTH_USER_MODEL))])]
