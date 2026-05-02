from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from .db import cursor
from .utils import generate_code
from .logger import logger

router = APIRouter()

# 🔹 Create short URL
@router.post("/shorten")
def shorten(url: str):

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    # ensure unique code
    while True:
        code = generate_code()
        cursor.execute("SELECT 1 FROM urls WHERE short_code=%s", (code,))
        if not cursor.fetchone():
            break

    cursor.execute(
        "INSERT INTO urls (original_url, short_code, clicks) VALUES (%s, %s, %s)",
        (url, code, 0)
    )

    logger.info(f"Shortened URL: {url} -> {code}")

    return {
        "short_url": f"http://localhost:8000/{code}"
    }


# 🔹 Redirect
@router.get("/{code}")
def redirect_url(code: str):
    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = %s",
        (code,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="URL not found")

    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s",
        (code,)
    )

    logger.info(f"Redirected {code}")

    return RedirectResponse(url=result[0])


# 🔹 Stats endpoint
@router.get("/stats/{code}")
def stats(code: str):
    cursor.execute(
        "SELECT original_url, clicks FROM urls WHERE short_code = %s",
        (code,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "url": result[0],
        "clicks": result[1]
    }