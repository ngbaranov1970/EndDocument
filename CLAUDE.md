# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

EndDocument — a small internal app for tracking work-permit documents ("документы") per organization, with archiving and JWT-based auth. Backend: FastAPI + SQLAlchemy (async) + SQLite + Alembic. Frontend: Vue 3 + Vite + Tailwind CSS.

## Commands

### Backend (run from repo root)

```bash
# activate the existing venv first (.venv already present at repo root)
uvicorn app.main:app --reload          # dev server on http://127.0.0.1:8000
alembic upgrade head                    # apply migrations
alembic revision --autogenerate -m "..." # create a new migration after model changes
```

There is no test suite and no linter/formatter config in this repo (no pytest, ruff, or pyproject.toml) — don't invent commands for these.

`uvicorn` must be started with the repo root as the working directory (or rely on `app/config.py`, which resolves `.env` relative to the module's own location rather than cwd — see below).

### Frontend (run from `frontend/`)

```bash
npm run dev       # Vite dev server, http://localhost:5173
npm run build      # production build to frontend/dist
npm run preview    # preview a production build
```

No test runner or ESLint config is set up for the frontend either.

### Docker

`docker-compose.yml` runs two services: `backend` (this repo's `Dockerfile`, runs `alembic upgrade head && uvicorn ...` on container start, SQLite file lives in the `db_data` volume) and `frontend` (built separately under `frontend/`, served on port 80). The backend container is not exposed directly — only `frontend`'s nginx is meant to reach it internally.

## Configuration

Settings are loaded via `app/config.py` (`pydantic-settings`) from a `.env` file at the repo root — see `.env.example` for the required keys (`jwt_secret_key` has no default and is required). `BASE_DIR` in `config.py` is computed from `__file__`, not cwd, specifically so the app finds `.env` regardless of where the process is launched from.

`app/main.py` hardcodes CORS `allow_origins` to the Vite dev server (`http://localhost:5173` / `http://127.0.1:5173`) — update this if the frontend origin changes.

## Backend architecture

Layout: `app/routers/` (FastAPI endpoints) → `app/schemas/` (Pydantic I/O models) → `app/models/` (SQLAlchemy ORM) → `app/db/` (engine/session). `app/service/auth.py` holds all auth logic (password hashing, JWT creation/verification, current-user/superuser dependencies).

- **Auth**: access + refresh JWT pair. Refresh tokens are not stored raw — only a SHA-256 hash lives on `User.refresh_token_hash`, and each refresh call rotates (invalidates the old hash, issues a new pair) — see `verify_and_invalidate_refresh_token` in `app/service/auth.py`. All document/organization/archive routers depend on `get_current_user` at the router level (`dependencies=[Depends(get_current_user)]`), so every route in those routers requires a valid access token by default. Admin-only user-management endpoints additionally depend on `get_current_superuser`.
- **First user becomes admin**: the first account ever registered (`user_router.create_user`) is auto-activated and made superuser; every subsequent registration starts inactive and must be activated by a superuser via `/users/admin/{user_id}/activate`.
- **Documents grouped by organization**: `GET /documents/` and `GET /documents/archived` both return `list[DocumentsByOrganization]` — a join between `Document` and `Organization`, grouped in Python into one entry per organization (see the identical grouping loop in `document_router.get_all_documents` and `archive_router.get_archived_documents`). Archiving is a soft flag (`Document.is_archived`), not a delete — `archive_router.py` has separate `archive`/`restore`/`delete` endpoints.
- **SQLite booleans**: model `server_default` values for booleans must use `text("1")`/`text("0")`, never string literals like `"true"` — SQLite stores those as literal text and `== True` filters silently fail to match. This is called out in comments in `organizations_models.py` and `users_model.py`; follow the same pattern for any new boolean columns.
- **Migrations**: `app/migrations/env.py` imports every model module explicitly (`Document`, `Organization`, ...) so `Base.metadata` is fully populated for autogenerate — new model modules must be imported there too or Alembic won't see them.

## Frontend architecture

- **Routing** (`src/router/index.js`): a single `beforeEach` guard reads `meta.requiresAuth` / `meta.guestOnly` / `meta.requiresSuperuser` on each route and redirects based on `useAuth()` state. Add new protected routes via these `meta` flags rather than per-component checks.
- **Auth store** (`src/store/auth.js`): a plain singleton built on `reactive()` (no Pinia/Vuex) — `useAuth()` returns the same shared state everywhere. Tokens persist in `localStorage` (`access_token`, `refresh_token`).
- **API client** (`src/api/client.js`): a single Axios instance injects the bearer token on every request and, on a 401 (excluding the login/refresh calls themselves), transparently refreshes the token and retries — including queuing concurrent requests while a refresh is in flight. Other `src/api/*.js` files are thin wrappers around this client; follow that pattern for new endpoints rather than calling axios directly from components.
- **Views** (`src/views/`) fetch data in `onMounted` and hold their own local state; there's no central store for documents/organizations. `HomeView.vue` and `ArchiveView.vue` both consume the same `DocumentsByOrganization[]` shape from the backend and render it grouped by organization.
- Styling is Tailwind utility classes inline in templates — no component library.

- Ты мой очень умный помошник по програмированию
- Каждый файл делаем отдельно и объясняем что сделали
- Страемся вести диалоги по русски

