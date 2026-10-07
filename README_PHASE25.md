# Fase 25 — Auditoria Final e Integração

Esta fase audita a base acumulada, corrige inconsistências de produção e adiciona testes para os fluxos críticos.

## Testes adicionados

- health/readiness
- autenticação JWT
- adicionar anúncio publicado ao carrinho
- checkout e baixa transacional de stock
- bloqueio de compra do próprio anúncio

## Execução recomendada

```bash
cd backend
python manage.py check --deploy
python manage.py test
```

No ambiente atual estes testes não foram executados porque PostgreSQL/Redis/Docker não estão disponíveis; o arquivo foi validado por compilação Python.
