# Architecture

## Overview

Pixone is a client-server application:

- **Backend** — Django REST API (Django Ninja), serves image processing endpoints
- **Frontend** — React SPA, communicates with the backend via HTTP

```
Browser (React SPA)
       |
       | HTTP (JSON + multipart)
       v
Django Ninja API  (:8000)
       |
       |--- Reframe Service
       |--- Face Detection Service
       |
       |--- Storage Backend (local or S3)
       |--- Face Detector Backend (Rekognition or own)
       |
       v
PostgreSQL (job tracking)
```

In development, the Vite dev server (:3000) proxies `/api` and `/media` to the Django backend (:8000). In production, a reverse proxy (nginx or similar) handles this.

---

## Backend Structure

```
api/
├── pixone/
│   ├── settings.py       # Central config (reads from .env via python-decouple)
│   └── urls.py           # Mounts all Ninja routers under /api/
│
├── apps/
│   ├── core/
│   │   ├── models.py     # ProcessingRequest, ProcessingResult
│   │   └── storage/      # Storage abstraction (local + S3 backends)
│   │
│   ├── reframe/
│   │   ├── api.py        # POST /api/reframe/, POST /api/reframe/smart/
│   │   ├── service.py    # Image cropping logic
│   │   └── schemas.py    # Request/response Pydantic schemas
│   │
│   └── face_detection/
│       ├── api.py        # POST /api/face-detection/
│       ├── schemas.py    # Request/response Pydantic schemas
│       └── services/     # Detector backends (Rekognition, own placeholder)
```

Each Django app follows the same three-layer pattern:
1. **api.py** — HTTP boundary only. Reads request, calls service, returns response.
2. **service.py** — All business logic. No HTTP awareness.
3. **schemas.py** — Data shapes for validation and serialization.

---

## Data Models

### ProcessingRequest

Tracks every incoming job regardless of feature.

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto PK |
| `feature` | enum | `reframe` or `face_detection` |
| `status` | enum | `pending`, `done`, `failed` |
| `input_params` | JSON | Feature-specific params (crop box, mode, aspect ratio, etc.) |
| `input_file_url` | URL | Where the uploaded input image was stored |
| `created_at` | datetime | Auto |

### ProcessingResult

One-to-one with ProcessingRequest. Created on success.

| Field | Type | Notes |
|-------|------|-------|
| `request` | FK | Points to ProcessingRequest |
| `output_url` | URL | Where the result image was stored (empty for face detection) |
| `metadata` | JSON | Feature-specific result data (crop box, face count, sizes, etc.) |
| `created_at` | datetime | Auto |

---

## Storage Abstraction

Controlled by `IMAGE_STORAGE_BACKEND` env var (`local` or `s3`).

```python
# Usage everywhere in app code:
get_storage().upload(bytes, folder="uploads", filename="foo.jpg")
```

- **LocalStorage** — saves to `api/storage/` and serves via Django's `MEDIA_URL`
- **S3Storage** — uploads to AWS S3, returns public URL

Both implement the same `StorageBackend` Protocol.

---

## Face Detector Abstraction

Controlled by `FACE_DETECTOR_BACKEND` env var (`rekognition` or `own`).

```python
# Usage everywhere in app code:
get_detector().detect(image_bytes)  # returns list[FaceResult]
```

- **RekognitionDetector** — calls AWS Rekognition `detect_faces`
- **OwnFaceDetector** — not yet implemented (raises NotImplementedError)

Both implement the same `FaceDetector` Protocol. `FaceResult` is a dataclass with `x, y, width, height, confidence, landmarks`.

---

## Frontend Structure

```
ui/src/
├── App.tsx                         # Router, nav shell
├── api/
│   └── pixone.ts                   # All API calls (Axios). No component touches Axios directly.
└── components/
    ├── reframe/
    │   ├── ReframePage.tsx          # Page state manager (manual vs smart mode)
    │   ├── ImageCanvas.tsx          # Konva canvas — drag/resize crop box
    │   └── Controls.tsx             # Aspect ratio selector, submit button
    └── face_detection/
        └── FaceDetectPage.tsx       # Upload + bounding box overlay UI
```

### Data Flow (Reframe)

1. User uploads image → `ReframePage` holds it in state
2. Image rendered in `ImageCanvas` (Konva stage)
3. User drags crop box — canvas updates local state
4. User clicks Submit → `pixone.ts` POSTs multipart form to `/api/reframe/`
5. Response contains `output_url` → displayed as download link

### Data Flow (Smart Reframe)

1. User uploads image, selects mode and aspect ratio
2. On submit → `pixone.ts` POSTs to `/api/reframe/smart/`
3. Backend: uploads image → detects faces → computes crop → saves result
4. Response contains `output_url` + `face_count` + `metadata`

---

## Key Design Decisions

**Why Django Ninja over DRF?**
Ninja uses Pydantic for schema validation and generates OpenAPI docs automatically. Less boilerplate than DRF serializers for a simple API.

**Why Konva for the canvas?**
React-compatible canvas library with built-in drag/resize transformer — avoids manual DOM event handling for the crop box interaction.

**Why abstract storage and face detector?**
Allows local development without AWS credentials (local storage) and future swap to a self-hosted face detector (own backend) without changing application code.

**Why synchronous job execution?**
Current scale doesn't require a task queue. Jobs complete in under 2s. If async is needed later, the `ProcessingRequest`/`ProcessingResult` model structure already supports it — just needs a worker.