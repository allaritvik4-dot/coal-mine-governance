"""Training pipeline for Coal Mine Safety Hazard Classifier & Risk Severity Predictor.

Trains an NLP + Ensemble Machine Learning model specifically on Indian Coal Mine incident,
hazard, and statutory inspection reports as specified in SIH26024 Section VII.
"""

import os
import json
import joblib
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

# Comprehensive domain training dataset based on DGMS accident reports and colliery hazard records
TRAINING_DATA = [
    # Gas inrush & Methane
    ("Methane CH4 concentration detected at 1.4% in return airway near Panel B longwall face, exceeding 0.75% limit", "gas_inrush", "critical"),
    ("Flammable gas feeder issuing from floor fissure in seam 3, safety lamp flame capped", "gas_inrush", "critical"),
    ("Methane detector alarm triggered at 1.1% near coal cutting drum shearer", "gas_inrush", "high"),
    ("Minor gas bubbling through floor shale water at chainage 220m, 0.4% CH4 recorded", "gas_inrush", "medium"),
    ("Carbon monoxide CO reading spiked to 45 ppm following blasting in 4th heading", "gas_inrush", "high"),
    ("CO detector normal at 3 ppm in intake airway during continuous shift monitoring", "gas_inrush", "low"),

    # Roof Fall & Strata Control
    ("Major roof fall over 15 meters length along main haulage roadway, sandstone layer sheared off", "roof_fall", "critical"),
    ("Cracking sound observed in shale roof with noticeable bed separation at junction 4", "roof_fall", "high"),
    ("Hydraulic prop yielded under excessive strata pressure at longwall face position 18", "roof_fall", "high"),
    ("Convergence monitoring tell-tale shows 8mm movement over 24 hours in bord and pillar district", "roof_fall", "medium"),
    ("Roof bolts loose at chainage 340m, requiring retorquing to statutory 150 Nm", "roof_fall", "medium"),
    ("Minor spalling of side coal pillar ribs observed along conveyor drift", "roof_fall", "low"),
    ("Skin fall of coal slab weighing approx 25 kg detached between steel crossbars", "roof_fall", "medium"),

    # Ventilation Failure
    ("Main surface exhaust fan tripped due to 33kV substation power fluctuation, ventilation stopped", "ventilation_failure", "critical"),
    ("Auxiliary forcing fan air duct torn over 4 meters, air velocity dropped below 0.3 m/s at face", "ventilation_failure", "high"),
    ("Air crossing brattice partition damaged by runaway mine tub, intake air short-circuiting into return", "ventilation_failure", "high"),
    ("Ventilation door left unlatched causing partial loss of air quantity in depillaring section", "ventilation_failure", "medium"),
    ("Booster fan bearing temperature elevated to 68C, airflow delivery reduced by 10%", "ventilation_failure", "medium"),
    ("Airflow velocity at intake shaft measured 1.6 m/s, meeting statutory requirements", "ventilation_failure", "low"),

    # Spontaneous Combustion & Mine Fire
    ("White smoke and sweet benzene smell issuing from sealed off goaf area panel 2", "spontaneous_combustion", "critical"),
    ("Hot spot detected on coal pillar rib with thermal imaging camera registering 72C", "spontaneous_combustion", "high"),
    ("CO/O2 deficiency ratio increased significantly indicating early stages of spontaneous heating", "spontaneous_combustion", "high"),
    ("Combustion products detected near conveyor belt drive roller due to friction accumulation of coal dust", "spontaneous_combustion", "critical"),
    ("Accumulation of dry coal dust under tension pulley near transfer chute, clearing ordered", "spontaneous_combustion", "medium"),
    ("Water spray on conveyor transfer point operating with adequate pressure at 3 bar", "spontaneous_combustion", "low"),

    # Inundation & Water Inrush
    ("Sudden water inflow of 800 gallons per minute broke through barrier adjoining old waterlogged workings", "inundation", "critical"),
    ("Water seepage rate in sump gallery increased sharply after heavy monsoon rainfall", "inundation", "high"),
    ("Advance exploratory borehole encountered pressurized water jet at 28 meters depth", "inundation", "high"),
    ("Main underground dewatering pump station failed due to motor winding burnout, water rising at 5cm/hr", "inundation", "high"),
    ("Drainage ditch along main level partially silted, water ponding over rail track", "inundation", "medium"),
    ("Routine water level in main sump at 45% capacity, submersible pump on automatic cycle", "inundation", "low"),

    # Machinery & Mechanical Failure
    ("Haulage rope severed under tension during man-riding train ascent on 1 in 6 incline", "machinery_failure", "critical"),
    ("Continuous miner cutter drum gearbox seized during extraction, oil leakage noted", "machinery_failure", "high"),
    ("Armored face conveyor chain jammed with trapped oversized stone chunk", "machinery_failure", "medium"),
    ("Emergency braking system on winding engine failed monthly test deceleration test", "machinery_failure", "critical"),
    ("Conveyor belt longitudinal tear of 2 meters caused by fallen iron scraper", "machinery_failure", "high"),
    ("Front loader steering hydraulic hose cracked and weeping fluid during shift inspection", "machinery_failure", "medium"),
    ("Routine grease lubrication completed on shaker screen bearings, vibration levels normal", "machinery_failure", "low"),

    # Electrical & Explosion Proofing
    ("Flameproof FLP enclosure casing found with missing bolts on 3.3kV gate end box underground", "electrical_short_circuit", "critical"),
    ("Trailing cable of shuttle car punctured by track sleeper with copper conductors exposed", "electrical_short_circuit", "high"),
    ("Earth leakage circuit breaker failed to trip during simulated test on 550V distribution board", "electrical_short_circuit", "high"),
    ("Sparking observed at brush contacts of auxiliary fan motor in return air zone", "electrical_short_circuit", "critical"),
    ("Slight discoloration on cable terminal box terminals due to loose lug connection", "electrical_short_circuit", "medium"),
    ("Transformer oil level checked and found within statutory markings, dielectric strength tested", "electrical_short_circuit", "low"),

    # Opencast Slope Stability
    ("Tension crack measuring 12 meters length and 15cm width developed on crest of overburden dump", "slope_instability", "critical"),
    ("Bench face angle measured at 65 degrees exceeding statutory maximum limit of 55 degrees", "slope_instability", "high"),
    ("Slumping and toe heave observed along western haul road edge beneath bench 3", "slope_instability", "high"),
    ("Minor ravelling of rock fragments observed on intermediate bench following night rainfall", "slope_instability", "medium"),
    ("Haul road berm height maintained at 1.5 times the tyre diameter of dumpers", "slope_instability", "low"),

    # Coal Dust Hazard
    ("Heavy accumulation of fine airborne coal dust on roadway roof beams without inert stone dust barriers", "dust_explosion", "critical"),
    ("Stone dust barrier shelves missing required 30 kg/m2 stone dust charge per CMR regulation", "dust_explosion", "high"),
    ("Water sprinkler nozzles clogged along 80 meters length of coal handling conveyor gallery", "dust_explosion", "high"),
    ("Incombustible matter content in roadway dust samples tested at 58%, below statutory 75% requirement", "dust_explosion", "high"),
    ("Dust suppression fogger mist spray operating satisfactorily at rotary coal tippler", "dust_explosion", "low"),
]


def train_and_save_model():
    """Execute training pipeline, evaluate performance, and persist model artifacts."""
    output_dir = os.path.join(os.path.dirname(__file__), "saved_model")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loaded {len(TRAINING_DATA)} statutory domain safety samples.")
    texts, categories, severities = zip(*TRAINING_DATA)

    # 1. Train Category Classifier
    X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(
        texts, categories, test_size=0.25, random_state=42, stratify=categories
    )

    category_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=1200, sublinear_tf=True)),
        ("clf", LogisticRegression(C=2.5, max_iter=300, random_state=42))
    ])

    category_pipeline.fit(X_train_cat, y_train_cat)
    cat_preds = category_pipeline.predict(X_test_cat)
    cat_acc = accuracy_score(y_test_cat, cat_preds)
    cat_f1 = f1_score(y_test_cat, cat_preds, average="weighted")
    print(f"[Model Training] Hazard Category Classifier Accuracy: {cat_acc:.2%}, F1: {cat_f1:.2%}")

    # 2. Train Severity Classifier
    X_train_sev, X_test_sev, y_train_sev, y_test_sev = train_test_split(
        texts, severities, test_size=0.25, random_state=42, stratify=severities
    )

    severity_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=1200, sublinear_tf=True)),
        ("clf", GradientBoostingClassifier(n_estimators=75, learning_rate=0.1, max_depth=3, random_state=42))
    ])

    severity_pipeline.fit(X_train_sev, y_train_sev)
    sev_preds = severity_pipeline.predict(X_test_sev)
    sev_acc = accuracy_score(y_test_sev, sev_preds)
    sev_f1 = f1_score(y_test_sev, sev_preds, average="weighted")
    print(f"[Model Training] Hazard Severity Predictor Accuracy: {sev_acc:.2%}, F1: {sev_f1:.2%}")

    # Retrain on full dataset for maximum deployment coverage
    category_pipeline.fit(texts, categories)
    severity_pipeline.fit(texts, severities)

    # Persist serialized artifacts
    model_bundle = {
        "category_model": category_pipeline,
        "severity_model": severity_pipeline,
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "training_samples_count": len(TRAINING_DATA),
        "classes": {
            "categories": sorted(list(set(categories))),
            "severities": ["low", "medium", "high", "critical"],
        },
        "metrics": {
            "category_accuracy": round(float(cat_acc), 4),
            "category_f1": round(float(cat_f1), 4),
            "severity_accuracy": round(float(sev_acc), 4),
            "severity_f1": round(float(sev_f1), 4),
        }
    }

    model_file = os.path.join(output_dir, "coal_mine_hazard_classifier.joblib")
    joblib.dump(model_bundle, model_file, compress=3)
    print(f"[OK] Trained AI Model saved to: {model_file}")

    # Save human-readable metadata JSON for UI and diagnostics
    meta_file = os.path.join(output_dir, "model_metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "model_name": "Coal Mine Statutory Hazard & Risk Predictor",
            "model_architecture": "Hybrid TF-IDF + LogisticRegression / GradientBoosting",
            "statutory_scope": "Coal Mines Regulations (CMR) 2017 & DGMS Safety Framework",
            "trained_at": model_bundle["trained_at"],
            "training_samples": len(TRAINING_DATA),
            "metrics": model_bundle["metrics"],
            "supported_categories": model_bundle["classes"]["categories"],
            "supported_severities": model_bundle["classes"]["severities"],
        }, f, indent=2)
    print(f"[OK] Model metadata saved to: {meta_file}")

    return model_bundle


if __name__ == "__main__":
    train_and_save_model()
