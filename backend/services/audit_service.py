"""Audit logging service for tracking administrative and compliance actions."""

import json
from datetime import datetime
from flask import request, has_request_context
from database.db import query_db, execute_db


def log_action(
    user_id,
    action: str,
    entity_type: str,
    entity_id: int = None,
    old_values=None,
    new_values=None,
    ip_address: str = None,
):
    """Record an audit trail event in the database."""
    if not ip_address and has_request_context():
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    old_str = (
        json.dumps(old_values, default=str)
        if isinstance(old_values, (dict, list))
        else old_values
    )
    new_str = (
        json.dumps(new_values, default=str)
        if isinstance(new_values, (dict, list))
        else new_values
    )

    query = """
        INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, new_values, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    now_iso = datetime.utcnow().isoformat() + "Z"
    return execute_db(
        query,
        (
            user_id,
            action.upper(),
            entity_type,
            entity_id,
            old_str,
            new_str,
            ip_address,
            now_iso,
        ),
    )


def get_audit_log(page: int = 1, per_page: int = 20, filters: dict = None):
    """Retrieve paginated audit log entries with optional filters."""
    page = max(1, int(page))
    per_page = max(1, min(100, int(per_page)))
    offset = (page - 1) * per_page
    filters = filters or {}

    where_clauses = []
    args = []

    if filters.get("user_id"):
        where_clauses.append("a.user_id = ?")
        args.append(filters["user_id"])

    if filters.get("entity_type"):
        where_clauses.append("a.entity_type = ?")
        args.append(filters["entity_type"])

    if filters.get("action"):
        where_clauses.append("a.action = ?")
        args.append(filters["action"].upper())

    if filters.get("start_date"):
        where_clauses.append("a.timestamp >= ?")
        args.append(filters["start_date"])

    if filters.get("end_date"):
        where_clauses.append("a.timestamp <= ?")
        args.append(filters["end_date"])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Count total
    count_sql = f"SELECT COUNT(*) AS total FROM audit_log a {where_sql}"
    total_row = query_db(count_sql, args, one=True)
    total = total_row["total"] if total_row else 0

    # Retrieve rows
    data_sql = f"""
        SELECT 
            a.id, a.user_id, a.action, a.entity_type, a.entity_id,
            a.old_values, a.new_values, a.ip_address, a.timestamp,
            u.username, u.full_name, u.role
        FROM audit_log a
        LEFT JOIN users u ON a.user_id = u.id
        {where_sql}
        ORDER BY a.timestamp DESC, a.id DESC
        LIMIT ? OFFSET ?
    """
    rows = query_db(data_sql, args + [per_page, offset])

    # Parse JSON values if possible
    parsed_rows = []
    for r in rows:
        row_dict = dict(r)
        for key in ("old_values", "new_values"):
            if row_dict[key]:
                try:
                    row_dict[key] = json.loads(row_dict[key])
                except (ValueError, TypeError):
                    pass
        parsed_rows.append(row_dict)

    return {
        "items": parsed_rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
    }
