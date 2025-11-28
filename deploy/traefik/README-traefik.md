# Traefik TLS Deployment

## Prerequisites
- DNS A/AAAA record pointing your domain to the server IP
- Environment variables:
  - `TRAEFIK_EMAIL` — email for Let’s Encrypt
  - `TRAEFIK_DOMAIN` — your domain (e.g., `console.example.com`)

## First-Time Setup
```bash
cd deploy/traefik
mkdir -p acme
touch acme/acme.json
chmod 600 acme/acme.json
TRAEFIK_EMAIL=you@example.com TRAEFIK_DOMAIN=console.example.com \
  docker compose -f docker-compose.traefik.yml up -d
```

## Routing
- `https://<domain>/` → frontend (Nginx)
- `https://<domain>/api/...` → backend (FastAPI)
- HTTP (`:80`) requests are redirected to HTTPS (`:443`)

## Notes
- Backend reads env from `backend/.env`; adjust `LLM_BASE_URL` if your LLM is remote.
- Certificates are stored in `acme/acme.json` (mounted as `/letsencrypt/acme.json`).
- Traefik dashboard is enabled but not exposed; you can add a secure router for it if needed.

