# Pixone

Intelligent image reframing and face detection tool.

Upload an image, select an aspect ratio, and let Pixone crop it manually or automatically around the most prominent face.

---

## Features

- **Manual Reframe** — drag-to-crop with aspect ratio constraints (1:1, 4:3, 16:9, 9:16, 3:4, Free)
- **Smart Reframe** — face-aware auto-crop in three modes: Zoomed, Standard, Full
- **Face Detection** — detect faces in images with bounding boxes and confidence scores

---

## Requirements

- Python 3.14+
- Node.js 20+
- PostgreSQL 15+
- AWS account with Rekognition access (for face-based features)

---

## Quick Start

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd pixone
```

### 2. Backend

```bash
cd api
cp .env.example .env
# Edit .env with your database URL and AWS credentials

python -m venv .venv
source .venv/bin/activate
pip install -e .

python manage.py migrate
python manage.py runserver
```

API will be available at `http://localhost:8000`
Interactive API docs: `http://localhost:8000/api/docs`

### 3. Frontend

```bash
cd ui
npm install
npm run dev
```

UI will be available at `http://localhost:3000`

The Vite dev server proxies `/api` and `/media` requests to the Django backend automatically.

---

## Project Structure

```
pixone/
├── api/                    # Django REST API (Django Ninja)
│   ├── apps/
│   │   ├── core/           # Shared models and storage backends
│   │   ├── reframe/        # Manual and smart reframe feature
│   │   └── face_detection/ # Face detection feature
│   ├── pixone/             # Django project config (settings, urls)
│   ├── storage/            # Local file storage (dev)
│   └── pyproject.toml
│
├── ui/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Feature UI components
│   │   └── api/            # Typed API client (Axios)
│   └── package.json
│
└── docs/                   # Project documentation
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and component overview |
| [API.md](docs/API.md) | API endpoint reference |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Functional and non-functional requirements |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Developer setup, conventions, and workflows |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [CLAUDE.md](CLAUDE.md) | Instructions for Claude Code |