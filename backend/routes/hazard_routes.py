"""Hazard reporting and mitigation route handlers."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

hazard_bp = Blueprint("hazards", __name__, url_prefix="/api/hazards")


@hazard_bp.route("", methods=["GET"])
@jwt_required()
def list_hazards():
    """List hazards with optional filters and pagination."""
    mine_id = request.args.get("mine_id")
    severity = request.args.get("severity")
    status = request.args.get("status")
    hazard_type = request.args.get("hazard_type")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("h.mine_id = ?")
        args.append(mine_id)
    if severity:
        where_clauses.append("h.severity = ?")
        args.append(severity)
    if status:
        where_clauses.append("h.status = ?")
        args.append(status)
    if hazard_type:
        where_clauses.append("h.hazard_type = ?")
        args.append(hazard_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = query_db(f"SELECT COUNT(*) AS total FROM hazards h {where_sql}", args, one=True)["total"]

    data_sql = f"""
        SELECT h.*, m.name as mine_name, s.name as section_name, u.full_name as reported_by_name
        FROM hazards h
        JOIN mines m ON h.mine_id = m.id
        LEFT JOIN sections s ON h.section_id = s.id
        JOIN users u ON h.reported_by = u.id
        {where_sql}
        ORDER BY 
            CASE h.severity 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'medium' THEN 3 
                ELSE 4 
            END,
            h.reported_date DESC, h.id DESC
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
        "message": "Hazards retrieved"
    }), 200


@hazard_bp.route("/<int:hazard_id>", methods=["GET"])
@jwt_required()
def get_hazard(hazard_id):
    """Retrieve details of a single hazard report."""
    hazard = query_db(
        """
        SELECT h.*, m.name as mine_name, s.name as section_name, u.full_name as reported_by_name, u.email as reporter_email
        FROM hazards h
        JOIN mines m ON h.mine_id = m.id
        LEFT JOIN sections s ON h.section_id = s.id
        JOIN users u ON h.reported_by = u.id
        WHERE h.id = ?
        """,
        (hazard_id,),
        one=True,
    )
    if not hazard:
        return jsonify({"success": False, "data": None, "message": "Hazard not found"}), 404

    return jsonify({"success": True, "data": dict(hazard), "message": "Hazard details retrieved"}), 200


@hazard_bp.route("", methods=["POST"])
@jwt_required()
def create_hazard():
    """Report a newly identified physical, atmospheric, or mechanical hazard."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    section_id = data.get("section_id")
    hazard_type = data.get("hazard_type", "").strip()
    description = data.get("description", "").strip()
    severity = data.get("severity", "medium").lower()
    location_detail = data.get("location_detail", "").strip()
    reported_date = data.get("reported_date") or datetime.utcnow().date().isoformat()
    reported_by = int(get_jwt_identity())

    if not mine_id or not hazard_type or not description:
        return jsonify({"success": False, "data": None, "message": "Mine, hazard type, and description required"}), 400

    if severity not in ("low", "medium", "high", "critical"):
        return jsonify({"success": False, "data": None, "message": "Severity must be low, medium, high, or critical"}), 400

    now_iso = datetime.utcnow().isoformat() + "Z"
    hazard_id = execute_db(
        """
        INSERT INTO hazards (mine_id, section_id, reported_by, hazard_type, description, severity, location_detail, status, reported_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'reported', ?, ?)
        """,
        (mine_id, section_id, reported_by, hazard_type, description, severity, location_detail, reported_date, now_iso),
    )

    log_action(user_id=reported_by, action="CREATE", entity_type="hazard", entity_id=hazard_id, new_values=data)

    return jsonify({"success": True, "data": {"id": hazard_id}, "message": "Hazard reported successfully"}), 201


@hazard_bp.route("/<int:hazard_id>", methods=["PUT"])
@jwt_required()
def update_hazard(hazard_id):
    """Update hazard report details."""
    existing = query_db("SELECT * FROM hazards WHERE id = ?", (hazard_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Hazard not found"}), 404

    data = request.get_json(silent=True) or {}
    hazard_type = data.get("hazard_type", existing["hazard_type"])
    description = data.get("description", existing["description"])
    severity = data.get("severity", existing["severity"])
    location_detail = data.get("location_detail", existing["location_detail"])
    status = data.get("status", existing["status"])
    resolved_date = data.get("resolved_date", existing["resolved_date"])

    execute_db(
        """
        UPDATE hazards
        SET hazard_type = ?, description = ?, severity = ?, location_detail = ?, status = ?, resolved_date = ?
        WHERE id = ?
        """,
        (hazard_type, description, severity, location_detail, status, resolved_date, hazard_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="hazard", entity_id=hazard_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": hazard_id}, "message": "Hazard updated successfully"}), 200


@hazard_bp.route("/<int:hazard_id>/status", methods=["PATCH", "PUT"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def update_hazard_status(hazard_id):
    """Update the lifecycle status of a hazard (reported -> under_review -> mitigated -> closed)."""
    existing = query_db("SELECT * FROM hazards WHERE id = ?", (hazard_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Hazard not found"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "").lower()
    if new_status not in ("reported", "under_review", "mitigated", "closed"):
        return jsonify({"success": False, "data": None, "message": "Invalid hazard status"}), 400

    resolved_date = existing["resolved_date"]
    if new_status in ("mitigated", "closed") and not resolved_date:
        resolved_date = datetime.utcnow().date().isoformat()

    execute_db(
        "UPDATE hazards SET status = ?, resolved_date = ? WHERE id = ?",
        (new_status, resolved_date, hazard_id),
    )

    user_id = int(get_jwt_identity())
    log_action(
        user_id=user_id,
        action="UPDATE_STATUS",
        entity_type="hazard",
        entity_id=hazard_id,
        old_values={"status": existing["status"]},
        new_values={"status": new_status, "resolved_date": resolved_date},
    )

    return jsonify({"success": True, "data": {"id": hazard_id, "status": new_status}, "message": "Status updated successfully"}), 200
