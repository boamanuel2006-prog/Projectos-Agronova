# AgroNova — Fase 28: Release Gate e Hardening Final

## Objetivo
Transformar a Fase 27 numa release candidate verificável, com um gate único para impedir a entrega acidental de uma versão estruturalmente incompleta.

## Implementado
- Gate estático automatizado em `RELEASE_GATE.sh`.
- Verificação de arquivos críticos de backend, staging, Web e Mobile.
- `compileall` do backend.
- Validação JSON de manifestos.
- Bloqueio explícito de dependências `latest`.
- Documentação do que pode ser aprovado localmente e do que exige ambiente Docker/Node/EAS.
- Autenticação JWT no WebSocket permanece suportada por header Bearer ou query token.

## Testes que continuam dependentes do ambiente
- PostgreSQL + Redis reais.
- `python manage.py check --deploy`.
- Suite Django completa.
- `npm ci && npm run build` Web.
- `npm ci && npx expo-doctor` Mobile.
- EAS Android/iOS.
- E2E real através do staging.

## Critério de saída
A aplicação só deve ser marcada como **Production Ready** quando os testes acima forem executados com sucesso num ambiente CI/staging real e os segredos, domínio, TLS, storage e gateways forem configurados.
