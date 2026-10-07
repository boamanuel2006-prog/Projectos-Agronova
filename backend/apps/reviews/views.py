from django.db.models import Avg,Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.orders.models import Order
from .models import Review
from .serializers import ReviewSerializer,CreateReviewSerializer

class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=ReviewSerializer
    permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        qs=Review.objects.filter(status='PUBLISHED').select_related('author','target','order')
        target=self.request.query_params.get('target')
        if target: qs=qs.filter(target_id=target)
        return qs
    @action(detail=False,methods=['post'],url_path='orders/(?P<order_id>[^/.]+)')
    def create_for_order(self,request,order_id=None):
        order=get_object_or_404(Order.objects.select_related('buyer','seller'),pk=order_id)
        if order.status!='COMPLETED': return Response({'error':{'code':'REVIEW_NOT_ELIGIBLE','message':'O pedido precisa estar concluído.'}},status=400)
        if request.user != order.buyer and request.user != order.seller: return Response({'error':{'code':'FORBIDDEN','message':'Apenas participantes do pedido podem avaliar.'}},status=403)
        target=order.seller if request.user==order.buyer else order.buyer
        if Review.objects.filter(order=order,author=request.user).exists(): return Response({'error':{'code':'ALREADY_REVIEWED','message':'Este pedido já foi avaliado por este utilizador.'}},status=409)
        data=CreateReviewSerializer(data=request.data); data.is_valid(raise_exception=True)
        review=Review.objects.create(order=order,author=request.user,target=target,**data.validated_data)
        return Response(ReviewSerializer(review).data,status=status.HTTP_201_CREATED)
    @action(detail=False,methods=['get'],url_path='users/(?P<user_id>[^/.]+)/summary')
    def user_summary(self,request,user_id=None):
        qs=Review.objects.filter(target_id=user_id,status='PUBLISHED')
        agg=qs.aggregate(average=Avg('rating'),count=Count('id'))
        return Response({'user_id':user_id,'average_rating':round(float(agg['average']),2) if agg['average'] is not None else None,'review_count':agg['count']})
