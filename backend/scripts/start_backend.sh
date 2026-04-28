#!/bin/sh
set -eu

cd /app/backend

# Clear stale bytecode from bind mounts before importing Alembic/app modules.
find /app/backend -type d -name "__pycache__" -prune -exec rm -rf {} +
find /app/backend -type f -name "*.pyc" -delete

echo "Starting backend migrations from /app/backend/alembic/env.py"
python -B -m alembic -c /app/backend/alembic.ini upgrade head
exec python -B -m uvicorn app.main:app --host 0.0.0.0 --port 8000
