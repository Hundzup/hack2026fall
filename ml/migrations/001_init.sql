CREATE TABLE IF NOT EXISTS customers (
    id                      SERIAL PRIMARY KEY,
    email                   TEXT NOT NULL,
    balance_eur             NUMERIC NOT NULL DEFAULT 0,
    total_replenished_eur   NUMERIC NOT NULL DEFAULT 0,
    risk_score              NUMERIC,
    risk_level              TEXT,
    reasons                 jsonb
);
