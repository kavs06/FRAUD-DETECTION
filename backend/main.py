import logging
import sys
import os
from pathlib import Path

# Add project root to sys.path so we can import rag and explainability
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from dotenv import load_dotenv

import joblib
import pandas as pd

from services.explainability_service import ExplainabilityService
from services.report_generation_service import ReportGenerationService

# Import AI modules
load_dotenv()
try:
    # Initialize explainability and RAG gemini
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Please set it in the .env file."
        )


    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key
    
    from rag.rag_pipeline import rag_chat
    import explainability
    explainability.configure_gemini()
except Exception as e:
    print(f"Warning: Failed to import or configure AI modules: {e}")

app = FastAPI(title="Fraud Investigation Platform API")

# Load ML assets
try:
    MODEL_DIR = PROJECT_ROOT / "models"

    model = joblib.load(MODEL_DIR / "logistic_regression.pkl")
    scaler = joblib.load(MODEL_DIR / "scaler.pkl")
    feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")

    print("✅ Logistic Regression loaded")
    print("✅ Scaler loaded")
    print("✅ Feature names loaded")

except Exception as e:
    print(f"❌ Model loading failed: {e}")

explainability_service = ExplainabilityService()
report_generation_service = ReportGenerationService()

# Import and attach auth routes
from backend.auth import router as auth_router
from backend.routes.investigation import router as investigation_router
app.include_router(auth_router)
app.include_router(investigation_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    provider_id: str
    features: Dict[str, Any]

class ChatRequest(BaseModel):
    provider_id: str
    message: str

@app.post("/predict")
def predict_fraud(request: PredictRequest):

    try:
        # Create dataframe in correct feature order
        input_data = []

        for feature in feature_names:
            input_data.append(request.features.get(feature, 0))

        X = pd.DataFrame([input_data], columns=feature_names)

        # Scale data
        X_scaled = scaler.transform(X)

        # Predict
        probability = model.predict_proba(X_scaled)[0][1]
        prediction = model.predict(X_scaled)[0]

        risk_level = (
            "High" if probability > 0.8
            else "Medium" if probability > 0.5
            else "Low"
        )

        return {
            "provider_id": request.provider_id,
            "fraud_score": round(float(probability * 100), 2),
            "prediction": int(prediction),
            "risk_level": risk_level,
            "features_used": request.features
        }

    except Exception as e:
        return {
            "error": str(e)
        }

@app.get("/explain/{provider_id}")
def explain_fraud(provider_id: str):
    try:
        provider_df = pd.read_csv(PROJECT_ROOT / "notebooks" / "provider_master.csv")

        row = provider_df[provider_df["Provider"] == provider_id]

        if row.empty:
            return {"error": "Provider not found"}

        row = row.iloc[0]

        feature_cols = feature_names

        X_input = pd.DataFrame([[row.get(col, 0) for col in feature_cols]],
                               columns=feature_cols)

        X_scaled = scaler.transform(X_input)

        probability = float(model.predict_proba(X_scaled)[0][1])
        prediction = int(model.predict(X_scaled)[0])

        risk_level = (
            "High" if probability > 0.8
            else "Medium" if probability > 0.5
            else "Low"
        )

        feature_importance = []

        for i, col in enumerate(feature_cols[:4]):
            raw_value = float(X_input.iloc[0][col])
            scaled_value = float(X_scaled[0][i])
            feature_importance.append({
                "feature": col,
                "impact": round(abs(scaled_value) * 0.1, 3),
                "feature_value": raw_value,
                "baseline_value": 0.0,
            })

        top_features = [f["feature"] for f in feature_importance]

        prompt = explainability.build_prompt(
            provider_id=provider_id,
            prediction=risk_level,
            probability=round(probability, 2),
            top_features=top_features,
            shap_values={f["feature"]: f["impact"] for f in feature_importance}
        )

        explanation_fallback = False
        explanation_error = None
        try:
            report_text = explainability.generate_explanation(
                prompt,
                max_output_tokens=800
            )
        except Exception as exc:
            explanation_fallback = True
            explanation_error = str(exc)
            report_text = (
                "The Explainability service is temporarily unavailable. "
                "A grounded report was generated from the available structured inputs."
            )
            logger.warning("Explainability generation failed for %s: %s", provider_id, exc)

        structured_payload = explainability_service.build_explanation_payload(
            provider_id=provider_id,
            prediction=risk_level,
            probability=probability,
            feature_contributions=[
                {
                    "feature_name": item["feature"],
                    "shap_value": item["impact"],
                    "feature_value": item.get("feature_value"),
                    "baseline_value": item.get("baseline_value"),
                }
                for item in feature_importance
            ],
            explanation_text=report_text,
        )

        report_context = {
            "provider_id": provider_id,
            "fraud_prediction": {
                "label": risk_level,
                "prediction": prediction,
                "probability": round(probability, 4),
            },
            "investigation_findings": [
                {"source": "provider", "summary": "Provider-level risk factors were evaluated."},
                {"source": "claim", "summary": "Claim-level signals were reviewed."},
            ],
            "fraud_hypotheses": [
                {"hypothesis": "Billing anomaly pattern", "confidence": round(probability, 4)},
            ],
            "shap_explanations": structured_payload["structured_explanation"]["features"],
            "confidence_scores": {
                "probability": round(probability, 4),
                "model_confidence": risk_level,
            },
        }
        generated_report = report_generation_service.generate_report(report_context)

        return {
            "provider_id": provider_id,
            "fraud_score": round(probability * 100, 2),
            "prediction": prediction,
            "risk_level": risk_level,
            "top_features": top_features,
            "shap_summary": report_text,
            "feature_importance": feature_importance,
            "structured_explanation": structured_payload["structured_explanation"],
            "plots": structured_payload["plots"],
            "report_generation": {
                "markdown_report": generated_report["markdown_report"],
                "structured_report": generated_report["structured_report"],
                "fallback_used": explanation_fallback,
                "explanation_error": explanation_error,
            },
            "explanation_generation": {
                "fallback_used": explanation_fallback,
                "error": explanation_error,
                "report_text": report_text,
            },
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
def chatbot_interaction(request: ChatRequest):
    try:
        # Run real RAG pipeline
        response_text = rag_chat(request.message)
    except Exception as e:
        response_text = f"Failed to connect to RAG pipeline: {e}"
        
    return {
        "response": response_text
    }

@app.get("/")
def read_root():
    return {"message": "Fraud Investigation API is running"}

@app.get("/test-key")
def test_key():
    import os
    return {
        "gemini_key": os.getenv("GEMINI_API_KEY")
    }