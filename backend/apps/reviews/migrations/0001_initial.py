import uuid
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

def dep(): return [('orders','0001_initial'),('accounts','0001_initial')]
class Migration(migrations.Migration):
    initial=True
    dependencies=dep()
    operations=[migrations.CreateModel(name='Review',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('rating',models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1),django.core.validators.MaxValueValidator(5)])),('comment',models.TextField(blank=True,max_length=2000)),('status',models.CharField(choices=[('PUBLISHED','Publicado'),('HIDDEN','Oculto'),('REMOVED','Removido')],default='PUBLISHED',max_length=20)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('author',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='written_reviews',to='accounts.user')),('order',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='reviews',to='orders.order')),('target',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='received_reviews',to='accounts.user'))],options={'ordering':['-created_at'],'indexes':[models.Index(fields=['target','status'],name='reviews_tar_status_idx'),models.Index(fields=['order'],name='reviews_order_idx')],'constraints':[models.UniqueConstraint(fields=('order','author'),name='unique_review_per_order_author')]})]
