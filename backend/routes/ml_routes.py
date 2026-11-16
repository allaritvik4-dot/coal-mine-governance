"""API routes for AI Machine Learning Safety Risk Classifier."""

from flask import Blueprint, request, jsonify
from services.auth_service import jwt_required, get_jwt_identity, role_required
from services.audit_service import log_action
from ml_model.predictor import CoalMineRiskPredictor
from ml_model.train import train_and_save_model

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")


@ml_bp.route("/model-info", methods=["GET"])
@jwt_required()
def get_model_info():
    """Get metadata and validation performance metrics of the trained AI model."""
    predictor = CoalMineRiskPredictor.get_instance()
    info = predictor.get_model_info()
    return jsonify({
        "success": True,
        "data": info,
        "message": "AI model specifications retrieved successfully"
    }), 200


@ml_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict_hazard():
    """Predict statutory hazard classification, severity, and DGMS advisory from text description."""
    data = request.get_json(silent=True) or {}
    description = (data.get("description") or data.get("text") or "").strip()

    if not description:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Field 'description' is required for AI risk assessment."
        }), 400

    predictor = CoalMineRiskPredictor.get_instance()
    result = predictor.predict_hazard_risk(description)

    if "error" in result:
        return jsonify({
            "success": False,
            "data": None,
            "message": result["error"]
        }), 500

    try:
        user_id = int(get_jwt_identity())
        log_action(
            user_id=user_id,
            action="AI_PREDICT",
            entity_type="ml_prediction",
            new_values={
                "predicted_category": result["predicted_category"],
                "predicted_severity": result["predicted_severity"],
                "confidence": result["confidence"],
            }
        )
    except Exception:
        pass

    return jsonify({
        "success": True,
        "data": result,
        "message": "Hazard risk predicted successfully"
    }), 200


@ml_bp.route("/retrain", methods=["POST"])
@jwt_required()
@role_required(["admin", "mine_manager", "safety_officer"])
def retrain_model():
    """Trigger retraining of the safety classifier model."""
    try:
        model_bundle = train_and_save_model()
        predictor = CoalMineRiskPredictor.get_instance()
        predictor._load_model()

        user_id = int(get_jwt_identity())
        log_action(
            user_id=user_id,
            action="AI_RETRAIN",
            entity_type="ml_model",
            new_values=model_bundle.get("metrics")
        )

        return jsonify({
            "success": True,
            "data": model_bundle.get("metrics"),
            "message": "Model retrained and persisted successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Training failed: {str(e)}"
        }), 500
