# Development Guide

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.14+ | Use `python3.14` or a version manager like `pyenv` |
| uv | latest | Python package manager — `brew install uv` or `pip install uv` |
| Node.js | 20+ | Use `nvm` or install directly |
| PostgreSQL | 15+ | Must be running locally |
| AWS account | — | Needed for face detection and S3 storage |

---

## Backend Setup

### 1. Create database

```bash
psql -U postgres
CREATE USER pixone WITH PASSWORD 'pixone';
CREATE DATABASE pixone OWNER pixone;
\q
```

### 2. Install Python dependencies

```bash
cd api
uv sync
```

This creates `.venv` and installs all dependencies from `pyproject.toml` + `uv.lock`.

To add or remove dependencies later:

```bash
uv add <package>
uv remove <package>
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DEBUG=True
SECRET_KEY=any-long-random-string-for-dev
DATABASE_URL=postgres://pixone:pixone@localhost:5432/pixone

IMAGE_STORAGE_BACKEND=local

FACE_DETECTOR_BACKEND=rekognition
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket   # only needed if IMAGE_STORAGE_BACKEND=s3
```

### 4. Run migrations

```bash
uv run python manage.py migrate
```

### 5. Create superuser (for Django admin)

```bash
uv run python manage.py createsuperuser
```

### 6. Start dev server

```bash
uv run python manage.py runserver
```

- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`
- API docs: `http://localhost:8000/api/docs`

---

## Frontend Setup

```bash
cd ui
npm install
npm run dev
```

- UI: `http://localhost:3000`
- Proxies `/api/*` and `/media/*` to `http://localhost:8000` (configured in `vite.config.ts`)

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEBUG` | yes | — | `True` for dev, `False` for prod |
| `SECRET_KEY` | yes | — | Django secret key |
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `IMAGE_STORAGE_BACKEND` | no | `local` | `local` or `s3` |
| `AWS_ACCESS_KEY_ID` | if using AWS | — | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | if using AWS | — | AWS credentials |
| `AWS_REGION` | if using AWS | `us-east-1` | AWS region |
| `AWS_S3_BUCKET` | if `s3` backend | — | S3 bucket name |
| `FACE_DETECTOR_BACKEND` | no | `rekognition` | `rekognition` or `own` |
| `CORS_ALLOWED_ORIGINS` | prod only | `""` | Comma-separated frontend URLs e.g. `https://app.railway.app` |

---

## Common Tasks

### Add a Django app

```bash
cd api
uv run python manage.py startapp <appname> apps/<appname>
```

Register it in `pixone/settings.py` under `INSTALLED_APPS`.

Follow the three-file pattern: `api.py`, `service.py`, `schemas.py`.
Mount the router in `pixone/urls.py`.

### Add a database migration

After changing any model in `apps/*/models.py`:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Run the Django shell

```bash
uv run python manage.py shell
```

### Check all migrations are applied

```bash
uv run python manage.py showmigrations
```

---

## Code Style

### Python

- Follow PEP 8.
- Type hints required on all function signatures.
- Business logic in `service.py`, never in `api.py` or `models.py`.
- Use `python-decouple` `config()` for all env var reads (already set up in `settings.py`).

### TypeScript

- Strict mode is on (`tsconfig.json`). No `any` types.
- All API calls go through `src/api/pixone.ts` only.
- Tailwind CSS for all styling — no inline styles.

---

## Storage Backends

### Local (development default)

Files saved to `api/storage/uploads/` and `api/storage/results/`.
Served at `http://localhost:8000/media/`.

No extra config needed.

### S3

Set `IMAGE_STORAGE_BACKEND=s3` and fill in the four AWS variables.
Files are uploaded as public objects. URLs are returned directly from S3.

---

## Face Detector Backends

### Rekognition (default)

Requires `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`.
The IAM user/role needs `rekognition:DetectFaces` permission.

### Own (not implemented)

`FACE_DETECTOR_BACKEND=own` raises `NotImplementedError` — placeholder for a future self-hosted model.

---

## Django Admin

Navigate to `http://localhost:8000/admin/` after creating a superuser.

- **ProcessingRequests** — all jobs with feature, status, input params, timestamps
- **ProcessingResults** — results with output URL and metadata (shown inline under each request)

Filter by feature (`reframe`, `face_detection`) or status (`pending`, `done`, `failed`).