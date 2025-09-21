# Contacts API

Features

- User registration with email verification
- JWT-based authentication
- CRUD operations for users
- Dockerized environment for easy setup
- PostgreSQL database

**Технології:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Docker

## Клонування
```bash
git clone https://github.com/Natalina686/goit-pythonweb-hw-08.git
cd goit-pythonweb-hw-08

Створення .env

POSTGRES_USER=postgres
POSTGRES_PASSWORD=pass123
POSTGRES_DB=contacts_db
DATABASE_URL=postgresql+psycopg2://postgres:pass123@db:5432/contacts_db

Запуск Docker

docker compose up -d --build

Міграції Alembic

docker compose exec app alembic upgrade head

API
URL: http://localhost:8000

Документація 
Swagger: http://localhost:8000/docs