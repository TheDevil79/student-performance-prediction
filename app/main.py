"""
FastAPI Application for Student Mathematics Performance Prediction
Loads fitted scikit-learn Pipeline at startup and provides /health and /predict endpoints.
"""

import os
import joblib
import numpy as np
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import StudentFeatures, PredictionResponse, HealthResponse

MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")
STATIC_DIR = os.getenv("STATIC_DIR", "static")

# Global reference to loaded model pipeline
model_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model pipeline into memory upon application startup."""
    global model_pipeline
    if os.path.exists(MODEL_PATH):
        try:
            print(f"[STARTUP] Loading model pipeline from '{MODEL_PATH}'...")
            model_pipeline = joblib.load(MODEL_PATH)
            print("[STARTUP] Model loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load model file '{MODEL_PATH}': {e}")
            model_pipeline = None
    else:
        print(
            f"[WARN] Model file '{MODEL_PATH}' not found.\n"
            "Please run 'python train.py' to generate and train the model."
        )
        model_pipeline = None
    yield
    print("[SHUTDOWN] Releasing resources...")


app = FastAPI(
    title="Student Performance Prediction API",
    description=(
        "Machine Learning web service to predict final mathematics grade (G3) "
        "on a 0–20 scale based on student demographic, social, and academic attributes."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_performance_tier(grade: float) -> str:
    """Classify 0-20 grade into standard qualitative tiers."""
    if grade >= 16.0:
        return "Excellent / Distinction (16-20)"
    elif grade >= 14.0:
        return "Good (14-15)"
    elif grade >= 12.0:
        return "Satisfactory (12-13)"
    elif grade >= 10.0:
        return "Sufficient / Pass (10-11)"
    else:
        return "Fail / Needs Improvement (0-9)"


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Check service status and model availability",
)
def health_check():
    """Verify API service status and whether the ML model is currently loaded."""
    is_loaded = model_pipeline is not None
    return HealthResponse(
        status="healthy" if is_loaded else "degraded",
        model_loaded=is_loaded,
        model_path=MODEL_PATH,
        version="1.0.0",
        message="Model ready for inference" if is_loaded else "Model file missing or not loaded. Run train.py.",
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Predict student final mathematics grade (G3)",
)
def predict_grade(student: StudentFeatures):
    """
    Accepts 30 student attributes and outputs predicted final mathematics grade (0–20).
    Excludes earlier exam grades (G1, G2) to evaluate true foundational factors.
    """
    if model_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Model file '{MODEL_PATH}' is not loaded or missing. "
                "Please run 'python train.py' to train and save the pipeline."
            ),
        )

    try:
        # Convert Pydantic model to a single-row DataFrame
        input_data = student.model_dump()
        input_df = pd.DataFrame([input_data])

        # Inference through scikit-learn pipeline (preprocessing + RandomForest)
        raw_prediction = float(model_pipeline.predict(input_df)[0])

        # Clamp prediction to legitimate 0–20 Portuguese grade bounds
        clamped_prediction = float(np.clip(raw_prediction, 0.0, 20.0))
        rounded_prediction = int(round(clamped_prediction))
        performance_tier = get_performance_tier(clamped_prediction)

        return PredictionResponse(
            predicted_grade=round(clamped_prediction, 2),
            rounded_grade=rounded_prediction,
            performance_level=performance_tier,
            scale_min=0.0,
            scale_max=20.0,
            status="success",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error during model prediction: {str(e)}",
        )


# Serve frontend static assets if directory exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Welcome to Student Performance Prediction API. Visit /docs for Swagger UI."}
