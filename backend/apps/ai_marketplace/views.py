from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.listings.models import Listing
from .serializers import RecommendationSerializer, PriceEstimateInputSerializer
from .services import recommend_listings, estimate_price, detect_listing_risk, assistant_answer

class RecommendationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = recommend_listings(request.user, int(request.query_params.get('limit', 12)), request.query_params.get('category_id'), request.query_params.get('province'))
        rows = []
        for x in data:
            payload = RecommendationSerializer(x['listing']).data
            payload.update(score=x['score'], reasons=x['reasons'])
            rows.append(payload)
        return Response({'items': rows, 'algorithm': 'hybrid-rules-v1'})

class PriceEstimateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        s = PriceEstimateInputSerializer(data=request.data); s.is_valid(raise_exception=True)
        data = s.validated_data
        listing = Listing.objects.get(pk=data['listing_id']) if data.get('listing_id') else None
        return Response(estimate_price(listing, **{k:v for k,v in data.items() if k != 'listing_id'}))

class ListingRiskView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        if listing.seller_id != request.user.id and not request.user.is_staff:
            return Response({'detail':'Sem permissão.'}, status=403)
        return Response(detect_listing_risk(listing))

class AssistantView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        return Response(assistant_answer(request.data.get('message')))
