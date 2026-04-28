# SMART FUEL DISPENSER MONITORING DASHBOARD

Production-oriented MVP for monitoring ordinary electronic petrol dispensers retrofitted with ESP32 pulse-reader devices. The platform delivers realtime fueling visibility, fraud alerts, multi-station management, operator accountability, analytics, simulator traffic, and automated test coverage.

## Stack

- Frontend: Next.js 15, React, TypeScript, Tailwind CSS, shadcn-style UI primitives, Recharts, TanStack Query, Zustand
- Backend: FastAPI, SQLAlchemy Async, PostgreSQL, Redis, MQTT, WebSocket, RQ
- Infra: Docker Compose, Nginx reverse proxy, GitHub Actions
- Testing: Pytest, Vitest, React Testing Library, Playwright, Locust

## Project Structure

```text
backend/
  alembic/
  app/
  scripts/
frontend/
  app/
  components/
  hooks/
  lib/
  store/
  tests/
infra/
  nginx/
locust/
.github/workflows/
simulate_devices.py
docker-compose.yml
.env.example
```

## Docker Setup

1. Copy environment values:

```bash
cp .env.example .env
```

2. Start the full stack:

```bash
docker compose up --build
```

3. Seed sample data from another terminal:

```bash
docker compose exec backend python scripts/seed.py
```

4. Open the app:

- Dashboard: `http://localhost`
- Backend API docs: `http://localhost/api/docs`
- Metrics: `http://localhost/api/metrics`

## Local Setup Without Docker

This project can also be run directly on your machine without Docker. The backend expects PostgreSQL, Redis, and an MQTT broker to already be available locally.

### Requirements

- Python `3.12`
- Node.js `22+`
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`
- Mosquitto or another MQTT broker running on `localhost:1883`

Example Ubuntu or Debian packages:

```bash
sudo apt update
sudo apt install postgresql redis-server mosquitto
sudo systemctl enable --now postgresql
sudo systemctl enable --now redis-server
```

If PostgreSQL is empty, create the local database once:

```bash
sudo -u postgres psql -c "CREATE USER smartfmd WITH PASSWORD 'smartfmd';"
sudo -u postgres psql -c "CREATE DATABASE smartfmd OWNER smartfmd;"
```

### 1. Backend environment

The backend reads its environment from `backend/.env` when launched from the `backend/` directory.

```bash
cd backend
cp .env.example .env
```

The checked-in `backend/.env.example` already uses local service hosts:

```env
DATABASE_URL=postgresql+asyncpg://smartfmd:smartfmd@localhost:5432/smartfmd
REDIS_URL=redis://localhost:6379/0
MQTT_HOST=localhost
MQTT_PORT=1883
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### 2. Backend install, migrate, seed, and run

From the project root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Then from `backend/`:

```bash
cd backend
python -m alembic -c alembic.ini upgrade head
python scripts/seed.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Optional background worker for queued notifications:

```bash
cd backend
source ../.venv/bin/activate
rq worker smartfmd
```

### 3. Frontend environment and run

Create `frontend/.env.local` from the local example:

```bash
cd frontend
cp .env.local.example .env.local
```

The local frontend values should look like this:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=SMART FUEL DISPENSER MONITORING DASHBOARD
```

Then start the frontend:

```bash
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

### 4. Open the app

- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8000/docs`
- Metrics: `http://localhost:8000/metrics`

### 5. Local simulator

Once the backend and MQTT broker are running, you can generate sample telemetry:

```bash
cd backend
source ../.venv/bin/activate
python scripts/simulate_devices.py --host localhost --port 1883 --interval 2
```

Or from the repo root:

```bash
source .venv/bin/activate
python simulate_devices.py --host localhost --port 1883 --interval 2
```

If you do not want MQTT locally, set `MQTT_ENABLED=false` in `backend/.env` and skip the simulator.

## Demo Credentials

- Email: `admin@example.com`
- Password: `Admin123!`

## Simulator

Run the MQTT simulator locally from the repo root:

```bash
python simulate_devices.py --host localhost --port 1883 --interval 1
```

Or from the backend directory:

```bash
cd backend
python scripts/simulate_devices.py --host localhost --port 1883 --interval 1
```

The simulator emits:

- random fueling sessions
- pulse telemetry
- low-pulse anomalies
- stalled pulse events
- meter reset patterns
- occasional offline gaps

## Testing Guide

Backend:

```bash
cd backend
pip install -r requirements.txt
pytest app/tests -q
```

Frontend unit tests:

```bash
cd frontend
npm install
npm run test
```

Frontend typecheck and lint:

```bash
cd frontend
npm run typecheck
npm run lint
```

Playwright E2E:

```bash
cd frontend
npx playwright install
npm run test:e2e
```

Locust load testing:

```bash
pip install -r locust/requirements.txt
locust -f locust/locustfile.py --host http://localhost/api -u 100 -r 10
```

If you are running without Docker or nginx, use `http://localhost:8000` as the Locust host instead.

Suggested realtime load target:

- 100 concurrent users
- 1000 websocket events/minute
- sustained `/transactions` and `/stations/dashboard/overview` traffic

## API Highlights

- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/stations`
- `GET /api/pumps`
- `GET /api/transactions`
- `GET /api/alerts`
- `GET /api/devices`
- `GET /api/reports/overview`
- `GET /api/users`
- `GET /api/health/live`
- `GET /api/health/ready`
- `GET /api/metrics`
- `WS /api/ws/dashboard/{station_id}`

## Seed Dataset

The seed script provisions:

- 1 company
- 3 stations
- 20 pumps
- 20 devices
- 50 users
- 5000 transactions
- seeded alerts and telemetry



## Notes

- Fraud detection rules are modular in `backend/app/services/fraud_engine.py`
- MQTT ingestion and websocket fan-out live in `backend/app/services/telemetry.py`
- The frontend uses optimistic, cache-driven live refresh via TanStack Query invalidation on websocket events
- Notifications are queued via RQ with email/SMS/WhatsApp placeholders ready for real provider integration
