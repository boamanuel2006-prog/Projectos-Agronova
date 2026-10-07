# AgroNova — Fase 22: QA, Segurança, Testes e Anti-Abuso

## Objetivo
Preparar a base para validação automatizada e endurecimento de segurança antes da fase de deployment.

## Implementado
- Throttling global DRF para utilizadores anónimos e autenticados.
- Limites configuráveis por ambiente: `API_ANON_RATE` e `API_USER_RATE`.
- Middleware de headers de segurança: `nosniff`, `DENY`, Referrer-Policy, Permissions-Policy e HSTS em produção.
- Hardening Django em `DEBUG=0`: HTTPS redirect, cookies seguros, HSTS e frame protection.
- Testes de segurança da API e isolamento administrativo.
- Preservação de segredos exclusivamente por variáveis de ambiente.

## Testes adicionados
`backend/apps/accounts/tests.py`
`backend/apps/listings/tests.py`
`backend/apps/common/tests.py`

## Comandos recomendados
```bash
python manage.py test
python manage.py check --deploy
python manage.py check
```

## Limitações desta fase
O ambiente de construção não possui necessariamente PostgreSQL/Redis/Django instalados e configurados para execução end-to-end. Portanto, compilação sintática não equivale a uma execução completa de integração.

Antes de produção, executar testes com PostgreSQL e Redis reais, testes de carga e testes de segurança externos.
