# AgroNova — Fase 15: Marketplace Financeiro

## Objetivo
Adicionar uma camada financeira interna para contabilizar vendas, comissão da plataforma, saldo do vendedor, liquidações e pedidos de levantamento, sem armazenar dinheiro real fora dos provedores de pagamento licenciados.

## Implementado
- Wallet por vendedor.
- Ledger imutável de movimentos financeiros.
- Settlement por pedido.
- Comissão configurável (`MARKETPLACE_COMMISSION_RATE`, default 5%).
- Valor bruto, taxas, comissão e líquido separados.
- Idempotência em pedidos de levantamento.
- PayoutRequest para preparar repasses para banco/mobile money/provedor.
- Endpoints de carteira, ledger, settlements e payouts.
- Django Admin para operações financeiras.

## Endpoints
- GET `/api/v1/finance/wallet/`
- GET `/api/v1/finance/ledger/`
- GET `/api/v1/finance/settlements/`
- GET/POST `/api/v1/finance/payouts/`

## Regra financeira
Exemplo: venda de 100.000 AOA, comissão de 5% e taxa de 1.000 AOA:
- bruto: 100.000
- comissão: 5.000
- taxas: 1.000
- líquido do vendedor: 94.000 AOA

## Segurança e conformidade
A carteira é um **ledger contábil interno**, não uma licença para o AgroNova custodiar fundos. O dinheiro real deve permanecer no gateway/PSP/banco conforme o modelo aprovado e a legislação aplicável. Antes de produção devem ser definidos KYC/KYB, settlement, chargebacks, refunds, reconciliação e requisitos regulatórios por país.

## Limitação desta fase
O payout ainda é uma solicitação interna; a transferência real para banco/mobile money depende do provider de payout escolhido e da aprovação da conta comercial.
