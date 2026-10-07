import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('auth','0012_alter_user_first_name_max_length')]
    operations = [
      migrations.CreateModel(name='User', fields=[
        ('password', models.CharField(max_length=128, verbose_name='password')), ('last_login', models.DateTimeField(blank=True,null=True,verbose_name='last login')),
        ('is_superuser', models.BooleanField(default=False,help_text='Designates that this user has all permissions without explicitly assigning them.',verbose_name='superuser status')),
        ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('email', models.EmailField(max_length=254, unique=True)),
        ('phone', models.CharField(blank=True,max_length=30,null=True,unique=True)), ('is_active', models.BooleanField(default=True)), ('is_staff', models.BooleanField(default=False)),
        ('is_verified', models.BooleanField(default=False)), ('date_joined', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
        ('groups', models.ManyToManyField(blank=True, related_name='accounts_user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
        ('user_permissions', models.ManyToManyField(blank=True, related_name='accounts_user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
      ], options={'abstract':False}),
      migrations.CreateModel(name='Profile', fields=[
        ('id', models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')), ('full_name',models.CharField(max_length=160)),
        ('role',models.CharField(choices=[('FARMER','Produtor'),('BUYER','Comprador'),('COMPANY','Empresa'),('TRANSPORTER','Transportador'),('CONSULTANT','Consultor'),('ADMIN','Administrador')],default='FARMER',max_length=20)),
        ('bio',models.TextField(blank=True)),('photo',models.ImageField(blank=True,null=True,upload_to='profiles/')),('verification_status',models.CharField(default='PENDING',max_length=20)),('city',models.CharField(blank=True,max_length=100)),('province',models.CharField(blank=True,max_length=100)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
        ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='profile',to='accounts.user')),
      ]),
      migrations.CreateModel(name='Farm', fields=[
        ('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('name',models.CharField(max_length=160)),('area_hectares',models.DecimalField(blank=True,decimal_places=2,max_digits=12,null=True)),('province',models.CharField(blank=True,max_length=100)),('municipality',models.CharField(blank=True,max_length=100)),('address',models.CharField(blank=True,max_length=255)),('latitude',models.DecimalField(blank=True,decimal_places=6,max_digits=9,null=True)),('longitude',models.DecimalField(blank=True,decimal_places=6,max_digits=9,null=True)),('production_types',models.JSONField(blank=True,default=list)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='farms',to='accounts.user')),
      ])
    ]
