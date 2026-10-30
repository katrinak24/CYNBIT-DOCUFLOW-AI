import json
import sqlite3
from datetime import datetime, timezone
import hashlib
from config import DATABASE_DIR, DATABASE_PATH
from core.schemas import InvoiceData
from core.verification_summary import build_verification_summary, normalize_verification

VALID_STATUSES = {"Pending Review", "Approved", "Rejected"}

def connect():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            vendor_name TEXT,
            invoice_number TEXT,
            total_amount REAL,
            status TEXT NOT NULL DEFAULT 'Pending Review',
            extracted_json TEXT NOT NULL,
            issues_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            source_text TEXT NOT NULL DEFAULT ''
        )
        """)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(invoices)").fetchall()}
        if "source_text" not in columns:
            conn.execute("ALTER TABLE invoices ADD COLUMN source_text TEXT NOT NULL DEFAULT ''")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS verification_audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            source_filename TEXT NOT NULL,
            original_workflow_status TEXT NOT NULL,
            previous_verification_json TEXT NOT NULL,
            new_verification_json TEXT NOT NULL,
            source_text_sha256 TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
        """)

def find_duplicate(vendor_name, invoice_number):
    if not vendor_name or not invoice_number:
        return None
    with connect() as conn:
        row = conn.execute(
            """SELECT id, filename, status, total_amount, created_at
               FROM invoices
               WHERE lower(trim(vendor_name))=lower(trim(?))
                 AND lower(trim(invoice_number))=lower(trim(?))
               ORDER BY id DESC LIMIT 1""",
            (vendor_name, invoice_number)
        ).fetchone()
    return dict(row) if row else None

def is_duplicate(vendor_name, invoice_number):
    return find_duplicate(vendor_name, invoice_number) is not None

def save_invoice(filename: str, data: InvoiceData, issues: list[dict], status="Pending Review", source_text: str = ""):
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported invoice status: {status}")
    with connect() as conn:
        cur = conn.execute("""
        INSERT INTO invoices
        (filename, vendor_name, invoice_number, total_amount, status, extracted_json, issues_json, created_at, source_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, data.vendor_name, data.invoice_number, data.total_amount, status,
            data.model_dump_json(), json.dumps(issues),
            datetime.now(timezone.utc).isoformat(), source_text
        ))
        return cur.lastrowid

def update_invoice_review(record_id: int, data: InvoiceData, issues: list[dict], status: str):
    """Atomically persist reviewer corrections and the matching workflow status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported invoice status: {status}")
    with connect() as conn:
        cur = conn.execute("""
            UPDATE invoices
               SET vendor_name=?, invoice_number=?, total_amount=?, status=?,
                   extracted_json=?, issues_json=?
             WHERE id=?
        """, (
            data.vendor_name, data.invoice_number, data.total_amount, status,
            data.model_dump_json(), json.dumps(issues), record_id
        ))
        if cur.rowcount != 1:
            raise ValueError(f"Invoice record #{record_id} was not found.")

def get_invoice_source(record_id: int) -> str:
    with connect() as conn:
        row = conn.execute("SELECT source_text FROM invoices WHERE id=?", (record_id,)).fetchone()
    if row is None:
        raise ValueError(f"Invoice record #{record_id} was not found.")
    return row["source_text"] or ""

def update_status(record_id: int, status: str):
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported invoice status: {status}")
    with connect() as conn:
        cur = conn.execute("UPDATE invoices SET status=? WHERE id=?", (status, record_id))
        if cur.rowcount != 1:
            raise ValueError(f"Invoice record #{record_id} was not found.")

def list_invoices():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def update_invoice_evidence(record_id: int, verified_data: InvoiceData, source_text: str,
                            source_filename: str) -> dict:
    """Update only verification metadata; preserve invoice values and approval status.

    The old/new evidence state is written to an append-only audit table in the
    same SQLite transaction as the metadata update.
    """
    now = datetime.now(timezone.utc).isoformat()
    new_statuses = normalize_verification(verified_data.field_verification)
    new_summary = build_verification_summary(new_statuses)
    new_evidence = {
        "field_confidence": verified_data.field_confidence,
        "field_evidence": verified_data.field_evidence,
        "field_verification": new_statuses,
        "verification_summary": new_summary,
    }
    source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    with connect() as conn:
        row = conn.execute(
            "SELECT extracted_json, status FROM invoices WHERE id=?", (record_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Invoice record #{record_id} was not found.")
        extracted = json.loads(row["extracted_json"])
        previous = {
            key: extracted.get(key, {})
            for key in ("field_confidence", "field_evidence", "field_verification", "verification_summary")
        }
        # Only evidence metadata is refreshed. Business fields and workflow status stay untouched.
        extracted.update(new_evidence)
        conn.execute(
            "UPDATE invoices SET extracted_json=?, source_text=? WHERE id=?",
            (json.dumps(extracted, ensure_ascii=False), source_text, record_id)
        )
        cur = conn.execute("""
            INSERT INTO verification_audit
            (invoice_id, source_filename, original_workflow_status,
             previous_verification_json, new_verification_json, source_text_sha256, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record_id, source_filename, row["status"],
            json.dumps(previous, ensure_ascii=False),
            json.dumps(new_evidence, ensure_ascii=False), source_hash, now
        ))
        return {"audit_id": cur.lastrowid, "workflow_status": row["status"],
                "verification_summary": new_summary, "created_at": now}


def list_verification_audit(record_id: int | None = None) -> list[dict]:
    with connect() as conn:
        if record_id is None:
            rows = conn.execute(
                "SELECT * FROM verification_audit ORDER BY audit_id DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM verification_audit WHERE invoice_id=? ORDER BY audit_id DESC",
                (record_id,)
            ).fetchall()
    return [dict(row) for row in rows]
