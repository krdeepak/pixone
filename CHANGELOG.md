# Changelog

All notable changes to Pixone will be documented here.

Format: `## [version] — YYYY-MM-DD` with sections Added / Changed / Fixed / Removed.

---

## [0.2.0] — 2026-05-25

### Added

- Railway deployment support: `Procfile` runs migrations then starts Gunicorn
- `whitenoise` for serving Django static files without a separate web server
- `django-cors-headers` with `CORS_ALLOWED_ORIGINS` env var for cross-origin frontend
- `STATIC_ROOT` + compressed manifest static file storage for `collectstatic`
- `VITE_API_URL` env var support in frontend API client for split-domain deploys
- Media files served in production via explicit URL route (fallback for local storage)

### Changed

- S3 is now the default storage backend
- S3 results stored under `test/kd/` prefix in `pixfirst-fr` bucket

### Fixed

- `DATABASE_URL` parsing broken for `postgresql://` scheme
- `import.meta.env` TypeScript error — added `vite/client` types
- Removed invalid `onResize` prop from `<img>` in `FaceDetectPage`
- Gunicorn not starting on Railway — Procfile now uses `uv run`

---

## [0.1.0] — 2026-04-17

### Added

- Manual reframe: interactive drag-to-crop canvas with aspect ratio constraints (1:1, 4:3, 16:9, 9:16, 3:4, Free)
- Smart reframe: face-aware auto-crop using AWS Rekognition in three modes (Zoomed, Standard, Full)
- Face detection: detect faces in images with bounding boxes and confidence scores
- Pluggable storage backends: local filesystem and AWS S3
- Pluggable face detector backends: AWS Rekognition and own (placeholder)
- Job tracking: every request recorded as `ProcessingRequest` + `ProcessingResult` in PostgreSQL
- Django admin interface for browsing requests and results
- React frontend with Konva canvas for interactive cropping
- Django Ninja API with auto-generated OpenAPI docs at `/api/docs`