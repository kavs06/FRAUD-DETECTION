import sys
import os
from pathlib import Path

# Add project root to sys.path so we can import rag and explainability
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

import joblib
import pandas as pd

# Import AI modules
try:
    # Initialize explainability and RAG gemini
    api_key = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY")
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

# Import and attach auth routes
from backend.auth import router as auth_router
app.include_router(auth_router)

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
            feature_importance.append({
                "feature": col,
                "impact": round(abs(X_scaled[0][i]) * 0.1, 3)
            })

        top_features = [f["feature"] for f in feature_importance]

        prompt = explainability.build_prompt(
            provider_id=provider_id,
            prediction=risk_level,
            probability=round(probability, 2),
            top_features=top_features,
            shap_values={f["feature"]: f["impact"] for f in feature_importance}
        )

        report_text = explainability.generate_explanation(
            prompt,
            max_output_tokens=800
        )

        return {
            "provider_id": provider_id,
            "fraud_score": round(probability * 100, 2),
            "prediction": prediction,
            "risk_level": risk_level,
            "top_features": top_features,
            "shap_summary": report_text,
            "feature_importance": feature_importance
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
