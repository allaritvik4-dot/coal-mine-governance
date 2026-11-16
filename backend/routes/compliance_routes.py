"""Compliance rules, automated checks, alerts, and corrective action routes."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action
from services.compliance_engine import run_all_checks, resolve_alert as engine_resolve_alert, create_corrective_action

compliance_bp = Blueprint("compliance", __name__, url_prefix="/api/compliance")


# ============================================================
# RULES
# ============================================================
@compliance_bp.route("/rules", methods=["GET"])
@jwt_required()
def get_rules():
    """List all statutory compliance rules."""
    category = request.args.get("category")
    is_active = request.args.get("is_active")

    where_clauses = []
    args = []
    if category:
        where_clauses.append("cr.category = ?")
        args.append(category)
    if is_active is not None:
        where_clauses.append("cr.is_active = ?")
        args.append(int(is_active))

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT cr.*, u.full_name as created_by_name
        FROM compliance_rules cr
        LEFT JOIN users u ON cr.created_by = u.id
        {where_sql}
        ORDER BY cr.rule_code ASC
    """
    rules = query_db(query, args)
    return jsonify({"success": True, "data": rules, "message": "Compliance rules retrieved"}), 200


@compliance_bp.route("/rules", methods=["POST"])
@jwt_required()
@role_required(["admin", "safety_officer"])
def create_rule():
    """Define a new statutory compliance rule."""
    data = request.get_json(silent=True) or {}
    rule_code = data.get("rule_code", "").strip().upper()
    description = data.get("description", "").strip()
    category = data.get("category", "").strip().lower()
    threshold_value = data.get("threshold_value")
    threshold_unit = data.get("threshold_unit", "")
    check_frequency = data.get("check_frequency", "monthly")
    severity = data.get("severity", "medium").lower()
    user_id = int(get_jwt_identity())

    if not rule_code or not description or not category:
        return jsonify({"success": False, "data": None, "message": "Rule code, description, and category required"}), 400

    existing = query_db("SELECT id FROM compliance_rules WHERE rule_code = ?", (rule_code,), one=True)
    if existing:
        return jsonify({"success": False, "data": None, "message": "Rule code already exists"}), 409

    now_iso = datetime.utcnow().isoformat() + "Z"
    rule_id = execute_db(
        """
        INSERT INTO compliance_rules (
            rule_code, description, category, threshold_value, threshold_unit, 
            check_frequency, severity, is_active, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (rule_code, description, category, threshold_value, threshold_unit, check_frequency, severity, user_id, now_iso),
    )

    log_action(user_id=user_id, action="CREATE", entity_type="compliance_rule", entity_id=rule_id, new_values=data)

    return jsonify({"success": True, "data": {"id": rule_id, "rule_code": rule_code}, "message": "Rule created successfully"}), 201


@compliance_bp.route("/rules/<int:rule_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "safety_officer"])
def update_rule(rule_id):
    """Update compliance rule parameters or active status."""
    existing = query_db("SELECT * FROM compliance_rules WHERE id = ?", (rule_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Rule not found"}), 404

    data = request.get_json(silent=True) or {}
    description = data.get("description", existing["description"]).strip()
    category = data.get("category", existing["category"]).strip().lower()
    threshold_value = data.get("threshold_value", existing["threshold_value"])
    threshold_unit = data.get("threshold_unit", existing["threshold_unit"])
    check_frequency = data.get("check_frequency", existing["check_frequency"])
    severity = data.get("severity", existing["severity"])
    is_active = data.get("is_active", existing["is_active"])

    execute_db(
        """
        UPDATE compliance_rules
        SET description = ?, category = ?, threshold_value = ?, threshold_unit = ?, 
            check_frequency = ?, severity = ?, is_active = ?
        WHERE id = ?
        """,
        (description, category, threshold_value, threshold_unit, check_frequency, severity, is_active, rule_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="compliance_rule", entity_id=rule_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": rule_id}, "message": "Rule updated successfully"}), 200


# ============================================================
# ALERTS
# ============================================================
@compliance_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    """List compliance alerts with filtering and pagination."""
    mine_id = request.args.get("mine_id")
    status = request.args.get("status")
    severity = request.args.get("severity")
    rule_id = request.args.get("rule_id")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("ca.mine_id = ?")
        args.append(mine_id)
    if status:
        where_clauses.append("ca.status = ?")
        args.append(status)
    if severity:
        where_clauses.append("ca.severity = ?")
        args.append(severity)
    if rule_id:
        where_clauses.append("ca.rule_id = ?")
        args.append(rule_id)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = query_db(f"SELECT COUNT(*) AS total FROM compliance_alerts ca {where_sql}", args, one=True)["total"]

    data_sql = f"""
        SELECT ca.*, cr.rule_code, cr.description as rule_description, cr.category,
               m.name as mine_name, s.name as section_name,
               u_assign.full_name as assigned_to_name, u_res.full_name as resolved_by_name
        FROM compliance_alerts ca
        JOIN compliance_rules cr ON ca.rule_id = cr.id
        JOIN mines m ON ca.mine_id = m.id
        LEFT JOIN sections s ON ca.section_id = s.id
        LEFT JOIN users u_assign ON ca.assigned_to = u_assign.id
        LEFT JOIN users u_res ON ca.resolved_by = u_res.id
        {where_sql}
        ORDER BY 
            CASE ca.severity 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'medium' THEN 3 
                ELSE 4 
            END,
            ca.created_at DESC
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
        "message": "Alerts retrieved"
    }), 200


@compliance_bp.route("/alerts/<int:alert_id>/acknowledge", methods=["PUT", "POST"])
@jwt_required()
def acknowledge_alert(alert_id):
    """Mark an alert as acknowledged by user."""
    existing = query_db("SELECT * FROM compliance_alerts WHERE id = ?", (alert_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Alert not found"}), 404

    user_id = int(get_jwt_identity())
    execute_db("UPDATE compliance_alerts SET status = 'acknowledged', assigned_to = ? WHERE id = ?", (user_id, alert_id))

    log_action(user_id=user_id, action="ACKNOWLEDGE", entity_type="compliance_alert", entity_id=alert_id, old_values={"status": existing["status"]})

    return jsonify({"success": True, "data": {"id": alert_id, "status": "acknowledged"}, "message": "Alert acknowledged"}), 200


@compliance_bp.route("/alerts/<int:alert_id>/resolve", methods=["PUT", "POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def resolve_alert_route(alert_id):
    """Resolve an open compliance alert."""
    user_id = int(get_jwt_identity())
    success, msg = engine_resolve_alert(alert_id, user_id)
    if not success:
        return jsonify({"success": False, "data": None, "message": msg}), 400

    return jsonify({"success": True, "data": {"id": alert_id, "status": "resolved"}, "message": msg}), 200


@compliance_bp.route("/run-checks", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer", "inspector"])
def trigger_compliance_checks():
    """Trigger real-time compliance evaluation engine scan."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    result = run_all_checks(mine_id)

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="RUN_CHECKS", entity_type="compliance_engine", entity_id=mine_id, new_values=result)

    return jsonify({"success": True, "data": result, "message": f"Compliance check completed. {result['total_new_alerts']} new alert(s) generated."}), 200


# ============================================================
# CORRECTIVE ACTIONS
# ============================================================
@compliance_bp.route("/corrective-actions", methods=["GET"])
@jwt_required()
def get_corrective_actions():
    """List corrective action plans."""
    mine_id = request.args.get("mine_id")
    status = request.args.get("status")
    priority = request.args.get("priority")
    alert_id = request.args.get("alert_id")

    where_clauses = []
    args = []
    if mine_id:
        where_clauses.append("ca.mine_id = ?")
        args.append(mine_id)
    if status:
        where_clauses.append("ca.status = ?")
        args.append(status)
    if priority:
        where_clauses.append("ca.priority = ?")
        args.append(priority)
    if alert_id:
        where_clauses.append("ca.alert_id = ?")
        args.append(alert_id)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT ca.*, m.name as mine_name,
               u_to.full_name as assigned_to_name,
               u_by.full_name as assigned_by_name,
               alert.message as alert_message, alert.severity as alert_severity
        FROM corrective_actions ca
        JOIN mines m ON ca.mine_id = m.id
        LEFT JOIN compliance_alerts alert ON ca.alert_id = alert.id
        LEFT JOIN users u_to ON ca.assigned_to = u_to.id
        LEFT JOIN users u_by ON ca.assigned_by = u_by.id
        {where_sql}
        ORDER BY ca.due_date ASC, ca.created_at DESC
    """
    items = query_db(query, args)
    return jsonify({"success": True, "data": items, "message": "Corrective actions retrieved"}), 200


@compliance_bp.route("/corrective-actions", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def post_corrective_action():
    """Create a new corrective action item."""
    data = request.get_json(silent=True) or {}
    alert_id = data.get("alert_id")
    mine_id = data.get("mine_id")
    description = data.get("description", "").strip()
    assigned_to = data.get("assigned_to")
    priority = data.get("priority", "medium")
    due_date = data.get("due_date")
    evidence_notes = data.get("evidence_notes")
    assigned_by = int(get_jwt_identity())

    if not alert_id or not mine_id or not description:
        return jsonify({"success": False, "data": None, "message": "Alert ID, mine ID, and description required"}), 400

    ca_id = create_corrective_action(
        alert_id=alert_id,
        mine_id=mine_id,
        description=description,
        assigned_to=assigned_to,
        assigned_by=assigned_by,
        priority=priority,
        due_date=due_date,
        evidence_notes=evidence_notes,
    )

    return jsonify({"success": True, "data": {"id": ca_id}, "message": "Corrective action assigned successfully"}), 201


@compliance_bp.route("/corrective-actions/<int:ca_id>", methods=["PUT"])
@jwt_required()
def update_corrective_action(ca_id):
    """Update progress, status, or evidence notes for a corrective action."""
    existing = query_db("SELECT * FROM corrective_actions WHERE id = ?", (ca_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Corrective action not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status", existing["status"])
    evidence_notes = data.get("evidence_notes", existing["evidence_notes"])
    completed_date = data.get("completed_date", existing["completed_date"])

    if status == "completed" and not completed_date:
        completed_date = datetime.utcnow().date().isoformat()

    now_iso = datetime.utcnow().isoformat() + "Z"
    execute_db(
        """
        UPDATE corrective_actions
        SET status = ?, evidence_notes = ?, completed_date = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, evidence_notes, completed_date, now_iso, ca_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="corrective_action", entity_id=ca_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": ca_id, "status": status}, "message": "Corrective action updated"}), 200
