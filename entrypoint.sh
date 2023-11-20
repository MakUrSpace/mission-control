#!/bin/sh

# Exit script in case of error
set -e

echo "Running migrations"
flask db upgrade

echo "Seeding database"
python scripts/seed_db.py

echo "Starting server"
exec "$@"
