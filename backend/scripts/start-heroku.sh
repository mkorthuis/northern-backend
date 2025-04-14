#!/bin/bash
set -e

echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Port: $PORT"

# Run migrations
echo "Running database migrations..."
python -m alembic upgrade head &

# Run uvicorn with reduced workers and optimized timeout flags
echo "Starting uvicorn with optimized settings..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 2 \
    --timeout-keep-alive 75 \
    --proxy-headers \
    --log-level info