# AgroNova — Fase 26: Staging / Deployment E2E

## Objetivo
Levar a Fase 25 para um ambiente de staging reproduzível, com PostgreSQL, Redis, Django/Daphne, Celery e Web separados.

## Executar
```bash
cd infra
docker compose -f docker-compose.staging.yml up --build -d
../infra/scripts/staging-smoke.sh
```

## Validações
- `/health/` verifica disponibilidade da API.
- `/readiness/` verifica PostgreSQL e Redis.
- O WebSocket usa JWT no header `Authorization: Bearer` ou query string `?token=`.
- Celery usa `config.celery:app`.
- Web e API ficam separados no staging para facilitar diagnóstico.

## E2E mínimo
1. Criar utilizador.
2. Obter JWT.
3. Criar/publicar anúncio.
4. Adicionar ao carrinho.
5. Fazer checkout.
6. Confirmar redução de stock.
7. Criar pagamento Mock e confirmar webhook.
8. Confirmar notificação.
9. Abrir WebSocket autenticado.
10. Testar consulta/admin/analytics.

## Limitação desta execução
O ambiente de execução usado para preparar esta fase não possui Docker daemon nem acesso de rede para instalar dependências Python/Node. Portanto, o compose e os scripts foram preparados e auditados estaticamente, mas a execução E2E real deve ser feita numa máquina/CI com Docker e acesso às imagens/dependências.

## Produção
Antes de produção: substituir secrets, configurar TLS, domínio, CORS, backups, provider de pagamentos real, observabilidade e políticas de retenção.
