from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ConsultationService, AvailabilitySlot, ConsultationRequest, ConsultationPayment, ConsultationReview
from .serializers import ServiceSerializer, SlotSerializer, ConsultationRequestSerializer, PaymentSerializer, ReviewSerializer
from .services import create_request, transition, create_payment, confirm_payment, create_review

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class=ServiceSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        qs=ConsultationService.objects.filter(status='PUBLISHED').select_related('consultant','consultant__profile')
        if self.request.user.is_authenticated and self.request.query_params.get('mine')=='1': qs=ConsultationService.objects.filter(consultant=self.request.user)
        return qs
    def perform_create(self,serializer):
        if not hasattr(self.request.user,'profile') or self.request.user.profile.role!='CONSULTANT': from rest_framework.exceptions import PermissionDenied; raise PermissionDenied('Apenas consultores podem criar serviços.')
        serializer.save(consultant=self.request.user)
    @action(detail=True,methods=['post'])
    def publish(self,request,pk=None):
        obj=self.get_object(); self._owner(obj,request); obj.status='PUBLISHED'; obj.save(update_fields=['status','updated_at']); return Response(ServiceSerializer(obj).data)
    @action(detail=True,methods=['post'])
    def pause(self,request,pk=None):
        obj=self.get_object(); self._owner(obj,request); obj.status='PAUSED'; obj.save(update_fields=['status','updated_at']); return Response(ServiceSerializer(obj).data)
    def _owner(self,obj,request):
        if obj.consultant_id!=request.user.id and not request.user.is_staff: from rest_framework.exceptions import PermissionDenied; raise PermissionDenied('Sem permissão.')

class SlotViewSet(viewsets.ModelViewSet):
    serializer_class=SlotSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return AvailabilitySlot.objects.filter(service__consultant=self.request.user)
    def perform_create(self,serializer): serializer.save()
    @action(detail=False,methods=['get'],url_path='service/(?P<service_id>[^/.]+)')
    def by_service(self,request,service_id=None):
        qs=AvailabilitySlot.objects.filter(service_id=service_id,is_booked=False,starts_at__gte=timezone.now()); return Response(SlotSerializer(qs,many=True).data)

class ConsultationRequestViewSet(viewsets.ModelViewSet):
    serializer_class=ConsultationRequestSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return ConsultationRequest.objects.filter(client=self.request.user) | ConsultationRequest.objects.filter(consultant=self.request.user)
    def create(self,request,*args,**kwargs):
        from .models import ConsultationService, AvailabilitySlot
        service=ConsultationService.objects.get(pk=request.data['service_id']); slot=AvailabilitySlot.objects.filter(pk=request.data.get('slot_id')).first() if request.data.get('slot_id') else None
        obj=create_request(service=service,client=request.user,slot=slot,requested_starts_at=request.data.get('requested_starts_at'),notes=request.data.get('notes',''))
        return Response(self.get_serializer(obj).data,status=201)
    @action(detail=True,methods=['post'])
    def accept(self,request,pk=None): return self._transition(request,pk,'ACCEPTED')
    @action(detail=True,methods=['post'])
    def reject(self,request,pk=None): return self._transition(request,pk,'REJECTED')
    @action(detail=True,methods=['post'])
    def request_payment(self,request,pk=None): return self._transition(request,pk,'AWAITING_PAYMENT')
    @action(detail=True,methods=['post'])
    def schedule(self,request,pk=None): return self._transition(request,pk,'SCHEDULED')
    @action(detail=True,methods=['post'])
    def start(self,request,pk=None): return self._transition(request,pk,'IN_PROGRESS')
    @action(detail=True,methods=['post'])
    def complete(self,request,pk=None): return self._transition(request,pk,'COMPLETED')
    @action(detail=True,methods=['post'])
    def cancel(self,request,pk=None): return self._transition(request,pk,'CANCELLED')
    def _transition(self,request,pk,state): return Response(self.get_serializer(transition(self.get_object(),request.user,state)).data)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=PaymentSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return ConsultationPayment.objects.filter(consultation__client=self.request.user)
    @action(detail=False,methods=['post'])
    def create_intent(self,request):
        from .models import ConsultationRequest
        c=ConsultationRequest.objects.get(pk=request.data['consultation_id']); p,created=create_payment(consultation=c,client=request.user,provider=request.data.get('provider','mock'),idempotency_key=request.headers.get('Idempotency-Key','')); return Response(self.get_serializer(p).data,status=201 if created else 200)
    @action(detail=True,methods=['post'])
    def confirm(self,request,pk=None): return Response(self.get_serializer(confirm_payment(payment=self.get_object())).data)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class=ReviewSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return ConsultationReview.objects.filter(author=self.request.user)
    def perform_create(self,serializer):
        c=ConsultationRequest.objects.get(pk=self.request.data['consultation_id']); obj=create_review(consultation=c,author=self.request.user,rating=int(self.request.data['rating']),comment=self.request.data.get('comment','')); serializer.instance=obj
