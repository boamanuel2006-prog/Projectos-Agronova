# AgroNova — Fase 27: comandos de release e E2E

## 1. Backend + infraestrutura

```bash
docker compose -f infra/docker-compose.staging.yml up -d --build
./infra/scripts/staging-smoke.sh
```

## 2. Testes backend

```bash
docker compose -f infra/docker-compose.staging.yml exec api python manage.py check --deploy
docker compose -f infra/docker-compose.staging.yml exec api python manage.py test
```

## 3. Web

```bash
cd web
npm ci
npm run typecheck
npm run build
```

## 4. Mobile

```bash
cd mobile
npm ci
npx expo-doctor
npm run typecheck
```

## 5. Builds EAS

```bash
npm run build:android
npm run build:ios
```

Os builds EAS exigem credenciais/projeto EAS e não são executados automaticamente no CI normal.

## 6. Fluxo E2E mínimo

1. Criar conta de produtor.
2. Criar anúncio.
3. Publicar anúncio.
4. Criar conta de comprador.
5. Pesquisar anúncio.
6. Adicionar ao carrinho.
7. Fazer checkout.
8. Confirmar pagamento sandbox.
9. Verificar transição do pedido.
10. Verificar notificação persistida.
11. Abrir WebSocket autenticado por JWT.
12. Confirmar evento `notification.created`.
13. Criar/aceitar entrega.
14. Finalizar pedido.
15. Criar avaliação.

## Critério de aprovação

A Fase 27 só pode ser marcada como **PASS** quando os comandos acima forem executados num ambiente com Docker, PostgreSQL, Redis e acesso ao npm/EAS. O código entregue nesta fase não declara esses testes como executados localmente quando o ambiente não os permite.
