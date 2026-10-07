from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer,ModerationUpdateSerializer
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class=ReportSerializer
    def get_permissions(self): return [permissions.IsAdminUser()] if self.action in ['list','retrieve','update','partial_update','destroy','moderate'] else [permissions.IsAuthenticated()]
    def get_queryset(self):
        qs=Report.objects.select_related('reporter','resolved_by')
        return qs if self.request.user.is_staff else qs.filter(reporter=self.request.user)
    def perform_create(self,serializer): serializer.save(reporter=self.request.user)
    @action(detail=True,methods=['post'])
    def moderate(self,request,pk=None):
        report=self.get_object(); data=ModerationUpdateSerializer(data=request.data); data.is_valid(raise_exception=True)
        report.status=data.validated_data['status']; report.resolution=data.validated_data.get('resolution',''); report.resolved_by=request.user if report.status in ['RESOLVED','REJECTED'] else None; report.save()
        return Response(ReportSerializer(report).data)
