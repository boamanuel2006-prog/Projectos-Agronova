from dataclasses import dataclass
from decimal import Decimal
from typing import Any
import hashlib
import hmac
import time
import uuid
import requests
from django.conf import settings

@dataclass
class PaymentCreation:
    provider_ref: str
    checkout_url: str = ''
    raw_response: dict[str, Any] | None = None

class PaymentProvider:
    name = 'base'
    def create_payment(self, *, payment, return_url: str = '') -> PaymentCreation: raise NotImplementedError
    def verify_webhook(self, *, body: bytes, signature: str) -> bool: raise NotImplementedError
    def parse_webhook(self, payload: dict) -> dict: raise NotImplementedError
    def refund(self, *, payment, amount: Decimal | None = None) -> dict: raise NotImplementedError

def _verify_hmac(body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature: return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def _post(url, *, headers=None, json=None, timeout=20):
    response = requests.post(url, headers=headers or {}, json=json, timeout=timeout)
    try: data = response.json()
    except ValueError: data = {'text': response.text}
    if response.status_code >= 400:
        raise ValueError(f'Provider HTTP {response.status_code}: {data}')
    return data

class MockPaymentProvider(PaymentProvider):
    name='mock'
    def create_payment(self, *, payment, return_url=''):
        ref=f'mock_{payment.id}'; return PaymentCreation(ref, return_url, {'provider':self.name,'reference':ref})
    def verify_webhook(self, *, body, signature): return True if settings.DEBUG and not signature else _verify_hmac(body, signature, getattr(settings,'PAYMENT_WEBHOOK_SECRET',''))
    def parse_webhook(self,payload): return {'event_id':str(payload.get('event_id') or payload.get('id') or ''),'event_type':payload.get('type',''),'provider_ref':payload.get('provider_ref',''),'status':payload.get('status','')}
    def refund(self, *, payment, amount=None): return {'status':'REFUNDED','provider_ref':f'refund_{payment.id}','amount':str(amount or payment.amount)}

class BitPayAOProvider(PaymentProvider):
    """BitPay Angola: Multicaixa Express and Multicaixa Reference."""
    name='bitpay_ao'
    def _base(self): return getattr(settings,'BITPAY_AO_BASE_URL','https://api-sandbox.bitpay.ao/v1').rstrip('/')
    def _headers(self, idem=None):
        h={'Authorization':f"Bearer {settings.BITPAY_AO_SECRET_KEY}",'Content-Type':'application/json'}
        if idem: h['Idempotency-Key']=idem
        return h
    def create_payment(self, *, payment, return_url=''):
        method=getattr(settings,'BITPAY_AO_PAYMENT_METHOD','multicaixa_reference')
        payload={'amount':int(Decimal(payment.amount)),'currency':payment.currency,'payment_method':method,'merchant_reference':str(payment.order_id),'metadata':{'agronova_payment_id':str(payment.id)}}
        mobile=getattr(payment.order.buyer,'phone','')
        if method=='multicaixa_express' and mobile: payload['customer']={'mobile':mobile}
        data=_post(self._base()+'/payment_intents',headers=self._headers(str(payment.idempotency_key)),json=payload)
        return PaymentCreation(str(data.get('id')),data.get('checkout_url','') or data.get('url',''),data)
    def verify_webhook(self, *, body, signature):
        secret=getattr(settings,'BITPAY_AO_WEBHOOK_SECRET','')
        if not secret or not signature: return False
        parts=dict(x.split('=',1) for x in signature.split(',') if '=' in x)
        ts=parts.get('t'); sig=parts.get('v1')
        if not ts or not sig: return False
        try:
            if abs(time.time()-int(ts))>600: return False
        except ValueError: return False
        expected=hmac.new(secret.encode(),f'{ts}.{body.decode()}'.encode(),hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,sig)
    def parse_webhook(self,payload):
        obj=payload.get('data') or payload.get('payment_intent') or payload
        return {'event_id':str(payload.get('id') or payload.get('event_id') or obj.get('id') or ''),'event_type':payload.get('type') or payload.get('event_type',''),'provider_ref':str(obj.get('id') or obj.get('payment_intent') or obj.get('provider_ref') or ''),'status':str(obj.get('status') or payload.get('status') or '')}
    def refund(self, *, payment, amount=None):
        payload={'payment_intent':payment.provider_ref}
        if amount is not None: payload['amount']=int(Decimal(amount))
        data=_post(self._base()+'/refunds',headers=self._headers(f'refund-{payment.id}-{uuid.uuid4()}'),json=payload)
        return data

class GPayGoAOProvider(PaymentProvider):
    """G-Pay Go: REST /api/pay; exact account payload is configurable because merchant onboarding determines fields."""
    name='gpaygo_ao'
    def _base(self): return getattr(settings,'GPAYGO_AO_BASE_URL','https://paypay-gateway.gpaygo.com').rstrip('/')
    def create_payment(self, *, payment, return_url=''):
        payload={'transaction_id':str(payment.id),'amount':str(payment.amount),'currency':payment.currency,'payment_method':getattr(settings,'GPAYGO_AO_PAYMENT_METHOD','reference'),'redirect_url':return_url}
        data=_post(self._base()+'/api/pay',headers={'Authorization':f"Bearer {settings.GPAYGO_AO_API_KEY}",'Content-Type':'application/json'},json=payload)
        return PaymentCreation(str(data.get('transaction_id') or data.get('id') or payment.id),data.get('checkout_url') or data.get('redirect_url') or '',data)
    def verify_webhook(self, *, body, signature): return _verify_hmac(body,signature,getattr(settings,'GPAYGO_AO_WEBHOOK_SECRET',''))
    def parse_webhook(self,payload): return {'event_id':str(payload.get('event_id') or payload.get('id') or payload.get('transaction_id') or ''),'event_type':payload.get('type') or payload.get('event_type',''),'provider_ref':str(payload.get('transaction_id') or payload.get('id') or payload.get('reference') or ''),'status':str(payload.get('status') or '')}
    def refund(self, *, payment, amount=None):
        raise ValueError('Confirme com G-Pay Go o endpoint de estorno habilitado para a conta antes de ativar reembolsos automáticos.')

class MollieProvider(PaymentProvider):
    name='mollie'
    def _headers(self): return {'Authorization':f"Bearer {settings.MOLLIE_API_KEY}",'Content-Type':'application/json'}
    def create_payment(self, *, payment, return_url=''):
        payload={'amount':{'currency':payment.currency,'value':f'{payment.amount:.2f}'},'description':f'AgroNova {payment.order_id}','redirectUrl':return_url,'webhookUrl':getattr(settings,'MOLLIE_WEBHOOK_URL','') or '', 'metadata':{'agronova_payment_id':str(payment.id)}}
        data=_post('https://api.mollie.com/v2/payments',headers=self._headers(),json=payload)
        return PaymentCreation(str(data['id']),((data.get('_links') or {}).get('checkout') or {}).get('href',''),data)
    def verify_webhook(self, *, body, signature): return True  # Mollie webhook is authenticated by querying the payment server-side.
    def parse_webhook(self,payload):
        return {'event_id':str(payload.get('id') or payload.get('event_id') or ''),'event_type':'payment.updated','provider_ref':str(payload.get('id') or ''),'status':str(payload.get('status') or '')}
    def refund(self, *, payment, amount=None): raise ValueError('Implemente o endpoint de refund da Mollie com as credenciais de produção antes de ativar esta operação.')

class MercadoPagoBRProvider(PaymentProvider):
    name='mercadopago_br'
    def create_payment(self, *, payment, return_url=''):
        email=getattr(payment.order.buyer,'email','') or 'buyer@agronova.local'
        payload={'transaction_amount':float(payment.amount),'description':f'AgroNova {payment.order_id}','payment_method_id':getattr(settings,'MERCADOPAGO_PAYMENT_METHOD','pix'),'payer':{'email':email}}
        headers={'Authorization':f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",'Content-Type':'application/json','X-Idempotency-Key':str(payment.idempotency_key)}
        data=_post('https://api.mercadopago.com/v1/payments',headers=headers,json=payload)
        url=data.get('ticket_url','')
        return PaymentCreation(str(data.get('id')),url,data)
    def verify_webhook(self, *, body, signature): return _verify_hmac(body,signature,getattr(settings,'MERCADOPAGO_WEBHOOK_SECRET','')) if signature else True
    def parse_webhook(self,payload):
        return {'event_id':str(payload.get('id') or payload.get('data',{}).get('id') or payload.get('event_id') or ''),'event_type':payload.get('type') or payload.get('action',''),'provider_ref':str(payload.get('data',{}).get('id') or payload.get('data',{}).get('payment_id') or payload.get('payment_id') or payload.get('id') or ''),'status':str(payload.get('status') or payload.get('data',{}).get('status') or '')}
    def refund(self, *, payment, amount=None):
        headers={'Authorization':f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",'Content-Type':'application/json'}
        data={}
        if amount is not None: data['amount']=float(amount)
        return _post(f"https://api.mercadopago.com/v1/payments/{payment.provider_ref}/refunds",headers=headers,json=data)

class StripeProvider(PaymentProvider):
    name='stripe'
    def create_payment(self, *, payment, return_url=''):
        # Stripe is available for merchant accounts in Brazil and Portugal; Angola is not currently listed as a supported merchant country.
        payload={'mode':'payment','success_url':return_url or getattr(settings,'STRIPE_SUCCESS_URL',''),'cancel_url':getattr(settings,'STRIPE_CANCEL_URL',''),'line_items[0][price_data][currency]':payment.currency.lower(),'line_items[0][price_data][product_data][name]':f'AgroNova {payment.order_id}','line_items[0][price_data][unit_amount]':str(int(Decimal(payment.amount)*100)),'line_items[0][quantity]':'1'}
        response=requests.post('https://api.stripe.com/v1/checkout/sessions',auth=(settings.STRIPE_SECRET_KEY,''),data=payload,timeout=20)
        data=response.json()
        if response.status_code>=400: raise ValueError(data)
        return PaymentCreation(str(data['id']),data.get('url',''),data)
    def verify_webhook(self, *, body, signature): return _verify_hmac(body,signature,getattr(settings,'STRIPE_WEBHOOK_SECRET',''))
    def parse_webhook(self,payload):
        obj=payload.get('data',{}).get('object',{})
        return {'event_id':str(payload.get('id','')),'event_type':payload.get('type',''),'provider_ref':str(obj.get('payment_intent') or obj.get('id') or ''),'status':'PAID' if payload.get('type') in {'checkout.session.completed','payment_intent.succeeded'} else ('FAILED' if 'failed' in payload.get('type','') else '')}
    def refund(self, *, payment, amount=None):
        data={}
        if amount is not None: data['amount']=str(int(Decimal(amount)*100))
        response=requests.post('https://api.stripe.com/v1/refunds',auth=(settings.STRIPE_SECRET_KEY,''),data={**data,'payment_intent':payment.provider_ref},timeout=20)
        result=response.json()
        if response.status_code>=400: raise ValueError(result)
        return result

PROVIDERS={'mock':MockPaymentProvider,'bitpay_ao':BitPayAOProvider,'gpaygo_ao':GPayGoAOProvider,'mollie':MollieProvider,'mercadopago_br':MercadoPagoBRProvider,'stripe':StripeProvider}

def get_provider(name: str) -> PaymentProvider:
    cls=PROVIDERS.get(name)
    if not cls: raise ValueError(f'Provider de pagamento não configurado: {name}')
    return cls()
