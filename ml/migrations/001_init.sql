CREATE TABLE IF NOT EXISTS customers (
    customer_id             SERIAL PRIMARY KEY,
    email                   TEXT NOT NULL,
    balance_eur             NUMERIC NOT NULL DEFAULT 0,
    total_replenished_eur   NUMERIC NOT NULL DEFAULT 0,
    risk_score              NUMERIC,
    risk_level              TEXT,
    reasons                 jsonb
);

CREATE TABLE IF NOT EXISTS model_weights (
    feature_name TEXT PRIMARY KEY,
    weight NUMERIC NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);