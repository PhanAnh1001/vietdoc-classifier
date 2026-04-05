# Architecture

## Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐
│   Vercel     │     │   Render    │     │    AWS Lightsail        │
│             │────▶│             │────▶│                         │
│  Next.js    │     │  FastAPI    │     │  PostgreSQL  │  Redis   │
│  Frontend   │     │  Backend    │     │              │          │
└─────────────┘     └─────────────┘     └─────────────────────────┘
```

## Services

### Frontend (Vercel)
- Next.js App Router
- Server-side rendering
- Auto-deploy from `master` branch

### Backend (Render)
- FastAPI with async PostgreSQL
- Docker-based deployment
- Auto-deploy from `master` branch

### Database (AWS Lightsail)
- PostgreSQL 16
- Docker Compose managed
- Persistent volume storage

### Cache (AWS Lightsail)
- Redis 7
- Session cache and rate limiting
- Co-located with database
