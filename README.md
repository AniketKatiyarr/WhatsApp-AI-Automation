# WhatsApp AI Automation Platform (SaaS MVP)

![Screenshot](:\Projects\Auto AI Whatsapp\static\Images\whatsapp_ai_automation.png) 


Production-ready Django + DRF + Celery platform that connects to Meta WhatsApp Cloud API, receives inbound webhooks, processes messages with **FAQ-first + OpenAI**, captures leads, and sends replies asynchronously.

## Tech stack

- **Backend**: Django + Django REST Framework
- **Frontend**: Django Templates + lightweight **React** (no build step)
- **DB**: PostgreSQL
- **Queue**: Redis + Celery
- **AI**: OpenAI API (GPT)
- **WhatsApp**: Meta WhatsApp Cloud API (primary)

## Project structure

- `accounts/` (custom user: business, OpenAI key, WhatsApp token)
- `dashboard/` (landing + dashboard pages)
- `messaging/` (webhook + logs + async send)
- `ai_engine/` (OpenAI prompt + extraction)
- `leads/` (lead capture)
- `faqs/` (FAQ CRUD + matcher)

**Architecture & workflow:** see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (includes diagram PNG).  
**Codebase explanation (folders/files/functions):** see [docs/CODEBASE_GUIDE.md](docs/CODEBASE_GUIDE.md).

## Setup (Windows / PowerShell)

### 1) Start Postgres + Redis

```bash
docker compose up -d
```

### 2) Create and activate venv

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure environment

Copy `.env.example` → `.env` and set:

- `SECRET_KEY`
- `DATABASE_URL` (recommended)
- `REDIS_URL`
- `WHATSAPP_VERIFY_TOKEN`
- `META_APP_SECRET` (recommended for request validation)
- `OPENAI_API_KEY` (optional; can also be set per-user in the UI/admin)

Example Postgres URL:

```text
DATABASE_URL=postgres://postgres:postgres@localhost:5432/whatsapp_ai
```

### 4) Migrate and create admin user

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5) Run Django + Celery

Terminal 1:

```bash
python manage.py runserver
```

Terminal 2:

```bash
celery -A config worker -l info --pool=solo --concurrency=1
```

## App usage

### Web UI

- Landing: `/`
- Signup/Login: `/accounts/signup/`, `/accounts/login/`
- Dashboard: `/dashboard/`
- FAQs: `/faqs/`
- Leads: `/leads/`

### APIs

- `GET /api/messages/`
- `GET /api/leads/`
- `GET|POST /api/faqs/`
- `GET|PUT|PATCH|DELETE /api/faqs/{id}/`
- JWT: `POST /api/auth/token/` and `POST /api/auth/token/refresh/`

### WhatsApp webhook

Single endpoint per Meta + spec: `GET|POST /webhook/`

- **GET** is used by Meta to verify the webhook (hub.challenge).
- **POST** receives inbound messages, stores a `MessageLog`, and triggers Celery processing:
  1. FAQ match (cheap)
  2. Else OpenAI reply + intent + lead extraction
  3. Store `Lead` and `MessageLog.outbound_response`
  4. Send reply async via WhatsApp Cloud API (with retries)

Business routing is done via `metadata.phone_number_id` → `accounts.User.whatsapp_phone_number_id`.

## Configure your Business credentials

For each business user, set:

- `whatsapp_phone_number_id`
- `whatsapp_token` (Cloud API token)
- `api_key` (OpenAI key, optional if `OPENAI_API_KEY` is set globally)

You can set these via Django Admin (`/admin/`) on the User model.

## Testing (webhook simulation)

```bash
python manage.py test
```

The webhook test posts a sample WhatsApp payload and verifies a `MessageLog` is created.

## Static files (CSS) — local vs production

- **Local dev (`DEBUG=1`)**: CSS/JS is served from the `static/` folder via Django’s default storage (no `collectstatic` needed).
- **Production (`DEBUG=0`)**: Run `python manage.py collectstatic` before deploy. WhiteNoise uses hashed filenames from the manifest; without `collectstatic`, styles can 404 and the site looks like plain HTML.

If the landing page looks unstyled:

1. Use **`DEBUG=1`** in `.env` for local dev (or omit `DEBUG` — it defaults to **on** in `settings.py`).
2. Open **`http://127.0.0.1:8000/static/styles.css`** — it should return **200** and CSS text. If 404, restart `runserver` after pulling the latest settings.
3. With **`DEBUG=0`**, run **`python manage.py collectstatic`** and ensure WhiteNoise is enabled (production layout).

## Security notes (production)

- Set `META_APP_SECRET` to enforce `X-Hub-Signature-256` validation on webhook requests.
- Keep tokens out of logs and source control; use `.env` + secret manager.
- For production, encrypt per-business `api_key` and `whatsapp_token` at rest.

