from django.contrib import admin
from .models import Report
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('id','target_type','reason','status','reporter','created_at')
    list_filter=('target_type','status','reason')
    search_fields=('reporter__email','description','resolution')
