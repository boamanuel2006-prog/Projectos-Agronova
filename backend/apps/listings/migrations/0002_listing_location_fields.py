from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('listings', '0001_initial')]
    operations = [
        migrations.AddField(model_name='listing', name='province', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='listing', name='municipality', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='listing', name='latitude', field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField(model_name='listing', name='longitude', field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddIndex(model_name='listing', index=models.Index(fields=['province', 'municipality'], name='listings_province_municipality_idx')),
    ]
