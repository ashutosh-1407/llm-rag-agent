import sqlite3
from pathlib import Path


DB_PATH = Path("metrics.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_metrics_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT NOT NULL,
            client_ip TEXT,
            latency_ms REAL,
            status TEXT,
            route TEXT,
            tool TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_request_metrics(
    endpoint: str,
    client_ip: str,
    latency_ms: float,
    status: str,
    route: str | None,
    tool: str | None
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO request_metrics (
            endpoint, client_ip, latency_ms, status, route, tool
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (endpoint, client_ip, latency_ms, status, route, tool))
    conn.commit()
    conn.close()
