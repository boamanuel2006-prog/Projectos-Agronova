from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.listings.models import Listing
from .models import Order
from .serializers import OrderSerializer,CreateOrderSerializer,StatusSerializer
from .services import create_order,transition_order

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return Order.objects.filter(buyer=self.request.user).union(Order.objects.filter(seller=self.request.user))
    def create(self,request,*args,**kwargs):
        data=CreateOrderSerializer(data=request.data); data.is_valid(raise_exception=True)
        try:
            listing=Listing.objects.get(pk=data.validated_data['listing'])
            order=create_order(buyer=request.user,listing=listing,quantity=data.validated_data['quantity'],delivery_address=data.validated_data.get('delivery_address',''),notes=data.validated_data.get('notes',''))
        except (DjangoValidationError, Listing.DoesNotExist) as exc:
            return Response({'error':{'code':'ORDER_INVALID','message':str(exc)}},status=400)
        return Response(OrderSerializer(order,context={'request':request}).data,status=status.HTTP_201_CREATED)
    @action(detail=True,methods=['post'])
    def transition(self,request,pk=None):
        data=StatusSerializer(data=request.data); data.is_valid(raise_exception=True)
        try: order=transition_order(order=self.get_object(),actor=request.user,new_status=data.validated_data['status'])
        except (DjangoValidationError,PermissionError) as exc: return Response({'error':{'code':'INVALID_TRANSITION','message':str(exc)}},status=400)
        return Response(OrderSerializer(order,context={'request':request}).data)
    @action(detail=True,methods=['post'])
    def cancel(self,request,pk=None):
        return self.transition(request,pk)
