from decimal import Decimal
from django.db.models import Avg, Count
from apps.listings.models import Listing


def recommend_listings(user, limit=12, category_id=None, province=None):
    qs = Listing.objects.filter(status=Listing.Status.PUBLISHED).select_related('category', 'seller')
    if category_id:
        qs = qs.filter(category_id=category_id)
    if province:
        qs = qs.filter(province__iexact=province)
    candidates = list(qs[:300])
    favorite_categories = set()
    if user and user.is_authenticated:
        favorite_categories = set(
            user.favorites.values_list('listing__category_id', flat=True)[:50]
        )
    scored = []
    for item in candidates:
        score = 0.0
        reasons = []
        if item.category_id in favorite_categories:
            score += 45
            reasons.append('categoria semelhante aos seus favoritos')
        if province and item.province.lower() == province.lower():
            score += 25
            reasons.append('mesma província')
        score += min(float(item.quantity), 1000.0) / 1000.0 * 5
        age_bonus = max(0, 10 - (item.id % 10))
        score += age_bonus
        if not reasons:
            reasons.append('relevância geral e disponibilidade')
        scored.append((score, item, reasons))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {'listing': item, 'score': round(score, 2), 'reasons': reasons}
        for score, item, reasons in scored[:limit]
    ]


def estimate_price(listing=None, category_id=None, province=None, unit=None, currency='AOA'):
    qs = Listing.objects.filter(status=Listing.Status.PUBLISHED, currency=currency)
    if listing:
        category_id = listing.category_id
        province = listing.province or province
        unit = listing.unit or unit
    if category_id:
        qs = qs.filter(category_id=category_id)
    if province:
        qs = qs.filter(province__iexact=province)
    if unit:
        qs = qs.filter(unit__iexact=unit)
    stats = qs.aggregate(avg=Avg('price'), count=Count('id'))
    avg = stats['avg']
    if avg is None:
        return {'currency': currency, 'sample_size': 0, 'estimated_price': None, 'low': None, 'high': None, 'confidence': 'insufficient_data'}
    avg = Decimal(avg)
    return {
        'currency': currency,
        'sample_size': stats['count'],
        'estimated_price': round(avg, 2),
        'low': round(avg * Decimal('0.85'), 2),
        'high': round(avg * Decimal('1.15'), 2),
        'confidence': 'medium' if stats['count'] >= 10 else 'low',
        'method': 'média de anúncios publicados comparáveis; não é avaliação oficial de mercado',
    }


def detect_listing_risk(listing):
    flags = []
    if listing.price <= 0:
        flags.append(('INVALID_PRICE', 'Preço inválido.'))
    if listing.quantity <= 0:
        flags.append(('INVALID_QUANTITY', 'Quantidade inválida.'))
    if not listing.description or len(listing.description.strip()) < 20:
        flags.append(('THIN_DESCRIPTION', 'Descrição muito curta.'))
    if not listing.province:
        flags.append(('MISSING_LOCATION', 'Localização provincial ausente.'))
    image_count = listing.images.count()
    if image_count == 0:
        flags.append(('NO_IMAGE', 'Anúncio sem imagem.'))
    return {
        'risk_level': 'high' if any(x[0] == 'INVALID_PRICE' for x in flags) else ('medium' if flags else 'low'),
        'flags': [{'code': code, 'message': msg} for code, msg in flags],
        'human_review_required': bool(flags),
    }


def assistant_answer(message):
    text = (message or '').strip().lower()
    if not text:
        return {'answer': 'Escreva uma pergunta sobre produtos, compras, vendas ou consultoria agrícola.', 'intent': 'empty'}
    intents = [
        (('preço', 'preco', 'valor'), 'price', 'Posso estimar o preço com base em anúncios comparáveis do marketplace.'),
        (('comprar', 'compra', 'pedido', 'encomenda'), 'purchase', 'Para comprar, pesquise o produto, confira quantidade, localização e vendedor e depois adicione ao carrinho.'),
        (('vender', 'venda', 'anúncio', 'anuncio'), 'sell', 'Para vender, publique título, descrição, preço, unidade, quantidade, localização e imagens reais do produto.'),
        (('consultoria', 'agronomia', 'veterinária', 'veterinaria'), 'consulting', 'A área de consultoria permite procurar serviços especializados e solicitar um horário disponível.'),
    ]
    for words, intent, answer in intents:
        if any(w in text for w in words):
            return {'answer': answer, 'intent': intent}
    return {'answer': 'Posso ajudar a pesquisar produtos, estimar preços, preparar anúncios e encontrar serviços de consultoria. Para recomendações específicas, informe produto e localização.', 'intent': 'general'}
