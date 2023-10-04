-- create_schema.sql
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    timestamp DATETIME,
    cpu_percent REAL,
    memory_usage_bytes REAL
);
