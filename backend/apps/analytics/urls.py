from django.urls import path
from .views import DashboardView, SummaryView, TimeseriesView, BreakdownsView, DashboardCsvView

urlpatterns = [
    path('dashboard/', DashboardView.as_view()),
    path('summary/', SummaryView.as_view()),
    path('timeseries/', TimeseriesView.as_view()),
    path('breakdowns/', BreakdownsView.as_view()),
    path('export.csv', DashboardCsvView.as_view()),
]
