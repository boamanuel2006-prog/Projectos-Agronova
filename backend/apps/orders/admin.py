from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Payment

for model in [Order, OrderItem, OrderStatusHistory, Payment]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
