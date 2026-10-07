from django.contrib import admin
from .models import ConsultationService, AvailabilitySlot, ConsultationRequest, ConsultationPayment, ConsultationReview

for model in [ConsultationService, AvailabilitySlot, ConsultationRequest, ConsultationPayment, ConsultationReview]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
