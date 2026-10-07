# AgroNova — Fase 16: Logística completa

Implementa a camada logística avançada do marketplace.

## Incluído
- Transportadores e veículos.
- Ciclo da entrega: REQUESTED -> ACCEPTED -> PICKED_UP -> IN_TRANSIT -> DELIVERED.
- Cotação de frete baseada em distância e peso.
- Distância Haversine.
- Expiração e aceitação de cotações.
- Rastreamento por localização com histórico.
- Prova de entrega por imagem e nota.
- Permissões por comprador, vendedor, transportador e administrador.
- Preparação para integração com operadores externos.

## API
- `/api/v1/logistics/transporters/`
- `/api/v1/logistics/vehicles/`
- `/api/v1/logistics/deliveries/`
- `/api/v1/logistics/deliveries/{id}/quote/`
- `/api/v1/logistics/deliveries/{id}/track/`
- `/api/v1/logistics/deliveries/{id}/proof-of-delivery/`
- `/api/v1/logistics/quotes/`
- `/api/v1/logistics/quotes/{id}/accept/`

## Modelo de preço inicial
`frete = taxa_base + (distância_km × preço_km) + (peso_kg × preço_kg)`

Os valores são parâmetros de desenvolvimento e devem ser substituídos por tabelas de tarifas reais antes de produção.

## Próximo passo
Integração com fornecedores logísticos, cálculo de frete por zonas/tipos de veículo, notificações em tempo real e sincronização automática do estado da entrega com o pedido.
