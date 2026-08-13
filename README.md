# Signal Clone — Production Deployment Guide & Documentation

A real-time, privacy-focused secure messaging web application built with **Next.js 16 (React 19)**, **Vanilla CSS / TailwindCSS**, **FastAPI**, **SQLAlchemy**, and **WebSockets**.

---

## Architecture Overview

- **Frontend**: Next.js (App Router, TypeScript) deployed on **Vercel**.
- **Backend**: FastAPI (Python 3.11+), Uvicorn ASGI server, WebSockets engine deployed on **Render**.
- **Database**: SQLite with SQLAlchemy ORM (persistent disk support on Render).
- **Authentication**: JWT token-based authentication stored in `localStorage`.

---

## Deployment Configuration & Environment Variables

### 1. Backend Environment Variables (Render)

Configure these in the Render Dashboard (`Environment` tab) or via `backend/.env.example`:

| Environment Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `[Random 64-char string]` | Secret key used to sign JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `43200` | Token expiration (30 days) |
| `DATABASE_URL` | `sqlite:////var/data/signal.db` | SQLite database filepath (`/var/data` on persistent disk) |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` | Comma-separated CORS allowed origins |

### 2. Frontend Environment Variables (Vercel)

Configure these in the Vercel Project Settings (`Environment Variables` tab) or via `frontend/.env.example`:

| Environment Variable | Production Value Example | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com` | Base HTTP/HTTPS URL of Render backend |
| `NEXT_PUBLIC_WS_URL` | `wss://your-backend.onrender.com` | Base WS/WSS WebSocket URL of Render backend |

---

## Step-by-Step Production Deployment Instructions

### A. Deploy Backend to Render

1. **Push Repository**: Push project to GitHub/GitLab repository.
2. **Create New Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Web Service**.
   - Connect your GitHub repository.
3. **Configure Build & Start Settings**:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - Add `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`, and `ALLOWED_ORIGINS`.
5. **Persistent Disk (Optional for Free Tier / Recommended for Paid)**:
   - Mount disk at `/var/data` and set `DATABASE_URL=sqlite:////var/data/signal.db`.

---

### B. Deploy Frontend to Vercel

1. **Import Project**:
   - Go to [Vercel Dashboard](https://vercel.com/new) -> Import Git Repository.
2. **Configure Framework & Root Directory**:
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
3. **Environment Variables**:
   - Set `NEXT_PUBLIC_API_URL` to `https://your-backend.onrender.com`
   - Set `NEXT_PUBLIC_WS_URL` to `wss://your-backend.onrender.com`
4. **Deploy**:
   - Click **Deploy**. Vercel will build the application using `npm run build`.

---

## SQLite & Database Persistence Considerations

1. **Render Free Tier Ephemeral Disks**:
   - Render's free tier spins down after inactivity and wipes transient files.
   - To persist SQLite data across restarts, add a **1GB Persistent Disk** in Render mounted at `/var/data`.
2. **Multi-Instance Scaling**:
   - SQLite is single-file. If horizontal scaling (multiple backend instances) is required in the future, migrate `DATABASE_URL` to a hosted PostgreSQL instance (`postgresql://user:pass@host/db`).

---

## Local Development & Testing Commands

### Backend Startup
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Startup
```bash
cd frontend
npm run dev
```

### Automated Real-Time Verification Suite
```bash
python scratch/test_realtime.py
```
