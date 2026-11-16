"""Inspection management and execution route handlers."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

inspection_bp = Blueprint("inspections", __name__, url_prefix="/api/inspections")


@inspection_bp.route("", methods=["GET"])
@jwt_required()
def list_inspections():
    """List inspections with optional filtering and pagination."""
    mine_id = request.args.get("mine_id")
    status = request.args.get("status")
    insp_type = request.args.get("type")
    risk_level = request.args.get("risk_level")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("i.mine_id = ?")
        args.append(mine_id)
    if status:
        where_clauses.append("i.status = ?")
        args.append(status)
    if insp_type:
        where_clauses.append("i.type = ?")
        args.append(insp_type)
    if risk_level:
        where_clauses.append("i.risk_level = ?")
        args.append(risk_level)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Total count
    count_sql = f"SELECT COUNT(*) AS total FROM inspections i {where_sql}"
    total = query_db(count_sql, args, one=True)["total"]

    # Data
    data_sql = f"""
        SELECT i.*, m.name as mine_name, s.name as section_name, u.full_name as inspector_name
        FROM inspections i
        JOIN mines m ON i.mine_id = m.id
        LEFT JOIN sections s ON i.section_id = s.id
        JOIN users u ON i.inspector_id = u.id
        {where_sql}
        ORDER BY i.scheduled_date DESC, i.id DESC
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
        "message": "Inspections retrieved"
    }), 200


@inspection_bp.route("/<int:inspection_id>", methods=["GET"])
@jwt_required()
def get_inspection(inspection_id):
    """Retrieve details of a single inspection."""
    insp = query_db(
        """
        SELECT i.*, m.name as mine_name, s.name as section_name, u.full_name as inspector_name, u.email as inspector_email
        FROM inspections i
        JOIN mines m ON i.mine_id = m.id
        LEFT JOIN sections s ON i.section_id = s.id
        JOIN users u ON i.inspector_id = u.id
        WHERE i.id = ?
        """,
        (inspection_id,),
        one=True,
    )
    if not insp:
        return jsonify({"success": False, "data": None, "message": "Inspection not found"}), 404

    return jsonify({"success": True, "data": dict(insp), "message": "Inspection details retrieved"}), 200


@inspection_bp.route("", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer", "inspector"])
def create_inspection():
    """Schedule a new mine inspection."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    section_id = data.get("section_id")
    inspector_id = data.get("inspector_id") or int(get_jwt_identity())
    insp_type = data.get("type", "safety_audit")
    scheduled_date = data.get("scheduled_date")

    if not mine_id or not scheduled_date or not insp_type:
        return jsonify({"success": False, "data": None, "message": "Mine, scheduled date, and type are required"}), 400

    now_iso = datetime.utcnow().isoformat() + "Z"
    insp_id = execute_db(
        """
        INSERT INTO inspections (mine_id, section_id, inspector_id, type, scheduled_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'scheduled', ?)
        """,
        (mine_id, section_id, inspector_id, insp_type, scheduled_date, now_iso),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="CREATE", entity_type="inspection", entity_id=insp_id, new_values=data)

    return jsonify({"success": True, "data": {"id": insp_id}, "message": "Inspection scheduled successfully"}), 201


@inspection_bp.route("/<int:inspection_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer", "inspector"])
def update_inspection(inspection_id):
    """Update inspection details."""
    existing = query_db("SELECT * FROM inspections WHERE id = ?", (inspection_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Inspection not found"}), 404

    data = request.get_json(silent=True) or {}
    section_id = data.get("section_id", existing["section_id"])
    inspector_id = data.get("inspector_id", existing["inspector_id"])
    insp_type = data.get("type", existing["type"])
    scheduled_date = data.get("scheduled_date", existing["scheduled_date"])
    status = data.get("status", existing["status"])
    findings = data.get("findings", existing["findings"])
    risk_level = data.get("risk_level", existing["risk_level"])
    evidence_attached = data.get("evidence_attached", existing["evidence_attached"])

    now_iso = datetime.utcnow().isoformat() + "Z"
    execute_db(
        """
        UPDATE inspections 
        SET section_id = ?, inspector_id = ?, type = ?, scheduled_date = ?, 
            status = ?, findings = ?, risk_level = ?, evidence_attached = ?, updated_at = ?
        WHERE id = ?
        """,
        (section_id, inspector_id, insp_type, scheduled_date, status, findings, risk_level, evidence_attached, now_iso, inspection_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="inspection", entity_id=inspection_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": inspection_id}, "message": "Inspection updated successfully"}), 200


@inspection_bp.route("/<int:inspection_id>/complete", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer", "inspector"])
def complete_inspection(inspection_id):
    """Submit findings and mark inspection as completed."""
    existing = query_db("SELECT * FROM inspections WHERE id = ?", (inspection_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Inspection not found"}), 404

    data = request.get_json(silent=True) or {}
    findings = data.get("findings", "").strip()
    risk_level = data.get("risk_level", "low")
    evidence_attached = 1 if data.get("evidence_attached") else 0
    completed_date = data.get("completed_date") or datetime.utcnow().date().isoformat()
    now_iso = datetime.utcnow().isoformat() + "Z"

    if not findings:
        return jsonify({"success": False, "data": None, "message": "Findings documentation required to complete inspection"}), 400

    execute_db(
        """
        UPDATE inspections
        SET status = 'completed', completed_date = ?, findings = ?, risk_level = ?, 
            evidence_attached = ?, updated_at = ?
        WHERE id = ?
        """,
        (completed_date, findings, risk_level, evidence_attached, now_iso, inspection_id),
    )

    user_id = int(get_jwt_identity())
    log_action(
        user_id=user_id,
        action="COMPLETE",
        entity_type="inspection",
        entity_id=inspection_id,
        old_values={"status": existing["status"]},
        new_values={"status": "completed", "risk_level": risk_level, "findings": findings},
    )

    return jsonify({"success": True, "data": {"id": inspection_id, "status": "completed"}, "message": "Inspection completed successfully"}), 200
