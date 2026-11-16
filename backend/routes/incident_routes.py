"""Incident and dangerous occurrence reporting and investigation routes."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

incident_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")


@incident_bp.route("", methods=["GET"])
@jwt_required()
def list_incidents():
    """List mine incidents with optional filtering and pagination."""
    mine_id = request.args.get("mine_id")
    severity = request.args.get("severity")
    status = request.args.get("status")
    incident_type = request.args.get("incident_type")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("inc.mine_id = ?")
        args.append(mine_id)
    if severity:
        where_clauses.append("inc.severity = ?")
        args.append(severity)
    if status:
        where_clauses.append("inc.status = ?")
        args.append(status)
    if incident_type:
        where_clauses.append("inc.incident_type = ?")
        args.append(incident_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = query_db(f"SELECT COUNT(*) AS total FROM incidents inc {where_sql}", args, one=True)["total"]

    data_sql = f"""
        SELECT inc.*, m.name as mine_name, s.name as section_name, u.full_name as reported_by_name
        FROM incidents inc
        JOIN mines m ON inc.mine_id = m.id
        LEFT JOIN sections s ON inc.section_id = s.id
        JOIN users u ON inc.reported_by = u.id
        {where_sql}
        ORDER BY inc.date_occurred DESC, inc.id DESC
        LIMIT ? OFFSET ?
    """
    items = query_db(data_sql, args + [per_page, offset])

    return jsonify({
        "success": True,
        "data": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
        "message": "Incidents retrieved"
    }), 200


@incident_bp.route("/<int:incident_id>", methods=["GET"])
@jwt_required()
def get_incident(incident_id):
    """Retrieve details of a single incident."""
    incident = query_db(
        """
        SELECT inc.*, m.name as mine_name, s.name as section_name, u.full_name as reported_by_name
        FROM incidents inc
        JOIN mines m ON inc.mine_id = m.id
        LEFT JOIN sections s ON inc.section_id = s.id
        JOIN users u ON inc.reported_by = u.id
        WHERE inc.id = ?
        """,
        (incident_id,),
        one=True,
    )
    if not incident:
        return jsonify({"success": False, "data": None, "message": "Incident not found"}), 404

    return jsonify({"success": True, "data": dict(incident), "message": "Incident details retrieved"}), 200


@incident_bp.route("", methods=["POST"])
@jwt_required()
def create_incident():
    """Report a new mining incident or dangerous occurrence."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    section_id = data.get("section_id")
    incident_type = data.get("incident_type", "").strip()
    description = data.get("description", "").strip()
    severity = data.get("severity", "medium").lower()
    casualties = int(data.get("casualties", 0))
    injuries = int(data.get("injuries", 0))
    date_occurred = data.get("date_occurred") or datetime.utcnow().date().isoformat()
    date_reported = data.get("date_reported") or datetime.utcnow().date().isoformat()
    root_cause = data.get("root_cause")
    reported_by = int(get_jwt_identity())

    if not mine_id or not incident_type or not description:
        return jsonify({"success": False, "data": None, "message": "Mine, incident type, and description required"}), 400

    now_iso = datetime.utcnow().isoformat() + "Z"
    inc_id = execute_db(
        """
        INSERT INTO incidents (
            mine_id, section_id, reported_by, incident_type, description, severity, 
            casualties, injuries, date_occurred, date_reported, root_cause, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'reported', ?)
        """,
        (mine_id, section_id, reported_by, incident_type, description, severity, casualties, injuries, date_occurred, date_reported, root_cause, now_iso),
    )

    log_action(user_id=reported_by, action="CREATE", entity_type="incident", entity_id=inc_id, new_values=data)

    return jsonify({"success": True, "data": {"id": inc_id}, "message": "Incident recorded successfully"}), 201


@incident_bp.route("/<int:incident_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer", "inspector"])
def update_incident(incident_id):
    """Update incident investigation details (root cause, casualties, status)."""
    existing = query_db("SELECT * FROM incidents WHERE id = ?", (incident_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Incident not found"}), 404

    data = request.get_json(silent=True) or {}
    incident_type = data.get("incident_type", existing["incident_type"])
    description = data.get("description", existing["description"])
    severity = data.get("severity", existing["severity"])
    casualties = int(data.get("casualties", existing["casualties"]))
    injuries = int(data.get("injuries", existing["injuries"]))
    root_cause = data.get("root_cause", existing["root_cause"])
    status = data.get("status", existing["status"])

    execute_db(
        """
        UPDATE incidents
        SET incident_type = ?, description = ?, severity = ?, casualties = ?, 
            injuries = ?, root_cause = ?, status = ?
        WHERE id = ?
        """,
        (incident_type, description, severity, casualties, injuries, root_cause, status, incident_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="incident", entity_id=incident_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": incident_id}, "message": "Incident updated successfully"}), 200
