import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/lab_state.db")

def init_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS port_baselines (
            host TEXT,
            port INTEGER,
            banner TEXT,
            first_seen TEXT,
            last_seen TEXT,
            PRIMARY KEY (host, port)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threat_iocs (
            indicator TEXT PRIMARY KEY,
            source TEXT,
            category TEXT,
            added_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cloud_findings (
            finding_id TEXT PRIMARY KEY,
            resource_file TEXT,
            severity TEXT,
            benchmark TEXT,
            description TEXT,
            detected_at TEXT
        )
    """)
    conn.commit()
    return conn

def record_and_diff_port(conn: sqlite3.Connection, host: str, port: int, banner: str) -> str:
    now = datetime.now(timezone.utc).isoformat()
    row = conn.execute(
        "SELECT banner FROM port_baselines WHERE host = ? AND port = ?",
        (host, port)
    ).fetchone()

    if row is None:
        conn.execute(
            "INSERT INTO port_baselines (host, port, banner, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
            (host, port, banner, now, now)
        )
        conn.commit()
        return f"[NEW PORT] {host}:{port} opened | Banner: {banner}"

    old_banner = row[0]
    conn.execute(
        "UPDATE port_baselines SET banner = ?, last_seen = ? WHERE host = ? AND port = ?",
        (banner, now, host, port)
    )
    conn.commit()

    if old_banner != banner:
        return f"[BANNER DRIFT] {host}:{port} changed from '{old_banner}' -> '{banner}'"
    return f"[UNCHANGED] {host}:{port} ({banner})"

def save_cloud_finding(conn: sqlite3.Connection, finding_id: str, resource_file: str, severity: str, benchmark: str, description: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO cloud_findings (finding_id, resource_file, severity, benchmark, description, detected_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(finding_id) DO UPDATE SET
            severity = excluded.severity,
            description = excluded.description,
            detected_at = excluded.detected_at
        """,
        (finding_id, resource_file, severity, benchmark, description, now)
    )
    conn.commit()
