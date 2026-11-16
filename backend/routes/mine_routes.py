"""Mine and Section management route handlers."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

mine_bp = Blueprint("mines", __name__, url_prefix="/api/mines")


@mine_bp.route("", methods=["GET"])
@jwt_required()
def list_mines():
    """Retrieve list of all registered coal mines."""
    status = request.args.get("status")
    mine_type = request.args.get("type")

    query = """
        SELECT m.id, m.name, m.type, m.location, m.state, m.district, 
               m.license_number, m.owner_company, m.status, m.created_at,
               COUNT(DISTINCT s.id) AS section_count,
               COUNT(DISTINCT CASE WHEN h.status IN ('reported', 'under_review') THEN h.id END) AS active_hazards_count,
               COUNT(DISTINCT CASE WHEN ca.status IN ('open', 'acknowledged', 'escalated') THEN ca.id END) AS active_alerts_count
        FROM mines m
        LEFT JOIN sections s ON m.id = s.mine_id
        LEFT JOIN hazards h ON m.id = h.mine_id
        LEFT JOIN compliance_alerts ca ON m.id = ca.mine_id
        WHERE 1=1
    """
    args = []
    if status:
        query += " AND m.status = ?"
        args.append(status)
    if mine_type:
        query += " AND m.type = ?"
        args.append(mine_type)

    query += " GROUP BY m.id ORDER BY m.name ASC"
    mines = query_db(query, args)
    return jsonify({"success": True, "data": mines, "message": "Mines retrieved successfully"}), 200


@mine_bp.route("/<int:mine_id>", methods=["GET"])
@jwt_required()
def get_mine(mine_id):
    """Retrieve detailed information for a specific mine including sections."""
    mine = query_db("SELECT * FROM mines WHERE id = ?", (mine_id,), one=True)
    if not mine:
        return jsonify({"success": False, "data": None, "message": "Mine not found"}), 404

    sections = query_db("SELECT * FROM sections WHERE mine_id = ? ORDER BY name ASC", (mine_id,))
    res = dict(mine)
    res["sections"] = sections
    return jsonify({"success": True, "data": res, "message": "Mine details retrieved"}), 200


@mine_bp.route("", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def create_mine():
    """Register a new coal mine (Admin only)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    mine_type = data.get("type", "").strip().lower()
    location = data.get("location", "").strip()
    state = data.get("state", "").strip()
    district = data.get("district", "").strip()
    license_number = data.get("license_number", "").strip()
    owner_company = data.get("owner_company", "").strip()
    status = data.get("status", "active")

    if not name or not mine_type or not license_number:
        return jsonify({"success": False, "data": None, "message": "Name, type, and license_number required"}), 400

    if mine_type not in ("underground", "opencast"):
        return jsonify({"success": False, "data": None, "message": "Type must be underground or opencast"}), 400

    existing = query_db("SELECT id FROM mines WHERE license_number = ?", (license_number,), one=True)
    if existing:
        return jsonify({"success": False, "data": None, "message": "License number already exists"}), 409

    now_iso = datetime.utcnow().isoformat() + "Z"
    mine_id = execute_db(
        """
        INSERT INTO mines (name, type, location, state, district, license_number, owner_company, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, mine_type, location, state, district, license_number, owner_company, status, now_iso),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="CREATE", entity_type="mine", entity_id=mine_id, new_values=data)

    return jsonify({"success": True, "data": {"id": mine_id, "name": name}, "message": "Mine registered successfully"}), 201


@mine_bp.route("/<int:mine_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "mine_manager"])
def update_mine(mine_id):
    """Update mine attributes."""
    existing = query_db("SELECT * FROM mines WHERE id = ?", (mine_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Mine not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name", existing["name"]).strip()
    mine_type = data.get("type", existing["type"]).strip().lower()
    location = data.get("location", existing["location"]).strip()
    state = data.get("state", existing["state"]).strip()
    district = data.get("district", existing["district"]).strip()
    owner_company = data.get("owner_company", existing["owner_company"]).strip()
    status = data.get("status", existing["status"])

    execute_db(
        """
        UPDATE mines 
        SET name = ?, type = ?, location = ?, state = ?, district = ?, owner_company = ?, status = ?
        WHERE id = ?
        """,
        (name, mine_type, location, state, district, owner_company, status, mine_id),
    )

    user_id = int(get_jwt_identity())
    log_action(
        user_id=user_id,
        action="UPDATE",
        entity_type="mine",
        entity_id=mine_id,
        old_values=dict(existing),
        new_values=data,
    )

    return jsonify({"success": True, "data": {"id": mine_id, "name": name}, "message": "Mine updated successfully"}), 200


@mine_bp.route("/<int:mine_id>/sections", methods=["GET"])
@jwt_required()
def list_sections(mine_id):
    """List sections for a given mine."""
    sections = query_db("SELECT * FROM sections WHERE mine_id = ? ORDER BY name ASC", (mine_id,))
    return jsonify({"success": True, "data": sections, "message": "Sections retrieved"}), 200


@mine_bp.route("/<int:mine_id>/sections", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager"])
def create_section(mine_id):
    """Add a new extraction/ventilation section to a mine."""
    mine = query_db("SELECT id FROM mines WHERE id = ?", (mine_id,), one=True)
    if not mine:
        return jsonify({"success": False, "data": None, "message": "Mine not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    section_type = data.get("type", "").strip()
    depth_meters = data.get("depth_meters")
    status = data.get("status", "active")

    if not name or not section_type:
        return jsonify({"success": False, "data": None, "message": "Section name and type required"}), 400

    now_iso = datetime.utcnow().isoformat() + "Z"
    sec_id = execute_db(
        """
        INSERT INTO sections (mine_id, name, type, depth_meters, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (mine_id, name, section_type, depth_meters, status, now_iso),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="CREATE", entity_type="section", entity_id=sec_id, new_values=data)

    return jsonify({"success": True, "data": {"id": sec_id, "name": name}, "message": "Section created successfully"}), 201


@mine_bp.route("/<int:mine_id>/dashboard", methods=["GET"])
@mine_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard_stats(mine_id=None):
    """Retrieve summary KPIs, alerts, inspections, and hazard trends for dashboard."""
    mine_filter = "WHERE mine_id = ?" if mine_id else ""
    args = [mine_id] if mine_id else []

    # Counts
    total_mines = query_db("SELECT COUNT(*) AS count FROM mines WHERE status = 'active'", one=True)["count"]
    total_inspections = query_db(f"SELECT COUNT(*) AS count FROM inspections {mine_filter}", args, one=True)["count"]
    active_hazards = query_db(
        f"SELECT COUNT(*) AS count FROM hazards WHERE status IN ('reported', 'under_review') {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]
    open_alerts = query_db(
        f"SELECT COUNT(*) AS count FROM compliance_alerts WHERE status IN ('open', 'acknowledged', 'escalated') {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]
    total_incidents = query_db(f"SELECT COUNT(*) AS count FROM incidents {mine_filter}", args, one=True)["count"]

    # Recent alerts
    recent_alerts = query_db(
        f"""
        SELECT ca.*, cr.rule_code, cr.category, m.name as mine_name
        FROM compliance_alerts ca
        JOIN compliance_rules cr ON ca.rule_id = cr.id
        JOIN mines m ON ca.mine_id = m.id
        {'WHERE ca.mine_id = ?' if mine_id else ''}
        ORDER BY ca.created_at DESC LIMIT 5
        """,
        args
    )

    # Upcoming inspections
    upcoming_inspections = query_db(
        f"""
        SELECT i.*, m.name as mine_name, s.name as section_name, u.full_name as inspector_name
        FROM inspections i
        JOIN mines m ON i.mine_id = m.id
        LEFT JOIN sections s ON i.section_id = s.id
        JOIN users u ON i.inspector_id = u.id
        WHERE i.status IN ('scheduled', 'in_progress') {'AND i.mine_id = ?' if mine_id else ''}
        ORDER BY i.scheduled_date ASC LIMIT 5
        """,
        args
    )

    # Compliance by category
    compliance_by_category = query_db(
        """
        SELECT cr.category, 
               COUNT(ca.id) as total_alerts,
               SUM(CASE WHEN ca.status = 'resolved' THEN 1 ELSE 0 END) as resolved_alerts
        FROM compliance_rules cr
        LEFT JOIN compliance_alerts ca ON cr.id = ca.rule_id
        GROUP BY cr.category
        """
    )

    return jsonify({
        "success": True,
        "data": {
            "total_mines": total_mines,
            "total_inspections": total_inspections,
            "active_hazards": active_hazards,
            "open_alerts": open_alerts,
            "total_incidents": total_incidents,
            "recent_alerts": recent_alerts,
            "upcoming_inspections": upcoming_inspections,
            "compliance_by_category": compliance_by_category,
        },
        "message": "Dashboard statistics retrieved"
    }), 200
