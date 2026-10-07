from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('orders','0001_initial')]
    operations = [
        migrations.CreateModel(name='PaymentAttempt', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('provider', models.CharField(max_length=80)), ('provider_ref', models.CharField(blank=True,max_length=180)),
            ('status', models.CharField(choices=[('CREATED','Criada'),('REDIRECT','Redirecionamento'),('SUCCEEDED','Sucesso'),('FAILED','Falhou'),('EXPIRED','Expirada')],default='CREATED',max_length=20)),
            ('checkout_url', models.URLField(blank=True)), ('raw_response', models.JSONField(default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='attempts',to='orders.payment')),
        ]),
        migrations.CreateModel(name='PaymentWebhookEvent', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('provider', models.CharField(max_length=80)), ('event_id', models.CharField(max_length=180)), ('event_type', models.CharField(max_length=100)),
            ('payload', models.JSONField(default=dict)), ('signature_valid', models.BooleanField(default=False)), ('processed', models.BooleanField(default=False)),
            ('processed_at', models.DateTimeField(blank=True,null=True)), ('error_message', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.AddConstraint(model_name='paymentwebhookevent', constraint=models.UniqueConstraint(fields=['provider','event_id'],name='unique_payment_webhook_event')),
    ]
