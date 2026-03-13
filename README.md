# {Project Name}

> Full-stack template: Next.js + FastAPI + PostgreSQL + Redis

## Tech Stack

| Layer      | Technology         | Deploy           |
| ---------- | ------------------ | ---------------- |
| Frontend   | Next.js (React)    | Vercel           |
| Backend    | FastAPI (Python)   | Render           |
| Database   | PostgreSQL         | AWS Lightsail    |
| Cache      | Redis              | AWS Lightsail    |

## Quick Start (Local Development)

```bash
# 1. Clone & setup environment
cp .env.example .env

# 2. Start all services
docker compose up -d

# 3. Frontend: http://localhost:3000
# 4. Backend API: http://localhost:8000
# 5. API Docs: http://localhost:8000/docs
```

## Project Structure

```
├── app/                  # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # Reusable UI components
│   │   ├── lib/          # Utilities & API client
│   │   ├── hooks/        # Custom React hooks
│   │   └── config/       # Environment config
│   └── docker/           # Frontend Dockerfile
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # DB models & Pydantic schemas
│   │   ├── routers/      # API endpoints
│   │   └── services/     # Business logic
│   ├── migrations/       # SQL migrations
│   └── tests/            # pytest test suite
├── docs/                 # Documentation
├── plans/                # Session plans
└── docker-compose.yml    # Local dev environment
```

## Development

### Frontend (Next.js)
```bash
cd app
npm install
npm run dev          # Dev server on :3000
npm test             # Vitest unit tests
npm run test:e2e     # Playwright E2E tests
npm run typecheck    # TypeScript check
```

### Backend (FastAPI)
```bash
cd backend
uv sync              # Install dependencies
uv run uvicorn app.main:app --reload  # Dev server on :8000
uv run pytest tests/ -v               # Run tests
```

## Deployment

### Frontend → Vercel
1. Connect repo to Vercel
2. Set root directory to `app/`
3. Set env var: `NEXT_PUBLIC_API_URL`

### Backend → Render
1. Create new Web Service on Render
2. Set root directory to `backend/`
3. Docker deploy using `backend/Dockerfile`
4. Set env vars: `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`

### Database & Redis → AWS Lightsail
1. Create Lightsail instance
2. SSH into instance
3. Run: `docker compose -f docker-compose.prod.yml up -d`
4. Configure firewall: open ports 5432 (Postgres) and 6379 (Redis)

## License

MIT
