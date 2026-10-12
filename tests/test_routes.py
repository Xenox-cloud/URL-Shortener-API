"""API tests that run without PostgreSQL by swapping in an in-memory cursor.

Run: pip install pytest httpx && pytest
"""
import sys
import types

import psycopg2
import pytest


class FakeCursor:
    """Mimics the few SQL statements the routes send."""

    def __init__(self):
        self.rows = {}
        self.result = None
        self.collide_next_insert = False

    def execute(self, sql, args=()):
        q = " ".join(sql.split())
        if q.startswith("INSERT"):
            url, code = args
            if self.collide_next_insert:
                self.collide_next_insert = False
                raise psycopg2.errors.UniqueViolation()
            self.rows[code] = {"url": url, "clicks": 0, "created_at": "2026-01-01T00:00:00Z"}
        elif q.startswith("UPDATE"):
            row = self.rows.get(args[0])
            self.result = None
            if row:
                row["clicks"] += 1
                self.result = (row["url"],)
        elif q.startswith("SELECT"):
            row = self.rows.get(args[0])
            self.result = (row["url"], row["clicks"], row["created_at"]) if row else None

    def fetchone(self):
        return self.result


@pytest.fixture
def client():
    fake_db = types.ModuleType("app.db")
    fake_db.cursor = FakeCursor()
    sys.modules["app.db"] = fake_db
    for mod in ("app.routes", "app.main"):
        sys.modules.pop(mod, None)

    from fastapi.testclient import TestClient
    from app.main import app

    yield TestClient(app), fake_db.cursor


def test_shorten_redirect_and_stats(client):
    c, _ = client
    res = c.post("/shorten", json={"url": "https://github.com"})
    assert res.status_code == 201
    code = res.json()["code"]
    assert res.json()["short_url"].endswith("/" + code)

    redirect = c.get("/" + code, follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://github.com/"

    c.get("/" + code, follow_redirects=False)
    assert c.get("/stats/" + code).json()["clicks"] == 2


def test_invalid_url_rejected(client):
    c, _ = client
    assert c.post("/shorten", json={"url": "not-a-url"}).status_code == 422


def test_code_collision_is_retried(client):
    c, cursor = client
    cursor.collide_next_insert = True
    res = c.post("/shorten", json={"url": "https://example.com"})
    assert res.status_code == 201
    assert res.json()["code"] in cursor.rows


def test_unknown_code_returns_404(client):
    c, _ = client
    assert c.get("/missing", follow_redirects=False).status_code == 404
    assert c.get("/stats/missing").status_code == 404
