# Codebase Guide (What each file does)

This file explains the project in plain language so you can understand what each folder, file, and important function is responsible for.

## 1) High-level architecture

Request flow for incoming WhatsApp messages:

1. Customer sends message on WhatsApp.
2. Meta sends webhook payload to `POST /webhook/`.
3. Django stores message in `MessageLog` and queues background processing with Celery.
4. Celery worker checks FAQ first; if no match, calls OpenAI.
5. Worker stores reply + optional lead data.
6. Worker sends reply back via Meta Cloud API.
7. Dashboard and APIs show messages/leads/faqs to logged-in business user.

Main URL router: `config/urls.py`

## 2) Project root files

- `manage.py`
  - Django CLI entry point (`runserver`, `migrate`, `test`, etc.).

- `requirements.txt`
  - Python dependencies (Django, DRF, Celery, Redis, OpenAI, WhiteNoise, etc.).

- `docker-compose.yml`
  - Local infrastructure for PostgreSQL + Redis.

- `.env.example`
  - Example environment variables (secrets + runtime config).

- `README.md`
  - Setup, run commands, API endpoints, webhook behavior.

## 3) `config/` (project configuration)

- `config/settings.py`
  - Global Django settings.
  - Reads `.env` values with `django-environ`.
  - Chooses DB (Postgres if `DATABASE_URL`, otherwise SQLite fallback).
  - Registers installed apps (`accounts`, `messaging`, `ai_engine`, etc.).
  - Configures REST auth classes (JWT + session).
  - Configures Celery (`CELERY_BROKER_URL`, result backend).
  - Static files behavior:
    - `DEBUG=1`: Django static storage (dev-friendly).
    - `DEBUG=0`: WhiteNoise manifest storage (production).

- `config/urls.py`
  - Main route table:
    - `/` -> dashboard pages
    - `/accounts/` -> login/signup/logout
    - `/api/...` -> DRF endpoints
    - `/webhook/` -> WhatsApp webhook
  - Adds static/media URL patterns in DEBUG mode.

- `config/celery.py`
  - Creates Celery app and auto-discovers `tasks.py` in apps.

- `config/__init__.py`
  - Exposes celery app so workers bootstrap correctly.

- `config/asgi.py`, `config/wsgi.py`
  - ASGI/WSGI entry points for deployment.

## 4) `accounts/` (auth + business identity)

- `accounts/models.py`
  - `UserManager`
    - `_create_user()`: shared user creation logic.
    - `create_user()`, `create_superuser()`: standard auth manager methods.
  - `User` (custom model)
    - Uses email as login identity.
    - Stores business fields:
      - `business_name`, `business_type`
      - `api_key` (OpenAI key)
      - `whatsapp_token`
      - `whatsapp_phone_number_id`
    - Important because each user = one business in MVP.

- `accounts/forms.py`
  - `SignupForm`: registration validation (`password1` == `password2`).
  - `LoginForm`: email-based login form.

- `accounts/views.py`
  - `signup_view()`: register business user and auto-login.
  - `login_view()`: authenticate session login.
  - `logout_view()`: session logout.

- `accounts/serializers.py`
  - `UserSerializer`: exposes user/business fields for API.

- `accounts/api_views.py`
  - `MeViewSet`:
    - `list()`: returns current authenticated user profile.
    - `partial_update()`: updates current user profile fields.

- `accounts/urls.py`
  - Template auth URLs (`/accounts/signup/`, `/accounts/login/`, `/accounts/logout/`).

- `accounts/api_urls.py`
  - JWT token endpoints:
    - `/api/auth/token/`
    - `/api/auth/token/refresh/`
  - `/api/auth/me/` via `MeViewSet`.

## 5) `dashboard/` (UI pages)

- `dashboard/views.py`
  - `landing()`: public marketing page (`/`).
  - `home()`: authenticated dashboard with message/lead counts.
  - `faqs_page()`: FAQ management page shell.
  - `leads_page()`: leads page shell.

- `dashboard/urls.py`
  - Routes for landing/dashboard/faqs/leads template pages.

## 6) `messaging/` (webhook, message storage, async processing)

- `messaging/models.py`
  - `Conversation`
    - Unique by `(business, phone)`.
    - Tracks `last_message_at`.
  - `MessageLog`
    - Stores inbound text, outbound response, timestamp, status, raw payload.
    - Status values: `received`, `processing`, `responded`, `failed`.

- `messaging/webhook_views.py`
  - `_verify_meta_signature(request)`
    - Validates `X-Hub-Signature-256` using `META_APP_SECRET`.
  - `webhook(request)` (`GET` + `POST`)
    - `GET`: webhook verification (`hub.verify_token` + `hub.challenge`).
    - `POST`: parses payload, maps to business by `phone_number_id`,
      writes `MessageLog`, queues `process_incoming_message.delay(log.id)`.

- `messaging/tasks.py` (core async pipeline)
  - `_recent_context_for_log()`
    - Builds last few chat turns for better AI context.
  - `process_incoming_message(message_log_id)`
    - Marks log processing.
    - Tries FAQ match.
    - If no FAQ: calls OpenAI service.
    - Saves response + lead.
    - Queues `send_whatsapp_reply`.
    - Retries on failure and marks status/error.
  - `send_whatsapp_reply(message_log_id, reply_text)`
    - Sends outbound text via Meta API helper.

- `messaging/whatsapp.py`
  - `send_whatsapp_text_message(...)`
    - Calls Meta Graph API endpoint `/messages`.
    - Uses business token + phone number ID.
    - Raises `WhatsAppSendError` on failure.

- `messaging/serializers.py`
  - `MessageLogSerializer`: response shape for message logs API.

- `messaging/api_views.py`
  - `MessageLogViewSet` (read-only)
    - Returns only current user/business messages.

- `messaging/api_urls.py`
  - Routes `/api/messages/`.

- `messaging/webhook_urls.py`
  - Routes `/webhook/` to webhook handler.

- `messaging/tests.py`
  - Webhook simulation test:
    - Posts sample payload.
    - Asserts `MessageLog` gets created.

## 7) `faqs/` (FAQ CRUD + matching)

- `faqs/models.py`
  - `FAQ` model: `question`, `answer`, business ownership.

- `faqs/matching.py`
  - `best_faq_match(...)`
    - Uses `difflib.SequenceMatcher` score.
    - Returns best FAQ when score >= threshold (default `0.78`).

- `faqs/serializers.py`
  - `FAQSerializer` for API payloads.

- `faqs/api_views.py`
  - `FAQViewSet` (full CRUD)
    - Filters FAQs by logged-in business.
    - Sets `business` during create.

- `faqs/api_urls.py`
  - Routes `/api/faqs/`.

## 8) `leads/` (captured lead data)

- `leads/models.py`
  - `Lead` model:
    - `name`, `phone`, `interest`, `intent`
    - `source_message_id` links origin message.

- `leads/serializers.py`
  - `LeadSerializer` for API output.

- `leads/api_views.py`
  - `LeadViewSet` (read-only)
    - Returns leads only for current business.

- `leads/api_urls.py`
  - Routes `/api/leads/`.

## 9) `ai_engine/` (OpenAI prompt + extraction logic)

- `ai_engine/services.py`
  - `AIResult` dataclass
    - Standard shape: `reply`, `intent`, `lead`.
  - `_client_for_business(business)`
    - Picks API key:
      - `business.api_key` first
      - fallback `settings.OPENAI_API_KEY`.
  - `build_system_prompt(business_type)`
    - System role prompt style by business type.
  - `generate_reply_and_lead(...)`
    - Sends prompt to OpenAI.
    - Requests strict JSON response.
    - Parses and normalizes:
      - intent in `{inquiry, booking, pricing, general}`
      - lead fields `{name, phone, interest}`
    - Has robust fallback if model output is not valid JSON.

## 10) `templates/` + `static/` (frontend)

- `templates/base.html`
  - Shared layout/navbar/footer.
  - Loads global CSS and React UMD scripts.

- `templates/dashboard/*.html`
  - Landing + dashboard shells + FAQ/lead page containers.

- `templates/accounts/*.html`
  - Login/signup pages.

- `static/styles.css`
  - SaaS-style UI theme.

- `static/js/csrf.js`
  - Helper for API fetch and CSRF header.

- `static/js/dashboard_recent_messages.js`
  - React table for recent messages.

- `static/js/faqs_app.js`
  - React FAQ CRUD UI.

- `static/js/leads_app.js`
  - React leads table UI.

## 11) Data ownership model (important)

- Every business user has isolated data:
  - messages, faqs, leads are filtered by `request.user`.
- In webhook flow, business is identified by incoming WhatsApp `phone_number_id`.
- This is the main tenancy boundary in MVP.

## 12) Typical request lifecycles

### A) Web dashboard request

1. Browser -> Django template view.
2. Template loads React widget.
3. React widget calls protected API endpoint.
4. DRF endpoint returns records for current user only.

### B) Incoming WhatsApp message

1. Meta POSTs webhook payload.
2. Django validates + logs + queues Celery.
3. Celery decides FAQ vs AI.
4. Lead is optionally captured.
5. Reply is sent through Meta Cloud API.

## 13) Where to start reading first (recommended)

1. `config/urls.py`
2. `messaging/webhook_views.py`
3. `messaging/tasks.py`
4. `ai_engine/services.py`
5. `messaging/models.py`
6. `faqs/matching.py`
7. `dashboard/views.py`

---

If you want, next I can also add a second doc: `docs/FUNCTION_INDEX.md` with a short one-line explanation for every function in the codebase (like a cheat-sheet).
