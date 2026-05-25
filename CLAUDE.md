# CLAUDE.md — Instructions for Claude Code

This file guides Claude's behavior when working in this repository.
Read this before making any changes.

---

## Project Summary

Pixone is a Django + React image processing app. The two main features are:
- **Reframe** — manual drag-to-crop and smart face-aware auto-crop
- **Face Detection** — detect faces via AWS Rekognition

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full picture.

---

## Running the Project

### Backend (Django)

```bash
cd api
source .venv/bin/activate
python manage.py runserver          # dev server on :8000
python manage.py migrate            # apply migrations
python manage.py makemigrations     # after model changes
```

### Frontend (React)

```bash
cd ui
npm run dev       # dev server on :3000 (proxies /api and /media to :8000)
npm run build     # production build
```

### Tests

```bash
# Backend (once test suite is added)
cd api
python manage.py test

# Frontend (once test suite is added)
cd ui
npm test
```

---

## Code Conventions

### Backend

- **Never put business logic in api.py (views).** All logic goes in `service.py`.
- **Never put logic in models.** Models are data only.
- Request/response shapes live in `schemas.py` (Pydantic via Django Ninja).
- Each Django app (`reframe`, `face_detection`) has: `api.py`, `service.py`, `schemas.py`.
- All new apps follow this same three-file pattern.
- Use `ProcessingRequest` + `ProcessingResult` models from `core` for every processing job.
- Storage is abstracted — use `get_storage().upload(...)`. Never reference local paths directly.
- Face detector is abstracted — use `get_detector().detect(...)`. Never call Rekognition directly.
- Use `python-decouple` for all config values. No hardcoded secrets or paths.

### Frontend

- TypeScript strict mode is on. No `any` types.
- All API calls go through `src/api/pixone.ts`. Components do not call Axios directly.
- Canvas interactions use Konva (`react-konva`). No raw DOM canvas manipulation.
- Tailwind CSS only — no inline styles, no CSS modules.
- Components are functional with hooks. No class components.

---

## Architecture Rules

- The storage backend (local vs S3) is controlled by `IMAGE_STORAGE_BACKEND` env var.
- The face detector backend (rekognition vs own) is controlled by `FACE_DETECTOR_BACKEND` env var.
- Do not hardcode either backend anywhere in application code.
- `OwnFaceDetector` is not yet implemented — do not stub or call it.

---

## What to Avoid

- Do not add features beyond what is asked.
- Do not add docstrings or comments to code you didn't change.
- Do not add error handling for impossible scenarios.
- Do not create helpers/utilities for one-time operations.
- Do not use `any` in TypeScript.
- Do not commit `.env` — only `.env.example` is version-controlled.
- Do not import boto3 or Rekognition outside of `face_detection/services/rekognition.py`.

---

## Key File Locations

| What | Where |
|------|-------|
| Django settings | `api/pixone/settings.py` |
| URL routing | `api/pixone/urls.py` |
| Core models | `api/apps/core/models.py` |
| Storage backends | `api/apps/core/storage/` |
| Reframe logic | `api/apps/reframe/service.py` |
| Face detection backends | `api/apps/face_detection/services/` |
| Reframe schemas | `api/apps/reframe/schemas.py` |
| Face detection schemas | `api/apps/face_detection/schemas.py` |
| API client (frontend) | `ui/src/api/pixone.ts` |
| Interactive canvas | `ui/src/components/reframe/ImageCanvas.tsx` |