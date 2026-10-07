import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.orders.models import Order

class Review(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name='reviews')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='written_reviews')
    target=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='received_reviews')
    rating=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField(blank=True,max_length=2000)
    status=models.CharField(max_length=20,default='PUBLISHED',choices=[('PUBLISHED','Publicado'),('HIDDEN','Oculto'),('REMOVED','Removido')])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['order','author'],name='unique_review_per_order_author')]
        indexes=[models.Index(fields=['target','status']),models.Index(fields=['order'])]
