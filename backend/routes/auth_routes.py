"""Authentication and user management route handlers."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import query_db, execute_db
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    role_required,
    jwt_required,
    get_jwt_identity,
)
from services.audit_service import log_action

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login generating JWT access token."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "data": None, "message": "Username and password required"}), 400

    user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"success": False, "data": None, "message": "Invalid username or password"}), 401

    if not user["is_active"]:
        return jsonify({"success": False, "data": None, "message": "Account has been deactivated"}), 403

    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={
            "username": user["username"],
            "role": user["role"],
            "mine_id": user["mine_id"],
            "full_name": user["full_name"],
        },
    )

    user_info = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "email": user["email"],
        "mine_id": user["mine_id"],
    }

    log_action(user_id=user["id"], action="LOGIN", entity_type="user", entity_id=user["id"])

    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": user_info,
        },
        "message": "Login successful"
    }), 200


@auth_bp.route("/register", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def register():
    """Register new user (Admin only)."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "viewer").strip().lower()
    email = data.get("email", "").strip()
    mine_id = data.get("mine_id")

    if not username or not password or not full_name or not email:
        return jsonify({"success": False, "data": None, "message": "Missing required fields"}), 400

    allowed_roles = ["admin", "mine_manager", "safety_officer", "inspector", "viewer"]
    if role not in allowed_roles:
        return jsonify({"success": False, "data": None, "message": f"Role must be one of: {allowed_roles}"}), 400

    existing_user = query_db("SELECT id FROM users WHERE username = ? OR email = ?", (username, email), one=True)
    if existing_user:
        return jsonify({"success": False, "data": None, "message": "Username or email already exists"}), 409

    hashed = hash_password(password)
    now_iso = datetime.utcnow().isoformat() + "Z"

    user_id = execute_db(
        """
        INSERT INTO users (username, password_hash, full_name, role, email, mine_id, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (username, hashed, full_name, role, email, mine_id, now_iso),
    )

    current_user_id = int(get_jwt_identity())
    log_action(
        user_id=current_user_id,
        action="CREATE",
        entity_type="user",
        entity_id=user_id,
        new_values={"username": username, "role": role, "email": email, "mine_id": mine_id},
    )

    return jsonify({
        "success": True,
        "data": {"id": user_id, "username": username, "full_name": full_name, "role": role},
        "message": "User registered successfully"
    }), 201


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Get profile of current authenticated user."""
    user_id = int(get_jwt_identity())
    user = query_db(
        """
        SELECT u.id, u.username, u.full_name, u.role, u.email, u.mine_id, u.is_active, u.created_at,
               m.name as mine_name
        FROM users u
        LEFT JOIN mines m ON u.mine_id = m.id
        WHERE u.id = ?
        """,
        (user_id,),
        one=True,
    )
    if not user:
        return jsonify({"success": False, "data": None, "message": "User not found"}), 404

    return jsonify({"success": True, "data": dict(user), "message": "User profile retrieved"}), 200


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change password for authenticated user."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"success": False, "data": None, "message": "Both old and new password required"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "data": None, "message": "Password must be at least 6 characters"}), 400

    user = query_db("SELECT password_hash FROM users WHERE id = ?", (user_id,), one=True)
    if not user or not verify_password(old_password, user["password_hash"]):
        return jsonify({"success": False, "data": None, "message": "Incorrect current password"}), 401

    new_hash = hash_password(new_password)
    now_iso = datetime.utcnow().isoformat() + "Z"
    execute_db("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now_iso, user_id))

    log_action(user_id=user_id, action="UPDATE_PASSWORD", entity_type="user", entity_id=user_id)

    return jsonify({"success": True, "data": None, "message": "Password changed successfully"}), 200
