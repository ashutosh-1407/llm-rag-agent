import sqlite3
from pathlib import Path

DB_PATH = Path("metrics.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def _percentile(values, pct):
    if not values:
        return None
    values = sorted(values)
    idx = int((pct / 100) * (len(values) - 1))
    return round(values[idx], 2)

def get_metrics_summary():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM request_metrics")
    total_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM request_metrics where status = 'success'")
    success_requests = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM request_metrics where status = 'error'")
    error_requests = cur.fetchone()[0]

    cur.execute("SELECT latency_ms FROM request_metrics")
    latencies = [row[0] for row in cur.fetchall()]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None
    p95_latency = _percentile(latencies, 95)

    cur.execute("""
        SELECT route, COUNT(*)
        FROM request_metrics
        WHERE route IS NOT NULL
        GROUP BY route
    """)
    routes = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("""
        SELECT tool, COUNT(*)
        FROM request_metrics
        WHERE tool IS NOT NULL
        GROUP BY tool
    """)
    tools = {row[0]: row[1] for row in cur.fetchall()}

    success_rate = (success_requests / total_requests) if total_requests else 0.0
    error_rate = (error_requests / total_requests) if total_requests else 0.0

    return {
        "requests": {
            "total": total_requests,
            "success": success_requests,
            "error": error_requests
        },
        "latency_ms": {
            "avg": avg_latency,
            "p95": p95_latency,
            "count": len(latencies)

        },
        "routes": routes,
        "tools": tools,
        "rates": {
            "success_rate": success_rate,
            "error_rate": error_rate
        }
    }
