# AgroNova — Fase 17

## Tempo real e notificações

Implementado:
- WebSocket por utilizador em `/ws/notifications/`.
- Channels + Redis channel layer.
- Autenticação via `AuthMiddlewareStack`.
- Grupo privado `user_<id>`.
- Eventos em tempo real para alterações de pedidos, pagamentos e entregas.
- Registo de dispositivos push para Android/iOS/Web.
- Endpoint `/api/v1/realtime/devices/`.
- Serviço `publish_user_event()` para publicação de eventos pelo backend.
- Ping/pong para manutenção da ligação.

## Eventos sugeridos

`order.updated`, `payment.updated`, `delivery.updated`, `message.created`, `notification.created`.

O WebSocket não substitui persistência: notificações importantes continuam a ser gravadas no banco e o cliente deve sincronizar o estado após reconexão.

## Dependências

`channels` e `channels-redis` foram adicionados ao backend.

## Nota

A execução end-to-end requer instalação das dependências Python e Redis/PostgreSQL disponíveis no ambiente de desenvolvimento.
