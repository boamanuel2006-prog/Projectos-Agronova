# AgroNova — Release checklist

## Backend
- [ ] Production secrets supplied outside Git.
- [ ] `DEBUG=False` and allowed hosts configured.
- [ ] PostgreSQL backups configured and restore tested.
- [ ] Redis persistence/retention reviewed.
- [ ] `python manage.py check --deploy` passes in the target environment.
- [ ] Migrations applied successfully.
- [ ] `/health/` returns 200.

## Web
- [ ] `npm run build` passes.
- [ ] API and WebSocket URLs point to the production origin.
- [ ] HTTPS/TLS is terminated at the gateway or load balancer.
- [ ] SPA routes resolve to `index.html`.

## Mobile
- [ ] Android application ID verified.
- [ ] iOS bundle identifier verified.
- [ ] Push credentials configured in Expo/EAS.
- [ ] Production API URL configured.
- [ ] Deep-link routes tested.
- [ ] Release builds tested on physical devices.

## Operations
- [ ] Error monitoring configured.
- [ ] Logs retained and access controlled.
- [ ] Rate limits reviewed.
- [ ] Payment webhooks tested in staging.
- [ ] Rollback procedure documented.
