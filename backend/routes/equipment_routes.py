"""Equipment registry and maintenance activity routes."""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

equipment_bp = Blueprint("equipment", __name__, url_prefix="/api/equipment")


@equipment_bp.route("", methods=["GET"])
@jwt_required()
def list_equipment():
    """List equipment inventory with filters and pagination."""
    mine_id = request.args.get("mine_id")
    status = request.args.get("status")
    eq_type = request.args.get("type")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("e.mine_id = ?")
        args.append(mine_id)
    if status:
        where_clauses.append("e.status = ?")
        args.append(status)
    if eq_type:
        where_clauses.append("e.type = ?")
        args.append(eq_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = query_db(f"SELECT COUNT(*) AS total FROM equipment e {where_sql}", args, one=True)["total"]

    data_sql = f"""
        SELECT e.*, m.name as mine_name, s.name as section_name
        FROM equipment e
        JOIN mines m ON e.mine_id = m.id
        LEFT JOIN sections s ON e.section_id = s.id
        {where_sql}
        ORDER BY e.next_maintenance_due ASC, e.name ASC
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
        "message": "Equipment retrieved"
    }), 200


@equipment_bp.route("/maintenance-due", methods=["GET"])
@jwt_required()
def get_maintenance_due():
    """List equipment items that are past due or due for maintenance within next 14 days."""
    mine_id = request.args.get("mine_id")
    target_date = (date.today() + timedelta(days=14)).isoformat()

    where_clauses = ["(e.next_maintenance_due <= ? OR e.status = 'needs_maintenance')", "e.status != 'decommissioned'"]
    args = [target_date]

    if mine_id:
        where_clauses.append("e.mine_id = ?")
        args.append(mine_id)

    where_sql = f"WHERE {' AND '.join(where_clauses)}"
    query = f"""
        SELECT e.*, m.name as mine_name, s.name as section_name
        FROM equipment e
        JOIN mines m ON e.mine_id = m.id
        LEFT JOIN sections s ON e.section_id = s.id
        {where_sql}
        ORDER BY e.next_maintenance_due ASC
    """
    items = query_db(query, args)
    return jsonify({"success": True, "data": items, "message": "Maintenance due equipment retrieved"}), 200


@equipment_bp.route("/<int:equipment_id>", methods=["GET"])
@jwt_required()
def get_equipment(equipment_id):
    """Retrieve equipment details along with its maintenance history."""
    eq = query_db(
        """
        SELECT e.*, m.name as mine_name, s.name as section_name
        FROM equipment e
        JOIN mines m ON e.mine_id = m.id
        LEFT JOIN sections s ON e.section_id = s.id
        WHERE e.id = ?
        """,
        (equipment_id,),
        one=True,
    )
    if not eq:
        return jsonify({"success": False, "data": None, "message": "Equipment not found"}), 404

    history = query_db(
        """
        SELECT ma.*, u.full_name as performed_by_name
        FROM maintenance_activities ma
        JOIN users u ON ma.performed_by = u.id
        WHERE ma.equipment_id = ?
        ORDER BY ma.date_performed DESC
        """,
        (equipment_id,),
    )

    res = dict(eq)
    res["maintenance_history"] = history
    return jsonify({"success": True, "data": res, "message": "Equipment details retrieved"}), 200


@equipment_bp.route("", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def create_equipment():
    """Register a new piece of mining machinery or apparatus."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    section_id = data.get("section_id")
    name = data.get("name", "").strip()
    eq_type = data.get("type", "").strip()
    serial_number = data.get("serial_number", "").strip()
    manufacturer = data.get("manufacturer", "").strip()
    installation_date = data.get("installation_date")
    last_maintenance_date = data.get("last_maintenance_date")
    next_maintenance_due = data.get("next_maintenance_due")
    status = data.get("status", "operational")

    if not mine_id or not name or not serial_number:
        return jsonify({"success": False, "data": None, "message": "Mine, name, and serial_number are required"}), 400

    existing = query_db("SELECT id FROM equipment WHERE serial_number = ?", (serial_number,), one=True)
    if existing:
        return jsonify({"success": False, "data": None, "message": "Serial number already registered"}), 409

    now_iso = datetime.utcnow().isoformat() + "Z"
    eq_id = execute_db(
        """
        INSERT INTO equipment (
            mine_id, section_id, name, type, serial_number, manufacturer, 
            installation_date, last_maintenance_date, next_maintenance_due, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (mine_id, section_id, name, eq_type, serial_number, manufacturer, installation_date, last_maintenance_date, next_maintenance_due, status, now_iso),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="CREATE", entity_type="equipment", entity_id=eq_id, new_values=data)

    return jsonify({"success": True, "data": {"id": eq_id}, "message": "Equipment registered successfully"}), 201


@equipment_bp.route("/<int:equipment_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def update_equipment(equipment_id):
    """Update equipment status and records."""
    existing = query_db("SELECT * FROM equipment WHERE id = ?", (equipment_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Equipment not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name", existing["name"]).strip()
    eq_type = data.get("type", existing["type"]).strip()
    manufacturer = data.get("manufacturer", existing["manufacturer"]).strip()
    section_id = data.get("section_id", existing["section_id"])
    last_maintenance_date = data.get("last_maintenance_date", existing["last_maintenance_date"])
    next_maintenance_due = data.get("next_maintenance_due", existing["next_maintenance_due"])
    status = data.get("status", existing["status"])

    execute_db(
        """
        UPDATE equipment
        SET name = ?, type = ?, manufacturer = ?, section_id = ?, 
            last_maintenance_date = ?, next_maintenance_due = ?, status = ?
        WHERE id = ?
        """,
        (name, eq_type, manufacturer, section_id, last_maintenance_date, next_maintenance_due, status, equipment_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="equipment", entity_id=equipment_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": equipment_id}, "message": "Equipment updated successfully"}), 200


# Maintenance Activities endpoints
@equipment_bp.route("/maintenance", methods=["GET"])
@equipment_bp.route("/<int:equipment_id>/maintenance", methods=["GET"])
@jwt_required()
def list_maintenance(equipment_id=None):
    """List maintenance activities with optional equipment filter."""
    where_sql = "WHERE ma.equipment_id = ?" if equipment_id else ""
    args = [equipment_id] if equipment_id else []

    query = f"""
        SELECT ma.*, e.name as equipment_name, e.serial_number, u.full_name as performed_by_name
        FROM maintenance_activities ma
        JOIN equipment e ON ma.equipment_id = e.id
        JOIN users u ON ma.performed_by = u.id
        {where_sql}
        ORDER BY ma.date_performed DESC
    """
    items = query_db(query, args)
    return jsonify({"success": True, "data": items, "message": "Maintenance activities retrieved"}), 200


@equipment_bp.route("/maintenance", methods=["POST"])
@equipment_bp.route("/<int:equipment_id>/maintenance", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def create_maintenance(equipment_id=None):
    """Log completed or scheduled maintenance activity and update equipment next_due_date."""
    data = request.get_json(silent=True) or {}
    eq_id = equipment_id or data.get("equipment_id")
    m_type = data.get("type", "preventive")
    description = data.get("description", "").strip()
    date_performed = data.get("date_performed") or datetime.utcnow().date().isoformat()
    next_due_date = data.get("next_due_date")
    cost = float(data.get("cost", 0.0))
    parts_replaced = data.get("parts_replaced", "")
    status = data.get("status", "completed")
    performed_by = int(get_jwt_identity())

    if not eq_id or not description:
        return jsonify({"success": False, "data": None, "message": "Equipment ID and description required"}), 400

    now_iso = datetime.utcnow().isoformat() + "Z"
    ma_id = execute_db(
        """
        INSERT INTO maintenance_activities (
            equipment_id, performed_by, type, description, date_performed, 
            next_due_date, cost, parts_replaced, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (eq_id, performed_by, m_type, description, date_performed, next_due_date, cost, parts_replaced, status, now_iso),
    )

    # If completed, update equipment's last maintenance date, next maintenance due, and status to operational
    if status == "completed":
        execute_db(
            """
            UPDATE equipment
            SET last_maintenance_date = ?, next_maintenance_due = ?, status = 'operational'
            WHERE id = ?
            """,
            (date_performed, next_due_date, eq_id),
        )

    log_action(user_id=performed_by, action="CREATE", entity_type="maintenance_activity", entity_id=ma_id, new_values=data)

    return jsonify({"success": True, "data": {"id": ma_id}, "message": "Maintenance activity recorded successfully"}), 201
