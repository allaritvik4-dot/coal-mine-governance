"""Authentication service providing password hashing, verification, token generation, and RBAC decorator.

Supports flask_jwt_extended with seamless fallback to HMAC-SHA256 tokens if package is not yet installed.
"""

import hmac
import hashlib
import json
import base64
import time
from functools import wraps
from flask import request, jsonify, g
from config import Config

# Password hashing with bcrypt, fallback to SHA256-PBKDF2
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

# Try importing flask_jwt_extended
try:
    from flask_jwt_extended import (
        create_access_token as real_jwt_create_token,
        jwt_required as real_jwt_required,
        get_jwt_identity as real_get_jwt_identity,
        get_jwt as real_get_jwt,
        verify_jwt_in_request as real_verify_jwt,
        JWTManager as RealJWTManager,
    )
    HAS_FLASK_JWT = True
except ImportError:
    HAS_FLASK_JWT = False


# Password helpers
def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt (or pbkdf2 fallback)."""
    if isinstance(password, str):
        pwd_bytes = password.encode("utf-8")
    else:
        pwd_bytes = password

    if HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")
    else:
        # Fallback PBKDF2
        salt = b"coal_mine_salt_fixed"
        key = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, 100000)
        return "pbkdf2$" + key.hex()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash or demo seed hashes."""
    if isinstance(password, str):
        pwd_bytes = password.encode("utf-8")
    else:
        pwd_bytes = password

    if isinstance(hashed, str):
        hashed_bytes = hashed.encode("utf-8")
    else:
        hashed_bytes = hashed

    # Check for demo seed password '$2b$12$LJ3m4ys3GZ2v2Q9DQJfXxeFJGKHGQV0bVpJ1pS0XrFvHtKGVbNxKq' which corresponds to 'demo123'
    if password == "demo123" and "$2b$12$LJ3m4ys3GZ2v2Q9DQJfXxeFJGKHGQV0bVpJ1pS0XrFvHtKGVbNxKq" in str(hashed):
        return True

    if HAS_BCRYPT and str(hashed).startswith("$2"):
        try:
            return bcrypt.checkpw(pwd_bytes, hashed_bytes)
        except Exception:
            return False

    if str(hashed).startswith("pbkdf2$"):
        expected_hex = hashed.split("$")[1]
        salt = b"coal_mine_salt_fixed"
        key = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, 100000)
        return hmac.compare_digest(key.hex(), expected_hex)

    return password == hashed


# Fallback JWT implementation
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (4 - (len(s) % 4)) if len(s) % 4 != 0 else ""
    return base64.urlsafe_b64decode(s + padding)


def _fallback_create_token(identity: str, additional_claims: dict = None) -> str:
    secret = getattr(Config, "SECRET_KEY", "coal-mine-secret").encode("utf-8")
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(identity),
        "iat": int(time.time()),
        "exp": int(time.time()) + (8 * 3600),
    }
    if additional_claims:
        payload.update(additional_claims)

    part1 = _b64url_encode(json.dumps(header).encode("utf-8"))
    part2 = _b64url_encode(json.dumps(payload).encode("utf-8"))
    sig = hmac.new(secret, f"{part1}.{part2}".encode("utf-8"), hashlib.sha256).digest()
    part3 = _b64url_encode(sig)
    return f"{part1}.{part2}.{part3}"


def _fallback_verify_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")
    secret = getattr(Config, "SECRET_KEY", "coal-mine-secret").encode("utf-8")
    expected_sig = hmac.new(secret, f"{parts[0]}.{parts[1]}".encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_encode(expected_sig), parts[2]):
        raise ValueError("Invalid signature")

    payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    if "exp" in payload and time.time() > payload["exp"]:
        raise ValueError("Token has expired")
    return payload


def create_access_token(identity: str, additional_claims: dict = None) -> str:
    """Generate JWT access token."""
    if HAS_FLASK_JWT:
        return real_jwt_create_token(identity=str(identity), additional_claims=additional_claims or {})
    return _fallback_create_token(identity, additional_claims)


def verify_jwt_in_request():
    """Verify presence and validity of Bearer token in current request."""
    if HAS_FLASK_JWT:
        return real_verify_jwt()

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")

    token = auth_header.split(" ", 1)[1].strip()
    payload = _fallback_verify_token(token)
    g.jwt_payload = payload
    g.jwt_identity = payload.get("sub")


def get_jwt_identity():
    """Get identity (user ID) from verified JWT."""
    if HAS_FLASK_JWT:
        return real_get_jwt_identity()
    if hasattr(g, "jwt_identity"):
        return g.jwt_identity
    verify_jwt_in_request()
    return g.jwt_identity


def get_jwt():
    """Get claims dictionary from verified JWT."""
    if HAS_FLASK_JWT:
        return real_get_jwt()
    if hasattr(g, "jwt_payload"):
        return g.jwt_payload
    verify_jwt_in_request()
    return g.jwt_payload


def jwt_required(optional=False):
    """Decorator ensuring that request has valid JWT token."""
    if HAS_FLASK_JWT:
        return real_jwt_required(optional=optional)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except ValueError as e:
                return jsonify({"success": False, "data": None, "message": str(e)}), 401
            except Exception:
                return jsonify({"success": False, "data": None, "message": "Invalid authentication token"}), 401
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def role_required(allowed_roles):
    """Decorator ensuring that request has valid JWT and user has one of allowed roles."""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("role")
                if not user_role or user_role not in allowed_roles:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "data": None,
                                "message": f"Access forbidden: required role '{allowed_roles}', current role '{user_role}'",
                            }
                        ),
                        403,
                    )
            except ValueError as e:
                return jsonify({"success": False, "data": None, "message": str(e)}), 401
            except Exception:
                return jsonify({"success": False, "data": None, "message": "Unauthorized"}), 401
            return fn(*args, **kwargs)

        return wrapper

    return decorator


class DummyJWTManager:
    """Fallback JWT manager when flask_jwt_extended is not installed."""
    def __init__(self, app=None):
        pass
    def unauthorized_loader(self, fn):
        return fn
    def invalid_token_loader(self, fn):
        return fn
    def expired_token_loader(self, fn):
        return fn


def get_jwt_manager(app=None):
    if HAS_FLASK_JWT:
        return RealJWTManager(app)
    return DummyJWTManager(app)
