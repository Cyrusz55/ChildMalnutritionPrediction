from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
import os
import joblib
import numpy as np
import pandas as pd

from apps.schemas import  ChildMalnutritionInput, MalnutritionPredictionResponse

from machine_learning.machine_learning import (
    load_model,
    predict_malnutrition,
)
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "API is healthy"}

@router.post("/predict", response_model=MalnutritionPredictionResponse)
def predict(input_data: dict):
    """Accept a raw dict (avoids FastAPI auto-422 on missing fields), validate with Pydantic
    and return a structured response. If validation fails, return 422 with readable errors.
    """
    # Validate and compute engineered features via the Pydantic model
    try:
        valid = ChildMalnutritionInput.model_validate(input_data)
    except ValidationError as e:
        # Return structured 422 so frontend can display validation messages
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        model = load_model()
        df = pd.DataFrame([valid.model_dump()])
        # Try to get probability if available
        proba = None
        try:
            proba = model.predict_proba(df)[:, 1][0]
        except Exception:
            pass

        pred = predict_malnutrition(model, df)[0]

        # Map prediction to labels expected by response model
        prediction_label = "Malnourished" if int(pred) == 1 else "Not malnourished"

        # Compute risk level and confidence
        confidence = float(proba) if proba is not None else (1.0 if int(pred) == 1 else 0.0)
        if proba is not None:
            if proba < 0.3:
                risk_level = "Low"
            elif proba <= 0.6:
                risk_level = "Medium"
            else:
                risk_level = "High"
        else:
            risk_level = "High" if pred == 1 else "Low"

        # Identify active engineered risk factors
        risk_factors = []
        for rf in ["poverty_indicator", "poor_sanitation", "poor_water", "unsafe_housing", "mother_vulnerable", "child_health_risk", "poverty_sanitation_risk"]:
            if rf in df.columns and int(df.iloc[0].get(rf, 0)) == 1:
                risk_factors.append(rf)

        return MalnutritionPredictionResponse(
            malnutrition_risk=confidence,
            prediction=prediction_label,
            risk_level=risk_level,
            confidence=confidence,
            risk_factors=risk_factors,
            status="success",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Model not found")
    except Exception as e:
        print(f"DEBUG: Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
def model_info():
    path = os.getenv("MODEL_PATH", "models/malnutrition_model.joblib")

    if not os.path.exists(path):
        return {"status": "no model found"}
    model = joblib.load(path)
    return{
        "status": "model loaded",
        "model_type": type(model.named_steps['model']).__name__,
        "model_params": model.named_steps['model'].get_params()

    }