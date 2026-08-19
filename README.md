# Max ERP

A small, modern ERP (Enterprise Resource Planning) system with built-in AI
capabilities. The project is split into a FastAPI backend and a Next.js
frontend, both fully containerized and deployable with a single
`docker compose up`.

## 1. Project overview

Max ERP provides a role-based multi-user platform where an administrator
(`root`) can manage regular users, while every authenticated user signs in
through a JWT + OAuth2 password flow. The system is designed to grow into a
full ERP with inventory, sales, accounting and an AI assistant (LangChain /
LangGraph + BGE embeddings) that answers questions in natural language.

What is included out of the box:

- **Backend** — FastAPI with auto-generated Swagger docs (`/docs`), SQLAlchemy
  2.0 async models, PostgreSQL via asyncpg, RBAC (one `root` account, many
  regular `user` accounts), JWT access/refresh tokens and structlog structured
  logging.
- **Frontend** — Next.js 15 company landing page and a login page. The landing
  page has a prominent **Login** button that routes to `/login`, where users
  authenticate with the backend. After login they reach a basic dashboard.
- **Infrastructure** — Dockerfiles for both services, a `docker-compose.yml`
  that provisions PostgreSQL + backend + frontend, and a GitHub Actions
  pipeline that runs tests, builds images and deploys to a local Mac mini.

## 2. Technology stack

### Backend

| Concern           | Technology                                        |
| ----------------- | ------------------------------------------------- |
| Language          | Python 3.12                                       |
| Package manager   | uv (with `pyproject.toml`)                        |
| Web framework     | FastAPI (auto-generated Swagger/OpenAPI at `/docs`) |
| ORM               | SQLAlchemy 2.0 (async) + asyncpg + PostgreSQL     |
| Validation        | Pydantic v2 + pydantic-settings                   |
| Auth              | JWT (PyJWT) + OAuth2 password flow + bcrypt       |
| Authorization     | RBAC (roles: `root`, `user`)                      |
| Logging           | structlog (structured JSON)                       |
| AI                | LangChain, LangGraph, BGE embeddings              |
| Testing           | pytest + pytest-asyncio (SQLite in-memory)        |

### Frontend

| Concern           | Technology                              |
| ----------------- | --------------------------------------- |
| Framework         | Next.js 15 (App Router) + React 19      |
| Styling           | shadcn/ui + Tailwind CSS                |
| State management  | Zustand                                 |
| Forms             | React Hook Form + Zod                   |
| Auth              | Auth.js v5 (credentials -> backend JWT) |
| File uploads      | react-dropzone                          |
| Markdown          | react-markdown                          |
| Language          | TypeScript                              |

### DevOps

| Concern          | Technology                              |
| ---------------- | --------------------------------------- |
| Containers       | Docker + Docker Compose                 |
| CI/CD            | GitHub Actions (test -> build -> deploy) |
| Target host      | Local Mac mini (self-hosted runner)     |

## 3. Local (Mac mini) deployment

### Prerequisites

- Docker with Docker Compose (e.g. [Docker Desktop](https://www.docker.com/products/docker-desktop/) or OrbStack)
- `uv` (for backend development outside Docker)
- Node.js 20+ and npm (for frontend development outside Docker)
- Git

### Option A — One-command deployment with Docker Compose (recommended)

```bash
git clone <repo-url> max_erp
cd max_erp
cp .env.example .env

docker compose up -d --build
```

Once the stack is up:

| Service            | URL                            |
| ------------------ | ------------------------------ |
| Frontend (landing) | http://localhost:3000          |
| Backend API        | http://localhost:8000          |
| Swagger docs       | http://localhost:8000/docs     |
| PostgreSQL         | localhost:5432 (user `maxerp`) |

Default root account (change via `.env`):

| Username | Password   |
| -------- | ---------- |
| root     | root12345  |

### Option B — Run locally without Docker

**Backend:**

```bash
cd backend
cp .env.example .env          # point DATABASE_URL at a running Postgres
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev           # serves on http://localhost:3001 (see note below)
```

> Note: `npm run dev` runs on port **3001** on purpose. The Docker deployment
> occupies port **3000**, and on Docker Desktop a lingering dev server can
> shadow that port (binding it while serving stale, broken CSS). Keeping dev on
> 3001 avoids the collision; the backend allows both origins via `CORS_ORIGINS`.

### CI/CD on the Mac mini

The pipeline in `.github/workflows/ci.yml` runs backend tests and the frontend
build on GitHub-hosted runners, then deploys on a **self-hosted runner**
installed on your Mac mini:

1. On the Mac mini: *Settings → Actions → Runners → New self-hosted runner*,
   follow the setup steps and add the label `macmini` (e.g.
   `./config.sh --labels macmini`).
2. Ensure Docker is installed and the runner user can run `docker compose`.
3. Push to `main` — the workflow builds the images and runs
   `docker compose up -d` on the machine.

> Note: keep `JWT_SECRET_KEY` and `AUTH_SECRET` (in `.env`) secret and use
> strong random values in production (`openssl rand -base64 32`).

## Project structure

```
max_erp/
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/        # routers (auth, users, health) + dependencies
│   │   ├── core/       # config, database, security, logging
│   │   ├── ai/         # LangChain/LangGraph + BGE embeddings
│   │   ├── db/         # startup DB seeding (roles + root user)
│   │   ├── models/     # SQLAlchemy ORM models
│   │   └── schemas/    # Pydantic schemas
│   ├── tests/          # pytest suite
│   └── pyproject.toml  # uv project + dependencies
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/        # App Router pages + Auth.js route handler
│   │   ├── components/ # UI + landing + login form
│   │   ├── lib/        # utilities + API client
│   │   ├── store/      # Zustand stores
│   │   └── types/      # TypeScript types
│   └── package.json
├── docker-compose.yml  # Postgres + backend + frontend
├── .github/workflows/  # CI/CD pipeline
└── .env.example        # environment template
```
