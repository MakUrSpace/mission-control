#!/bin/sh
set -e

echo "Setting environment variables"
python -c "from dotenv import load_dotenv; load_dotenv()"

echo "Running migrations"
flask db upgrade

echo "Seeding database"
python scripts/seed_db.py

echo "Starting server"
exec "$@"
