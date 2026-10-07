from django.urls import path
from .views import CartViewSet

view = CartViewSet.as_view({'get': 'list'})
add = CartViewSet.as_view({'post': 'add'})
update = CartViewSet.as_view({'patch': 'update_item'})
remove = CartViewSet.as_view({'delete': 'remove'})
checkout = CartViewSet.as_view({'post': 'checkout'})

urlpatterns = [
    path('', view, name='cart'),
    path('items/', add, name='cart-add'),
    path('items/<uuid:item_id>/', update, name='cart-update'),
    path('items/<uuid:item_id>/remove/', remove, name='cart-remove'),
    path('checkout/', checkout, name='cart-checkout'),
]
