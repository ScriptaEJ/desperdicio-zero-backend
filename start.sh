echo "Subindo possiveis alterações nas migrations"
alembic upgrade head

echo "Iniciando CodeLearn Backend!"
uvicorn app.main:app --host 0.0.0.0 --port 5000

