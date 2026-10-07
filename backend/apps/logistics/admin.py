from django.contrib import admin
from .models import TransporterProfile, Vehicle, Delivery, DeliveryQuote

for model in [TransporterProfile, Vehicle, Delivery, DeliveryQuote]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
