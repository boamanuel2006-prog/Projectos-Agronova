# AgroNova — Auditoria Final de Produção (Fase 25)

Data da auditoria: 2026-09-25

## Resultado

**Estado: Share with caveats / NÃO liberar diretamente para produção.**

A base foi auditada estaticamente e recebeu correções de integração. Sintaxe Python passou em `compileall`. Não foi possível executar a suíte Django, Docker Compose ou builds mobile/web neste ambiente porque o runtime não possui Docker e o backend depende de PostgreSQL/Redis.

## Correções aplicadas

- WebSocket agora usa middleware JWT próprio para `Authorization: Bearer` e `?token=`.
- Endpoint `/readiness/` verifica conectividade com PostgreSQL e retorna 503 quando não está pronto.
- Web deixou de apresentar anúncios fictícios como fallback de produção.
- Botão de detalhe do anúncio passou a usar `/api/v1/cart/items/` para adicionar ao carrinho, removendo referência obsoleta à Fase 10.
- Mobile deixou de apresentar produtos fictícios como fallback.
- Mobile deixou de declarar `expo-router` sem estrutura de rotas correspondente; passou para o entrypoint clássico do Expo.
- Dependências mobile foram fixadas para Expo SDK 57 e versões compatíveis documentadas.
- Configuração do plugin de notificações foi adicionada ao `app.config.js`.

## Verificações realizadas

- Inventário do projeto: 369 arquivos no pacote auditado.
- `python -m compileall backend`: PASS.
- JWT WebSocket: código presente e ligado no ASGI: PASS estático.
- Rotas principais API: presentes no `config/urls.py`.
- CI/CD: workflow presente.
- Docker/Compose: arquivos presentes, mas build/runtime NÃO VERIFICADOS neste ambiente.
- Web build: NÃO VERIFICADO neste ambiente.
- Android/iOS/EAS build: NÃO VERIFICADO neste ambiente.
- Testes Django completos: NÃO EXECUTADOS por ausência de PostgreSQL/Django runtime configurado.

## Bloqueadores antes do lançamento

1. Executar `python manage.py check --deploy` e `python manage.py test` em ambiente com PostgreSQL/Redis.
2. Executar `npm ci && npm run build` no Web e `npm ci && npx expo-doctor` + EAS development/preview build no Mobile.
3. Confirmar credenciais reais e webhooks de cada PSP antes de habilitar pagamentos reais.
4. Configurar TLS no edge/load balancer e garantir que o gateway Nginx não seja exposto sem HTTPS em produção.
5. Configurar segredos fora do repositório (`DJANGO_SECRET_KEY`, passwords, PSP keys, webhook secrets).
6. Validar push notifications em dispositivos físicos; Expo informa que push remoto no Android não funciona no Expo Go a partir do SDK 53 e requer development build.
7. Criar testes de integração com PostgreSQL/Redis para checkout, pagamentos idempotentes, logística, consultoria, notificações e WebSocket.

## Critério de liberação

Só considerar `production-ready` após todos os itens acima passarem em CI ou ambiente de staging equivalente e após teste E2E dos fluxos críticos: cadastro → anúncio → carrinho → checkout → pagamento → logística → conclusão → avaliação.
