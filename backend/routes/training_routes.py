"""Worker safety training and competency certification route handlers."""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from database.db import query_db, execute_db
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

training_bp = Blueprint("training", __name__, url_prefix="/api/training")


@training_bp.route("", methods=["GET"])
@jwt_required()
def list_training():
    """List training and certification records with filters and pagination."""
    mine_id = request.args.get("mine_id")
    status = request.args.get("status")
    training_type = request.args.get("training_type")
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    where_clauses = []
    args = []

    if mine_id:
        where_clauses.append("t.mine_id = ?")
        args.append(mine_id)
    if status:
        where_clauses.append("t.status = ?")
        args.append(status)
    if training_type:
        where_clauses.append("t.training_type = ?")
        args.append(training_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = query_db(f"SELECT COUNT(*) AS total FROM training_records t {where_sql}", args, one=True)["total"]

    data_sql = f"""
        SELECT t.*, m.name as mine_name
        FROM training_records t
        JOIN mines m ON t.mine_id = m.id
        {where_sql}
        ORDER BY t.valid_until ASC, t.worker_name ASC
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
        "message": "Training records retrieved"
    }), 200


@training_bp.route("/expiring", methods=["GET"])
@jwt_required()
def get_expiring_training():
    """Retrieve certifications that are expired or expiring within next 30 days."""
    mine_id = request.args.get("mine_id")
    today = date.today().isoformat()
    future = (date.today() + timedelta(days=30)).isoformat()

    where_clauses = ["t.valid_until <= ?"]
    args = [future]

    if mine_id:
        where_clauses.append("t.mine_id = ?")
        args.append(mine_id)

    where_sql = f"WHERE {' AND '.join(where_clauses)}"
    query = f"""
        SELECT t.*, m.name as mine_name,
               CASE 
                   WHEN t.valid_until < '{today}' THEN 'expired'
                   ELSE 'expiring_soon'
               END as computed_status
        FROM training_records t
        JOIN mines m ON t.mine_id = m.id
        {where_sql}
        ORDER BY t.valid_until ASC
    """
    items = query_db(query, args)
    return jsonify({"success": True, "data": items, "message": "Expiring training records retrieved"}), 200


@training_bp.route("/<int:record_id>", methods=["GET"])
@jwt_required()
def get_training(record_id):
    """Retrieve details of a single training record."""
    rec = query_db(
        """
        SELECT t.*, m.name as mine_name
        FROM training_records t
        JOIN mines m ON t.mine_id = m.id
        WHERE t.id = ?
        """,
        (record_id,),
        one=True,
    )
    if not rec:
        return jsonify({"success": False, "data": None, "message": "Training record not found"}), 404

    return jsonify({"success": True, "data": dict(rec), "message": "Training record details retrieved"}), 200


@training_bp.route("", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def create_training():
    """Register new training completion or statutory certification."""
    data = request.get_json(silent=True) or {}
    mine_id = data.get("mine_id")
    worker_name = data.get("worker_name", "").strip()
    worker_id_number = data.get("worker_id_number", "").strip()
    training_type = data.get("training_type", "").strip()
    description = data.get("description", "").strip()
    trainer_name = data.get("trainer_name", "").strip()
    date_completed = data.get("date_completed") or datetime.utcnow().date().isoformat()
    valid_until = data.get("valid_until")
    certificate_number = data.get("certificate_number", "").strip()

    if not mine_id or not worker_name or not worker_id_number or not training_type:
        return jsonify({"success": False, "data": None, "message": "Mine, worker name, ID, and training type required"}), 400

    # Compute status based on valid_until
    today_str = date.today().isoformat()
    thirty_days = (date.today() + timedelta(days=30)).isoformat()
    if valid_until:
        if valid_until < today_str:
            status = "expired"
        elif valid_until <= thirty_days:
            status = "expiring_soon"
        else:
            status = "valid"
    else:
        status = "valid"

    now_iso = datetime.utcnow().isoformat() + "Z"
    t_id = execute_db(
        """
        INSERT INTO training_records (
            mine_id, worker_name, worker_id_number, training_type, description, 
            trainer_name, date_completed, valid_until, certificate_number, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (mine_id, worker_name, worker_id_number, training_type, description, trainer_name, date_completed, valid_until, certificate_number, status, now_iso),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="CREATE", entity_type="training_record", entity_id=t_id, new_values=data)

    return jsonify({"success": True, "data": {"id": t_id}, "message": "Training record logged successfully"}), 201


@training_bp.route("/<int:record_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def update_training(record_id):
    """Update training record or renew validity."""
    existing = query_db("SELECT * FROM training_records WHERE id = ?", (record_id,), one=True)
    if not existing:
        return jsonify({"success": False, "data": None, "message": "Training record not found"}), 404

    data = request.get_json(silent=True) or {}
    worker_name = data.get("worker_name", existing["worker_name"]).strip()
    worker_id_number = data.get("worker_id_number", existing["worker_id_number"]).strip()
    training_type = data.get("training_type", existing["training_type"]).strip()
    description = data.get("description", existing["description"]).strip()
    trainer_name = data.get("trainer_name", existing["trainer_name"]).strip()
    date_completed = data.get("date_completed", existing["date_completed"])
    valid_until = data.get("valid_until", existing["valid_until"])
    certificate_number = data.get("certificate_number", existing["certificate_number"]).strip()

    today_str = date.today().isoformat()
    thirty_days = (date.today() + timedelta(days=30)).isoformat()
    if valid_until:
        if valid_until < today_str:
            status = "expired"
        elif valid_until <= thirty_days:
            status = "expiring_soon"
        else:
            status = "valid"
    else:
        status = existing["status"]

    execute_db(
        """
        UPDATE training_records
        SET worker_name = ?, worker_id_number = ?, training_type = ?, description = ?, 
            trainer_name = ?, date_completed = ?, valid_until = ?, certificate_number = ?, status = ?
        WHERE id = ?
        """,
        (worker_name, worker_id_number, training_type, description, trainer_name, date_completed, valid_until, certificate_number, status, record_id),
    )

    user_id = int(get_jwt_identity())
    log_action(user_id=user_id, action="UPDATE", entity_type="training_record", entity_id=record_id, old_values=dict(existing), new_values=data)

    return jsonify({"success": True, "data": {"id": record_id}, "message": "Training record updated successfully"}), 200
