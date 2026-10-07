from django.contrib import admin
from .models import Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=('id','order','author','target','rating','status','created_at')
    list_filter=('rating','status')
    search_fields=('author__email','target__email','comment')
