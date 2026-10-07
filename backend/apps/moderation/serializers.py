from rest_framework import serializers
from .models import Report
class ReportSerializer(serializers.ModelSerializer):
    reporter_email=serializers.EmailField(source='reporter.email',read_only=True)
    class Meta:
        model=Report; fields=['id','reporter','reporter_email','target_type','target_id','reason','description','status','resolution','created_at','updated_at']
        read_only_fields=['id','reporter','reporter_email','status','resolution','created_at','updated_at']
class ModerationUpdateSerializer(serializers.Serializer):
    status=serializers.ChoiceField(choices=['OPEN','REVIEWING','RESOLVED','REJECTED'])
    resolution=serializers.CharField(required=False,allow_blank=True,max_length=2000)
