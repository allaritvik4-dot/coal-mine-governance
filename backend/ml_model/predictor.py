"""Inference service for the Coal Mine Safety Hazard Classifier & Risk Severity Predictor."""

import os
import json
import joblib
import numpy as np
from typing import Dict, Any, List

# DGMS Safety Advisories mapped to predicted hazard types
DGMS_SAFETY_ADVISORIES = {
    "gas_inrush": {
        "title": "Methane / Noxious Gas Statutory Protocol (CMR 2017 Reg 169)",
        "advisory": "Immediately evacuate the return airway and downstream working faces if CH4 exceeds 0.75%. Cut off electrical power to FLP machinery. Deploy flame safety lamps and multi-gas detector for continuous monitoring.",
        "action_required": "Ventilation survey, methane drainage check, and DGMS Form IV notification."
    },
    "roof_fall": {
        "title": "Strata Control & Roof Support Plan (CMR 2017 Reg 123)",
        "advisory": "Cease coal extraction in affected heading. Inspect all resin-grouted roof bolts and W-strap assemblies within 30 meters. Check load cells and convergence indicators.",
        "action_required": "Install emergency cribs / hydraulic props. Authorize entry only by certified Overman."
    },
    "ventilation_failure": {
        "title": "Main & Auxiliary Ventilation Emergency Procedure (CMR 2017 Reg 153)",
        "advisory": "If main exhaust fan trips, withdraw all personnel to intake shaft station immediately. Do not start auxiliary fans until main air current is fully restored and tested.",
        "action_required": "Check substation switchgear, standby diesel generator switchover, and brattice integrity."
    },
    "spontaneous_combustion": {
        "title": "Mine Fire & Spontaneous Heating Protocol (CMR 2017 Reg 137)",
        "advisory": "Collect air samples for CO/O2 Graham's ratio analysis. Inspect all isolation stopping seals for leakage. Prepare nitrogen injection or high-expansion foam equipment.",
        "action_required": "Sample air chromatograph analysis and airtight sealing inspection."
    },
    "inundation": {
        "title": "Precaution Against Inundation of Water (CMR 2017 Reg 149)",
        "advisory": "Do not advance working face within 60 meters of unverified old workings without advance exploratory boreholes. Verify sump storage margin and standby pump capacity.",
        "action_required": "Start emergency turbine dewatering pumps and test telemetric float switches."
    },
    "machinery_failure": {
        "title": "Heavy Earth Moving & Underground Machinery Safety (CMR 2017 Reg 184)",
        "advisory": "Lock-out and tag-out (LOTO) mechanical power transmission. Inspect hydraulic hoses, braking calipers, and emergency trip wires.",
        "action_required": "Non-destructive testing (NDT) and colliery mechanical engineer sign-off."
    },
    "electrical_short_circuit": {
        "title": "Flameproof Electrical Apparatus Standard (CMR 2017 Reg 196)",
        "advisory": "Isolate high-tension circuit breaker at surface substation. Inspect flameproof enclosure gap tolerances (< 0.5mm) and earth continuity relay.",
        "action_required": "Megger insulation resistance test before re-energizing gate end box."
    },
    "slope_instability": {
        "title": "Opencast Bench & Dump Slope Stability Regulation (CMR 2017 Reg 175)",
        "advisory": "Clear haul trucks from bench toe immediately. Set up prism laser targets and radar for slope movement rate tracking. Reduce overall bench slope to <= 55 degrees.",
        "action_required": "Geotechnical engineer strata stability review."
    },
    "dust_explosion": {
        "title": "Coal Dust Explosion Prevention & Stone Dusting (CMR 2017 Reg 144)",
        "advisory": "Apply heavy stone dust charge to floor, roof, and sides ensuring >= 75% incombustible matter content. Verify all water barriers and mist fogger nozzles.",
        "action_required": "Roadway dust sampling and lab incineration test."
    }
}


class CoalMineRiskPredictor:
    """Wrapper for the trained scikit-learn models with DGMS advisories."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(__file__), "saved_model")
        self.model_path = os.path.join(self.model_dir, "coal_mine_hazard_classifier.joblib")
        self.meta_path = os.path.join(self.model_dir, "model_metadata.json")
        self.bundle = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        """Load trained model bundle and metadata."""
        if os.path.exists(self.model_path):
            try:
                self.bundle = joblib.load(self.model_path)
                print(f"[CoalMineRiskPredictor] Successfully loaded AI model from {self.model_path}")
            except Exception as e:
                print(f"[CoalMineRiskPredictor] Warning: Error loading model: {e}")
                self.bundle = None

        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"[CoalMineRiskPredictor] Warning: Error loading metadata: {e}")
                self.metadata = None

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata, metrics, and training specifications."""
        if not self.metadata:
            return {
                "status": "not_trained",
                "message": "AI Model not loaded or not trained."
            }
        return {
            "status": "ready",
            "model_file": self.model_path,
            "file_size_bytes": os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 0,
            "metadata": self.metadata,
        }

    def predict_hazard_risk(self, description: str) -> Dict[str, Any]:
        """Run ML prediction on input hazard or incident observation text."""
        if not description or not description.strip():
            return {"error": "Description cannot be empty"}

        if not self.bundle:
            self._load_model()
            if not self.bundle:
                return {
                    "error": "Trained model file not found. Run backend/ml_model/train.py first."
                }

        cat_model = self.bundle["category_model"]
        sev_model = self.bundle["severity_model"]

        # Run predictions
        pred_cat = cat_model.predict([description])[0]
        pred_sev = sev_model.predict([description])[0]

        # Probabilities
        cat_probs = cat_model.predict_proba([description])[0]
        cat_classes = cat_model.classes_
        confidence = float(np.max(cat_probs))

        # Top 3 predicted categories with confidence
        top_indices = np.argsort(cat_probs)[::-1][:3]
        top_categories = [
            {"category": cat_classes[i], "probability": round(float(cat_probs[i]), 4)}
            for i in top_indices
        ]

        # DGMS statutory advisory
        advisory = DGMS_SAFETY_ADVISORIES.get(pred_cat, {
            "title": "General Coal Mine Safety Precaution",
            "advisory": "Follow standard operating procedure and inform designated colliery safety officer.",
            "action_required": "Site inspection and risk assessment."
        })

        return {
            "input_text": description,
            "predicted_category": pred_cat,
            "predicted_severity": pred_sev,
            "confidence": round(confidence, 4),
            "top_categories": top_categories,
            "statutory_advisory": advisory,
            "model_version": self.metadata.get("trained_at", "v1.0") if self.metadata else "v1.0",
        }
