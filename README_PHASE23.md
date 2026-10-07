# AgroNova — Fase 23: Infraestrutura de Produção + CI/CD

Esta fase prepara a aplicação para um ambiente de produção baseado em Docker.

## Componentes
- Django + Daphne para HTTP/WebSocket.
- PostgreSQL 17.
- Redis 8 com persistência AOF.
- Celery worker.
- Nginx como reverse proxy e gateway WebSocket.
- Volumes persistentes para banco, Redis, media e static.
- Healthchecks de PostgreSQL/Redis.
- Script de backup PostgreSQL.
- GitHub Actions para check, testes e compilação.

## Deploy
1. Copiar `infra/.env.production.example` para `.env.production` e preencher secrets reais.
2. Ajustar domínio, CORS e parâmetros de segurança.
3. Executar `docker compose -f infra/docker-compose.production.yml up -d --build`.
4. Configurar TLS/HTTPS no proxy ou balanceador externo. `SECURE_SSL_REDIRECT=1` só deve ser ativado quando o encaminhamento HTTPS estiver corretamente configurado.

## Limitações
- Não contém secrets reais.
- O compose expõe HTTP na porta 80; TLS deve ser adicionado antes de exposição pública.
- Backups precisam de retenção, cópia off-site e teste periódico de restauração.
- CI depende de execução em runner GitHub com acesso às imagens Docker.
