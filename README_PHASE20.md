# AgroNova — Fase 20: Painel Administrativo + Analytics

## Objetivo
Adicionar uma camada administrativa para monitorizar utilizadores, marketplace, pedidos, vendas, consultorias, logística, avaliações e moderação sem expor métricas administrativas a utilizadores comuns.

## Backend
Novo app: `backend/apps/analytics/`

Endpoints protegidos por `IsAdminUser`:
- `GET /api/v1/admin-analytics/dashboard/?days=30`
- `GET /api/v1/admin-analytics/summary/?days=30`
- `GET /api/v1/admin-analytics/timeseries/?days=30`
- `GET /api/v1/admin-analytics/breakdowns/`
- `GET /api/v1/admin-analytics/export.csv?days=30`

### Métricas
- utilizadores totais, verificados, ativos e novos;
- anúncios totais, publicados e novos;
- pedidos, pedidos pagos e concluídos;
- vendas brutas, vendas concluídas e ticket médio;
- solicitações e conclusões de consultoria;
- entregas;
- denúncias abertas;
- média de avaliações;
- séries diárias;
- distribuição por perfil/status/categoria/pagamento/logística.

O parâmetro `days` aceita de 1 a 365 dias.

## Frontend web
Criado `web/src/admin/AdminDashboard.tsx` com:
- KPIs;
- filtro de período;
- atualização manual;
- gráfico simples de pedidos/dia;
- distribuições por estado/perfil;
- exportação CSV;
- acesso visível somente quando a sessão informa `is_staff`.

`UserSerializer` passou a expor `is_staff` como campo somente leitura para o frontend decidir se mostra a entrada administrativa.

## Segurança
O frontend não é a barreira de segurança. Todos os endpoints de analytics usam `IsAdminUser`; um utilizador comum recebe 403 mesmo que tente chamar a API diretamente.

## Validação
- `python -m compileall backend`: OK.
- Build React/TypeScript: não executado porque `node_modules` não está instalado neste ambiente.
- Teste end-to-end com Django/PostgreSQL/Redis: requer ambiente de execução configurado.
