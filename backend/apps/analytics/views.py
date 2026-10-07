from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
import csv

from .serializers import AnalyticsQuerySerializer
from .services import dashboard_summary, timeseries, breakdowns

class AdminOnlyMixin:
    permission_classes = [IsAdminUser]

class DashboardView(AdminOnlyMixin, APIView):
    def get(self, request):
        s = AnalyticsQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        days = s.validated_data.get('days', 30)
        return Response({'summary': dashboard_summary(days), 'timeseries': timeseries(days), 'breakdowns': breakdowns()})

class SummaryView(AdminOnlyMixin, APIView):
    def get(self, request):
        s = AnalyticsQuerySerializer(data=request.query_params); s.is_valid(raise_exception=True)
        return Response(dashboard_summary(s.validated_data.get('days', 30)))

class TimeseriesView(AdminOnlyMixin, APIView):
    def get(self, request):
        s = AnalyticsQuerySerializer(data=request.query_params); s.is_valid(raise_exception=True)
        return Response(timeseries(s.validated_data.get('days', 30)))

class BreakdownsView(AdminOnlyMixin, APIView):
    def get(self, request):
        return Response(breakdowns())

class DashboardCsvView(AdminOnlyMixin, APIView):
    def get(self, request):
        s = AnalyticsQuerySerializer(data=request.query_params); s.is_valid(raise_exception=True)
        rows = timeseries(s.validated_data.get('days', 30))
        response = StreamingHttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="agronova-analytics.csv"'
        writer = csv.writer(response)
        writer.writerow(['data','novos_utilizadores','novos_anuncios','pedidos','vendas','consultorias'])
        for r in rows:
            writer.writerow([r['date'], r['users'], r['listings'], r['orders'], r['sales'], r['consultations']])
        return response
