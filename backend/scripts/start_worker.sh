#!/bin/sh
set -eu

cd /app/backend

# Keep worker imports aligned with the latest mounted source tree.
find /app/backend -type d -name "__pycache__" -prune -exec rm -rf {} +
find /app/backend -type f -name "*.pyc" -delete

exec rq worker smartfmd
