import psycopg2
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from .db import cursor
from .utils import generate_code
from .logger import logger

router = APIRouter()

MAX_CODE_ATTEMPTS = 5


class ShortenRequest(BaseModel):
    url: HttpUrl


# 🔹 Create short URL
@router.post("/shorten", status_code=201)
def shorten(body: ShortenRequest, request: Request):
    url = str(body.url)

    # The unique index on short_code rejects collisions, so retry with a new code
    for _ in range(MAX_CODE_ATTEMPTS):
        code = generate_code()
        try:
            cursor.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (%s, %s)",
                (url, code)
            )
            break
        except psycopg2.errors.UniqueViolation:
            continue
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique code")

    logger.info(f"Shortened URL: {url} -> {code}")

    return {
        "short_url": f"{str(request.base_url).rstrip('/')}/{code}",
        "code": code
    }


# 🔹 Stats endpoint
@router.get("/stats/{code}")
def stats(code: str):
    cursor.execute(
        "SELECT original_url, clicks, created_at FROM urls WHERE short_code = %s",
        (code,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "url": result[0],
        "clicks": result[1],
        "created_at": result[2]
    }


# 🔹 Redirect (registered last so it can't shadow /stats)
@router.get("/{code}")
def redirect_url(code: str):
    # One indexed query both counts the click and returns the target
    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s RETURNING original_url",
        (code,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="URL not found")

    logger.info(f"Redirected {code}")

    return RedirectResponse(url=result[0])
