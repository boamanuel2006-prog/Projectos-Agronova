import uuid
from django.conf import settings
from django.db import models
class Report(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    reporter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='reports_made')
    target_type=models.CharField(max_length=30,choices=[('USER','Utilizador'),('LISTING','Anúncio'),('MESSAGE','Mensagem'),('REVIEW','Avaliação')])
    target_id=models.UUIDField()
    reason=models.CharField(max_length=80)
    description=models.TextField(blank=True,max_length=2000)
    status=models.CharField(max_length=20,default='OPEN',choices=[('OPEN','Aberto'),('REVIEWING','Em análise'),('RESOLVED','Resolvido'),('REJECTED','Rejeitado')])
    resolution=models.TextField(blank=True)
    resolved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='moderation_resolutions')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']; indexes=[models.Index(fields=['status','created_at'])]
