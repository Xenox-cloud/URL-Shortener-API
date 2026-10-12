-- URL Shortener schema (PostgreSQL)
CREATE TABLE IF NOT EXISTS urls (
    id           BIGSERIAL PRIMARY KEY,
    original_url TEXT        NOT NULL,
    short_code   VARCHAR(10) NOT NULL,
    clicks       INTEGER     NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- For databases created before created_at existed
ALTER TABLE urls ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Every redirect and stats lookup filters on short_code, so it gets a unique B-tree index.
-- The UNIQUE constraint also guarantees no two URLs share a code.
CREATE UNIQUE INDEX IF NOT EXISTS idx_urls_short_code ON urls (short_code);
