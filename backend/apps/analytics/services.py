from datetime import timedelta
from decimal import Decimal
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.accounts.models import User, Profile
from apps.listings.models import Listing
from apps.orders.models import Order
from apps.orders.models import Payment as OrderPayment
from apps.consultations.models import ConsultationRequest, ConsultationService
from apps.logistics.models import Delivery
from apps.moderation.models import Report
from apps.reviews.models import Review


def _money(qs, field='total'):
    return qs.aggregate(value=Sum(field))['value'] or Decimal('0')


def dashboard_summary(days=30):
    days = max(1, min(int(days), 365))
    now = timezone.now()
    since = now - timedelta(days=days)

    orders = Order.objects.filter(created_at__gte=since)
    paid_orders = orders.filter(status__in=['PAID','PROCESSING','READY_FOR_DELIVERY','IN_TRANSIT','DELIVERED','COMPLETED'])
    completed = orders.filter(status='COMPLETED')
    consultations = ConsultationRequest.objects.filter(created_at__gte=since)

    return {
        'period_days': days,
        'generated_at': now.isoformat(),
        'users': User.objects.count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'new_users': User.objects.filter(date_joined__gte=since).count(),
        'listings': Listing.objects.count(),
        'published_listings': Listing.objects.filter(status='PUBLISHED').count(),
        'new_listings': Listing.objects.filter(created_at__gte=since).count(),
        'orders': orders.count(),
        'paid_orders': paid_orders.count(),
        'completed_orders': completed.count(),
        'gross_sales': _money(paid_orders),
        'completed_sales': _money(completed),
        'average_order_value': (paid_orders.aggregate(v=Avg('total'))['v'] or Decimal('0')),
        'consultation_requests': consultations.count(),
        'consultations_completed': consultations.filter(status='COMPLETED').count(),
        'deliveries': Delivery.objects.filter(created_at__gte=since).count(),
        'open_reports': Report.objects.filter(status__in=['OPEN','REVIEWING']).count(),
        'average_review': Review.objects.filter(created_at__gte=since, status='PUBLISHED').aggregate(v=Avg('rating'))['v'] or Decimal('0'),
    }


def timeseries(days=30):
    days = max(1, min(int(days), 365))
    since = timezone.now() - timedelta(days=days)
    dates = {}
    cursor = since.date()
    end = timezone.now().date()
    while cursor <= end:
        dates[str(cursor)] = {'date': str(cursor), 'users': 0, 'listings': 0, 'orders': 0, 'sales': Decimal('0'), 'consultations': 0}
        cursor += timedelta(days=1)

    for row in User.objects.filter(date_joined__gte=since).annotate(day=TruncDate('date_joined')).values('day').annotate(n=Count('id')):
        dates[str(row['day'])]['users'] = row['n']
    for row in Listing.objects.filter(created_at__gte=since).annotate(day=TruncDate('created_at')).values('day').annotate(n=Count('id')):
        dates[str(row['day'])]['listings'] = row['n']
    for row in Order.objects.filter(created_at__gte=since).annotate(day=TruncDate('created_at')).values('day').annotate(n=Count('id'), sales=Sum('total')):
        dates[str(row['day'])]['orders'] = row['n']
        dates[str(row['day'])]['sales'] = row['sales'] or Decimal('0')
    for row in ConsultationRequest.objects.filter(created_at__gte=since).annotate(day=TruncDate('created_at')).values('day').annotate(n=Count('id')):
        dates[str(row['day'])]['consultations'] = row['n']
    return list(dates.values())


def breakdowns(limit=10):
    return {
        'users_by_role': list(Profile.objects.values('role').annotate(count=Count('id')).order_by('-count')),
        'orders_by_status': list(Order.objects.values('status').annotate(count=Count('id')).order_by('-count')),
        'listings_by_status': list(Listing.objects.values('status').annotate(count=Count('id')).order_by('-count')),
        'consultations_by_status': list(ConsultationRequest.objects.values('status').annotate(count=Count('id')).order_by('-count')),
        'top_listing_categories': list(Listing.objects.values('category__name').annotate(count=Count('id')).order_by('-count')[:limit]),
        'payments_by_status': list(OrderPayment.objects.values('status').annotate(count=Count('id'), amount=Sum('amount')).order_by('-count')),
        'deliveries_by_status': list(Delivery.objects.values('status').annotate(count=Count('id')).order_by('-count')),
        'reports_by_status': list(Report.objects.values('status').annotate(count=Count('id')).order_by('-count')),
    }
