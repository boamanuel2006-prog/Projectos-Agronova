# AgroNova — Fase 14: Gateways reais e roteamento internacional

## Objetivo
Preparar o módulo de pagamentos para operar com provedores reais sem acoplar o marketplace a um único gateway.

## Providers incluídos
- `bitpay_ao`: Angola — Multicaixa Express e Referência Multicaixa. Sandbox por defeito.
- `gpaygo_ao`: Angola — Referência/Multicaixa Express, com payload configurável conforme onboarding da conta.
- `mercadopago_br`: Brasil — Pix via Payments API; exige Access Token de uma conta Mercado Pago Brasil.
- `mollie`: Portugal/EEA — checkout hospedado; útil para EUR e métodos como MB WAY/Multibanco conforme elegibilidade da conta.
- `stripe`: Portugal/Brasil e outros países suportados pela Stripe; não usar como merchant-of-record em Angola sem estrutura societária/conta elegível.
- `mock`: desenvolvimento e testes.

## Segurança
- Nenhum segredo fica no mobile/web.
- Chaves somente no backend/secret manager.
- Idempotency-Key por operação financeira.
- Webhooks deduplicados no banco.
- Assinaturas verificadas quando o provider fornece mecanismo de assinatura.
- Pagamentos somente são considerados confirmados após estado de sucesso do provider.

## Configuração
Copiar as variáveis de ambiente do `.env.example` e preencher apenas as credenciais do provider realmente contratado.

## Estado
Os adapters estão implementados como integração backend. A ativação em produção depende de onboarding/KYC, credenciais, configuração de webhook e homologação de cada provedor.
