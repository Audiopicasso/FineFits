# FineFits auf dem Raspberry Pi (Produktion)

Anleitung für einen **kostengünstigen Betrieb** mit **OpenAI API**, eigener **Subdomain** und HTTPS.

## Architektur

```
Internet
   │
   ▼
Caddy (HTTPS, Port 443)          ← Let's Encrypt, auf dem Pi installiert
   │
   ▼
nginx Container (127.0.0.1:8080) ← docker-compose.prod.yml
   ├── Frontend (Next.js)
   ├── Backend (FastAPI)
   ├── Worker (KI-Jobs)
   ├── PostgreSQL
   └── Redis
   │
   ▼
OpenAI API (Cloud)               ← nur bei KI-Nutzung Kosten
```

**Was auf dem Pi läuft:** App, Datenbank, Bilder, Hintergrundentfernung (optional).  
**Was in der Cloud läuft:** nur OpenAI (Pay-per-use).

---

## Voraussetzungen

| | Minimum | Empfohlen |
|---|---------|-----------|
| Hardware | Raspberry Pi 4, 4 GB RAM | Pi 5, 8 GB RAM |
| Speicher | 32 GB SD | **USB-SSD** (deutlich stabiler) |
| OS | Raspberry Pi OS 64-bit | gleich |
| Domain | Subdomain mit A-Record auf Pi | z. B. `finefits.example.com` |
| Router | Port 80/443 auf Pi weiterleiten | oder Cloudflare Tunnel |

---

## Kosten (Richtwerte)

| Posten | Kosten |
|--------|--------|
| Strom Pi | ~5–15 €/Monat |
| Domain | ~1 €/Monat (falls nicht vorhanden) |
| OpenAI | variabel — mit **`gpt-4o-mini`** oft **1–5 €/Monat** bei normaler Nutzerin |
| Hosting | **0 €** (alles self-hosted) |

### OpenAI sparsam nutzen

In `.env` (siehe `.env.production.example`):

```env
AI_VISION_MODEL=gpt-4o-mini
AI_TEXT_MODEL=gpt-4o-mini
```

Zusätzlich im [OpenAI Dashboard](https://platform.openai.com/settings/organization/billing/limits):

- **Monatliches Limit** setzen (z. B. 10 €)
- Usage Alerts aktivieren

Typische API-Aufrufe:

- **1× pro hochgeladenem Kleidungsstück** (Bildanalyse)
- **1× pro Outfit-Vorschlag** (Text)

---

## Schritt 1: Pi vorbereiten

```bash
# Docker installieren (offizielle Anleitung für Debian/RPi)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Neu einloggen

# Projekt klonen
git clone <dein-repo> finefits
cd finefits
```

Optional Swap (hilft beim ersten Build):

```bash
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup && sudo dphys-swapfile swapon
```

---

## Schritt 2: Produktions-.env anlegen

```bash
cp .env.production.example .env
nano .env
```

Pflichtfelder:

1. `APP_URL` und `NEXTAUTH_URL` → `https://deine-subdomain.de`
2. `SECRET_KEY`, `NEXTAUTH_SECRET`, `POSTGRES_PASSWORD` → mit `openssl rand -hex 32` erzeugen
3. `AI_API_KEY` → dein OpenAI Key
4. **OIDC** konfigurieren (siehe Schritt 3) — **ohne OIDC kein sicherer Login in Produktion**

---

## Schritt 3: Login (Auth) — Pflicht für Produktion

Dev-Login (`DEBUG=true`) ist **nur für lokale Entwicklung** gedacht. In Produktion brauchst du **OIDC**.

### Empfehlung für 2 Personen (du + Sophia)

**Option A — Pocket ID** (leicht, self-hosted, ideal für Pi)  
- Eigene Subdomain z. B. `auth.deine-domain.de`
- OIDC-Client anlegen, Redirect-URI:
  `https://finefits.deine-domain.de/api/auth/callback/oidc`
- Werte in `.env` eintragen

**Option B — Bestehender Anbieter**  
Google / GitHub / Authentik — alles mit OIDC-Unterstützung funktioniert.

**Option C — Cloudflare Access** (kein OIDC in der App nötig, schützt die ganze Seite)  
Vor den Pi — gut wenn du keinen eigenen Auth-Server willst.

---

## Schritt 4: App starten

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Erster Build auf dem Pi kann **30–60 Minuten** dauern (ARM + rembg-Modell).

Datenbank migrieren:

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

Prüfen:

```bash
curl -s http://127.0.0.1:8080/health
docker compose -f docker-compose.prod.yml ps
```

---

## Schritt 5: HTTPS mit Caddy

```bash
sudo apt install -y caddy
sudo cp deploy/Caddyfile.example /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile   # Domain anpassen
sudo systemctl enable --now caddy
```

DNS: **A-Record** `finefits` → öffentliche IP des Pi (oder DynDNS).

Router: **Port 443 und 80** auf den Pi forwarden.

---

## Schritt 6: Updates & Backup

```bash
cd ~/finefits
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

**Backup** (mindestens):

```bash
# Datenbank
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U wardrobe wardrobe > backup-$(date +%F).sql

# Bilder
docker run --rm -v finefits_uploads_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/uploads-$(date +%F).tar.gz -C /data .
```

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Build bricht ab (Speicher) | Swap erhöhen, `docker system prune`, SSD nutzen |
| Login redirect loop | `NEXTAUTH_URL` muss exakt HTTPS-URL sein |
| KI timeout | `NGINX_AI_TIMEOUT=600`, `AI_TIMEOUT=120` |
| OIDC Fehler | Redirect-URI im IdP prüfen |
| Pi langsam bei BG-Entfernung | Normal — rembg ist CPU-lastig; optional seltener nutzen |

---

## Checkliste vor Go-Live

- [ ] Starke Secrets gesetzt (nicht `change-me-in-production`)
- [ ] `DEBUG` nicht gesetzt oder `false`
- [ ] HTTPS aktiv, HTTP → HTTPS Redirect
- [ ] OIDC Login getestet (Sophia + du)
- [ ] OpenAI Billing-Limit gesetzt
- [ ] Backup-Strategie definiert
- [ ] Erstes Kleidungsstück hochgeladen → KI-Tagging OK
- [ ] Outfit-Vorschlag mit Standort getestet
