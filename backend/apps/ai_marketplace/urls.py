from django.urls import path
from .views import RecommendationsView, PriceEstimateView, ListingRiskView, AssistantView
urlpatterns = [
    path('recommendations/', RecommendationsView.as_view()),
    path('price-estimate/', PriceEstimateView.as_view()),
    path('listings/<int:pk>/risk/', ListingRiskView.as_view()),
    path('assistant/', AssistantView.as_view()),
]
