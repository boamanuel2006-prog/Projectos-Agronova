from django.conf import settings
from django.db import models

class TransporterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transporter_profile')
    company_name = models.CharField(max_length=150, blank=True)
    license_number = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name or f"Transportador #{self.id}"

class Vehicle(models.Model):
    transporter = models.ForeignKey(TransporterProfile, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=50, default='truck')
    plate_number = models.CharField(max_length=30)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle_type} ({self.plate_number})"

class Delivery(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Solicitada'
        ACCEPTED = 'ACCEPTED', 'Aceite'
        PICKED_UP = 'PICKED_UP', 'Recolhida'
        IN_TRANSIT = 'IN_TRANSIT', 'Em trânsito'
        DELIVERED = 'DELIVERED', 'Entregue'
        CANCELLED = 'CANCELLED', 'Cancelada'

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='deliveries', null=True, blank=True)
    transporter = models.ForeignKey(TransporterProfile, on_delete=models.SET_NULL, related_name='deliveries', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.REQUESTED)
    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_address = models.CharField(max_length=255)
    delivery_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    tracking_notes = models.TextField(blank=True)
    proof_of_delivery_image = models.ImageField(upload_to='proof_of_delivery/', null=True, blank=True)
    proof_of_delivery_note = models.TextField(blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Entrega #{self.id} ({self.status})"

class DeliveryQuote(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='quotes')
    transporter = models.ForeignKey(TransporterProfile, on_delete=models.CASCADE, related_name='quotes')
    price = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='AOA')
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=24)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cotação #{self.id} - {self.price} {self.currency}"
