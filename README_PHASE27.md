# Fase 27 — Release Engineering, Builds e E2E

## Correções desta fase

- Removido `latest` do Web.
- Adicionadas versões explícitas para React, React DOM, Vite, plugin React e TypeScript.
- Adicionados `tsconfig.json` e `vite.config.ts`, que estavam ausentes apesar do script `tsc -b && vite build`.
- Adicionados `typecheck` e build verificável no Web.
- Atualizadas versões patch do Expo SDK 57 e React Native 0.86.
- Adicionados scripts de `expo-doctor`, typecheck e builds EAS Android/iOS.
- CI ampliado para backend, Web e Mobile.
- Criado roteiro E2E de negócio completo.

## Estado de validação deste ambiente

- Backend Python compileall: PASS.
- Detecção de Docker daemon: indisponível.
- Instalação npm/package-lock: não concluída neste ambiente por timeout de rede.
- Web build: NÃO EXECUTADO.
- Mobile build: NÃO EXECUTADO.
- EAS Android: NÃO EXECUTADO.
- EAS iOS: NÃO EXECUTADO.
- E2E real: NÃO EXECUTADO.

## Fontes de versões consultadas

As versões foram conferidas no npm em 25/09/2026. Expo 57.0.24 é o patch atual do SDK 57; React Native 0.86.3 é o patch estável da linha 0.86; `@vitejs/plugin-react` está em 6.1.1; Vite em 8.3.1. O projeto mantém o Expo SDK 57 em vez de migrar para uma versão preview do SDK 58 nesta release.
