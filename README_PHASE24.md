# AgroNova — Fase 24: Release Engineering

Esta fase prepara Web e Mobile para builds de produção e organiza um stack de release único.

## Entregas
- Dockerfile do React Web e configuração SPA.
- Compose de release com gateway, Web, API, PostgreSQL, Redis e Celery.
- Proxy Nginx para `/`, `/api/`, `/ws/`, `/admin/`, `/health/`.
- Configuração EAS para Android/iOS.
- `app.config.js` com variáveis de ambiente de build.
- Checklist de release e operação.

## Validação
A estrutura e os arquivos de configuração foram revisados estaticamente. O build React Native/Expo, build Docker e publicação nas lojas exigem Node/Expo/Docker e credenciais reais no ambiente de release.
