# URL Shortener API

FastAPI-based URL shortener using PostgreSQL and raw SQL.

## Features
- Create short URLs
- Redirect to original URL
- Click tracking
- Stats endpoint
- Raw SQL (no ORM)
- Indexed database for performance

## Run

uvicorn app.main:app --reload

## Endpoints
POST /shorten  
GET /{code}  
GET /stats/{code}

## Tech Stack
FastAPI, PostgreSQL, Docker