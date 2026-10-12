# URL Shortener API

FastAPI-based URL shortener using PostgreSQL and raw SQL (no ORM).

## Features
- Create short URLs (input validated with Pydantic)
- Redirect to the original URL
- Click tracking, counted atomically in the same query as the redirect lookup
- Stats endpoint
- Raw SQL with a unique B-tree index on `short_code` ([schema.sql](schema.sql))
- Collision-safe code generation: the unique index rejects duplicates and the API retries
- Docker Compose setup with PostgreSQL

## Run with Docker

```bash
docker compose up --build
```

API docs: http://localhost:8000/docs

## Run locally

```bash
cp .env.example .env          # then set your own DATABASE_URL
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The table and index are created automatically on startup from `schema.sql`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/shorten` | Body `{"url": "https://example.com"}` → `{"short_url": "...", "code": "aB3xY9"}` |
| GET | `/{code}` | Redirects to the original URL and increments its click count |
| GET | `/stats/{code}` | `{"url": "...", "clicks": 3, "created_at": "..."}` |

## Example

```bash
curl -X POST http://localhost:8000/shorten -H "Content-Type: application/json" -d '{"url": "https://github.com"}'
curl -i http://localhost:8000/aB3xY9
curl http://localhost:8000/stats/aB3xY9
```

## Tech Stack
FastAPI, PostgreSQL, psycopg2, Docker
