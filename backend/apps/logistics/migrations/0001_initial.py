from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='TransporterProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=150)),
                ('license_number', models.CharField(blank=True, max_length=80)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='transporter_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_type', models.CharField(default='truck', max_length=50)),
                ('plate_number', models.CharField(max_length=30)),
                ('capacity_kg', models.DecimalField(decimal_places=2, default=1000, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='logistics.transporterprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('REQUESTED', 'Solicitada'), ('ACCEPTED', 'Aceite'), ('PICKED_UP', 'Recolhida'), ('IN_TRANSIT', 'Em trânsito'), ('DELIVERED', 'Entregue'), ('CANCELLED', 'Cancelada')], default='REQUESTED', max_length=30)),
                ('pickup_address', models.CharField(max_length=255)),
                ('pickup_lat', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('pickup_lon', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('delivery_address', models.CharField(max_length=255)),
                ('delivery_lat', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('delivery_lon', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('tracking_notes', models.TextField(blank=True)),
                ('proof_of_delivery_image', models.ImageField(blank=True, null=True, upload_to='proof_of_delivery/')),
                ('proof_of_delivery_note', models.TextField(blank=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='orders.order')),
                ('transporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deliveries', to='logistics.transporterprofile')),
                ('vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logistics.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=14)),
                ('currency', models.CharField(default='AOA', max_length=3)),
                ('distance_km', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('estimated_hours', models.DecimalField(decimal_places=2, default=24, max_digits=6)),
                ('is_accepted', models.BooleanField(default=False)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delivery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='logistics.delivery')),
                ('transporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='logistics.transporterprofile')),
            ],
        ),
    ]
