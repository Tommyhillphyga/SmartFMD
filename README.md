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

## Local Setup

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
