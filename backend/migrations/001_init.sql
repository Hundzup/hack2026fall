CREATE TABLE IF NOT EXISTS items (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    value      NUMERIC NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO items (name, value) VALUES
    ('alpha', 10.5),
    ('beta',  20.0),
    ('gamma', 7.25)
ON CONFLICT DO NOTHING;