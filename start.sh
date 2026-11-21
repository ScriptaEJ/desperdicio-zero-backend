#!/bin/sh
set -e

echo "Subindo possiveis alterações nas migrations"
alembic upgrade head

echo "Iniciando Backend!"
uvicorn app.main:app --host 0.0.0.0 --port 5000