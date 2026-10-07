from django.urls import path
from .views import WalletView, LedgerList, SettlementList, PayoutListCreate
urlpatterns=[path('wallet/',WalletView.as_view()),path('ledger/',LedgerList.as_view()),path('settlements/',SettlementList.as_view()),path('payouts/',PayoutListCreate.as_view())]
