"""Main application factory and entry point for the Coal Mine Governance API."""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from database.db import init_db, close_db, query_db
from services.auth_service import get_jwt_manager
from services.rag_service import RAGService
from knowledge_base.ingest import ingest_all_documents

# Import blueprints
from routes.auth_routes import auth_bp
from routes.mine_routes import mine_bp
from routes.inspection_routes import inspection_bp
from routes.hazard_routes import hazard_bp
from routes.incident_routes import incident_bp
from routes.equipment_routes import equipment_bp
from routes.training_routes import training_bp
from routes.compliance_routes import compliance_bp
from routes.assistant_routes import assistant_bp
from routes.report_routes import report_bp
from routes.ml_routes import ml_bp


def create_app(config_class=Config):
    """Application factory for Flask backend."""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
    app = Flask(__name__, static_folder=frontend_dist, static_url_path="")
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Setup JWT Manager
    jwt = get_jwt_manager(app)

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"success": False, "data": None, "message": "Missing Authorization header with Bearer token"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"success": False, "data": None, "message": "Invalid authentication token"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"success": False, "data": None, "message": "Authentication token has expired. Please log in again."}), 401

    # Database teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(mine_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(hazard_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(ml_bp)

    # Global Health Check
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_healthy = False
        try:
            res = query_db("SELECT 1 AS ok;", one=True)
            db_healthy = res and res["ok"] == 1
        except Exception:
            db_healthy = False

        return jsonify({
            "success": True,
            "data": {
                "status": "healthy" if db_healthy else "degraded",
                "database_connected": db_healthy,
                "version": "1.0.0",
                "service": "Coal Mine Smart Governance & Compliance Backend"
            },
            "message": "Service operational"
        }), 200

    # Serve React Frontend SPA
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"success": False, "data": None, "message": "API endpoint not found"}), 404
        target = os.path.join(frontend_dist, path)
        if path and os.path.exists(target):
            return send_from_directory(frontend_dist, path)
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(frontend_dist, "index.html")
        return jsonify({"message": "Frontend distribution not found. Run npm run build."}), 404

    # Global HTTP Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({"success": False, "data": None, "message": str(e.description if hasattr(e, 'description') else "Bad request")}), 400

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"success": False, "data": None, "message": "Endpoint or resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        return jsonify({"success": False, "data": None, "message": "HTTP method not allowed for this route"}), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"success": False, "data": None, "message": "Internal server error occurred"}), 500

    return app


app = create_app()


def startup():
    """Perform initial database migration and knowledge base indexing."""
    with app.app_context():
        try:
            print("[Startup] Initializing SQLite database...")
            init_db(app)
            print("[Startup] Database initialized successfully.")
        except Exception as e:
            print(f"[Startup] Error initializing database: {e}")

        try:
            print("[Startup] Initializing Knowledge Base...")
            ingest_all_documents()
            print("[Startup] Knowledge base indexing complete.")
        except Exception as e:
            print(f"[Startup] Error indexing knowledge base: {e}")


# Initialize when imported or started
startup()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
