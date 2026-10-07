# AgroNova — Fase 21: IA e automação do marketplace

## Objetivo
Adicionar uma camada de inteligência aplicada ao marketplace sem depender de um provedor externo de IA para o funcionamento básico.

## Implementado
- Recomendações híbridas por regras: categoria, favoritos, localização e sinais de disponibilidade.
- Estimativa de preço baseada em anúncios comparáveis publicados.
- Sinalização de risco/qualidade de anúncios para revisão humana.
- Assistente textual básico com classificação de intenção para compras, vendas, preços e consultoria.
- APIs versionadas em `/api/v1/ai/`.

## Endpoints
- `GET /api/v1/ai/recommendations/`
- `POST /api/v1/ai/price-estimate/`
- `GET /api/v1/ai/listings/{id}/risk/`
- `POST /api/v1/ai/assistant/`

## Limitações importantes
Esta fase implementa uma base determinística e explicável. A estimativa de preço não representa preço oficial de mercado e requer amostra suficiente. As recomendações não são machine learning treinado. A sinalização de risco é um filtro auxiliar e não substitui moderação humana.

## Validação
`python -m compileall backend` deve ser executado no ambiente com Python disponível. O sistema completo ainda depende de Django/PostgreSQL/Redis e dos pacotes frontend instalados.
