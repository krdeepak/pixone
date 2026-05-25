# Requirements

This document captures what Pixone must do (functional) and how it must behave (non-functional).
Update this file before implementing new features — treat it as the source of truth for scope.

---

## Phase 1 — Current (MVP)

### FR-01: Manual Reframe

- User can upload an image and see it in an interactive canvas.
- User can drag and resize a crop box over the image.
- User can constrain the crop box to a fixed aspect ratio: 1:1, 4:3, 16:9, 9:16, 3:4.
- User can select "Free" to crop without aspect ratio constraints.
- User submits the crop — backend returns a downloadable cropped image.
- Output format is JPEG at 92% quality.
- Output can optionally be resized to a specific pixel dimension (`output_width` × `output_height`).

### FR-02: Smart Reframe

- User can upload an image and select a reframe mode and aspect ratio.
- System detects faces in the image using AWS Rekognition.
- If no face is detected, the system returns a clear error (not a silent failure).
- System crops around the most prominent (largest by area) face.
- Three crop modes:
  - **Zoomed** — tight crop, 0.3× face-size padding on each side
  - **Standard** — balanced crop, 0.5× face-size padding on each side
  - **Full** — wide crop, 1.8× face-size padding on each side
- Supported aspect ratios: 1:1, 4:3, 16:9, 9:16, 3:4.
- Crop is capped to image bounds without distorting the aspect ratio.
- Output format is JPEG at 92% quality.
- Response includes face count and metadata (crop box, original size, output size).

### FR-03: Face Detection

- User can upload an image.
- System detects all faces using AWS Rekognition.
- Response includes per-face bounding box (x, y, width, height in pixels) and confidence score.
- UI renders bounding boxes overlaid on the image.
- Face count is displayed.

### FR-04: Job Tracking

- Every processing request (reframe, smart reframe, face detection) is recorded in the database.
- Each request tracks: feature, status (pending/done/failed), input params, input file URL, timestamp.
- Each successful request has an associated result: output URL and metadata.
- All requests are viewable in Django admin.

### FR-05: Storage Backends

- System supports two storage backends switchable via environment variable:
  - **Local** — saves files to `api/storage/`, serves via Django media URL.
  - **S3** — uploads to AWS S3, returns public URL.
- Application code is backend-agnostic (uses `get_storage()` abstraction).

---

## Non-Functional Requirements

### NFR-01: Performance
- API responses for reframe and face detection complete within 5 seconds for images up to 10 MB.

### NFR-02: Correctness
- Smart crop must never produce a crop box outside the image bounds.
- Aspect ratio of smart crop output must match the requested ratio (within 1px rounding tolerance).

### NFR-03: Security
- No secrets committed to version control.
- AWS credentials only in environment variables.
- `DEBUG=False` in production.

### NFR-04: Configurability
- All environment-specific config (DB URL, AWS keys, storage backend, face detector backend) controlled via `.env` / environment variables.
- No hardcoded values for any of the above.

### NFR-05: Observability
- All processing requests and results persisted to the database for auditability.
- Failures are recorded with `status=failed` on the ProcessingRequest row.

---

## Phase 2 — Planned (Not Yet Scoped)

These are candidate features. Scope and priority to be decided.

- [ ] Multiple face support — reframe around multiple detected faces
- [ ] Batch processing — upload multiple images and reframe all
- [ ] Self-hosted face detector — replace Rekognition with local model (OwnFaceDetector)
- [ ] Async job processing — return a job ID immediately, poll for completion
- [ ] Job history UI — browse past requests and results in the frontend
- [ ] API authentication — protect endpoints with API keys or JWT
- [ ] Signed S3 URLs — replace public S3 URLs with time-limited signed URLs
- [ ] File size and type validation — enforce limits at upload time
- [ ] Video frame reframing — extend reframe to video files

---

## Out of Scope (Phase 1)

- User accounts or authentication
- Paid tiers or usage quotas
- Mobile app
- Non-JPEG output formats (PNG, WebP)
- Real-time collaborative editing