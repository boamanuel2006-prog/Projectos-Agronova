# AgroNova — Fase 18: Push + integração frontend

## Implementado
- WebSocket autenticado por JWT para React Native e Web.
- Token aceito no header `Authorization: Bearer` ou query `?token=`.
- Registo de tokens Expo Push em `/api/v1/realtime/devices/`.
- `expo-notifications` + `expo-device` no mobile.
- Contagem de não lidas e `read_all` no backend.
- Centro de notificações básico no Web.
- Eventos em tempo real `notification.created`.
- Helper backend `create_and_publish_notification()` para persistir + publicar evento.
- Reconexão/limpeza de WebSocket ao mudar sessão.
- Deep-linking/ações específicas ainda devem ser ligados por tipo de notificação na próxima etapa.

## Segurança
O JWT deve ser transportado preferencialmente por header em clientes que suportem handshake customizado. O parâmetro `?token=` foi incluído para compatibilidade com WebSocket no React Native, mas URLs podem aparecer em logs; usar TLS (`wss`) em produção e evitar logging de query strings.

## Validação
Foi feita validação estática/compilação de Python. A execução end-to-end depende de Django, PostgreSQL, Redis e dependências Node/Expo instaladas.
