from django.contrib import admin
from .models import Wallet, LedgerEntry, Settlement, PayoutRequest
admin.site.register([Wallet,LedgerEntry,Settlement,PayoutRequest])
