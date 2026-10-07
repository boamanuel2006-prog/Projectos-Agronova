from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Farm
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('email', 'phone', 'is_active', 'is_staff', 'is_verified')
    fieldsets = ((None, {'fields': ('email', 'password')}), ('Estado', {'fields': ('is_active','is_staff','is_superuser','is_verified')}), ('Contacto', {'fields': ('phone',)}))
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email','password1','password2')}),)
    search_fields = ('email', 'phone')
admin.site.register(Profile)
admin.site.register(Farm)
