# AgroNova — Fase 19: Marketplace de Consultoria

Esta fase adiciona o módulo de consultoria multidisciplinar ao marketplace.

## Incluído
- Serviços de Agronomia, Veterinária, Biologia/Ambiente e Tecnologia.
- Perfil do consultor via `Profile.role=CONSULTANT`.
- Publicação/pausa de serviços.
- Agenda por slots com proteção contra dupla reserva.
- Solicitações de consultoria e máquina de estados.
- Fluxo: solicitação → aceite → pagamento → agendamento → atendimento → conclusão.
- Payment Intent específico de consultoria com idempotência e provider abstraction inicial (`mock`).
- Notificações persistentes + WebSocket para pedidos e mudanças de estado.
- Avaliação 1–5 após conclusão.
- API REST em `/api/v1/consultations/`.

## Endpoints principais
- `GET/POST /services/`
- `POST /services/{id}/publish/`
- `POST /services/{id}/pause/`
- `GET/POST /slots/`
- `GET /slots/service/{service_id}/`
- `GET/POST /requests/`
- `POST /requests/{id}/accept/`
- `POST /requests/{id}/reject/`
- `POST /requests/{id}/request_payment/`
- `POST /requests/{id}/schedule/`
- `POST /requests/{id}/start/`
- `POST /requests/{id}/complete/`
- `POST /requests/{id}/cancel/`
- `POST /payments/create_intent/` com `Idempotency-Key`
- `POST /payments/{id}/confirm/`
- `POST /reviews/`

## Observações
O provider de pagamento da consultoria está preparado para ser ligado aos gateways reais já existentes no projeto. A confirmação atual é de desenvolvimento (`mock`); não há credenciais reais no código.

## Validação
Foi feita compilação sintática dos módulos Python. A execução end-to-end depende de Django/PostgreSQL/Redis e das variáveis de ambiente do projeto.
