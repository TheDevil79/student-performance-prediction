"""
Integration and Unit Tests for Student Performance Prediction API
Uses FastAPI TestClient to validate endpoints, schemas, input bounds, and inference results.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app, model_pipeline


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient within the application lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


VALID_STUDENT_PAYLOAD = {
    "school": "GP",
    "sex": "F",
    "age": 17,
    "address": "U",
    "famsize": "GT3",
    "Pstatus": "T",
    "Medu": 4,
    "Fedu": 4,
    "Mjob": "health",
    "Fjob": "teacher",
    "reason": "reputation",
    "guardian": "mother",
    "traveltime": 1,
    "studytime": 3,
    "failures": 0,
    "schoolsup": "no",
    "famsup": "yes",
    "paid": "yes",
    "activities": "yes",
    "nursery": "yes",
    "higher": "yes",
    "internet": "yes",
    "romantic": "no",
    "famrel": 5,
    "freetime": 3,
    "goout": 2,
    "Dalc": 1,
    "Walc": 1,
    "health": 5,
    "absences": 2,
}


def test_health_endpoint(client):
    """GET /health should return 200 and report whether the model is loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "model_loaded" in data
    assert data["version"] == "1.0.0"


def test_predict_endpoint_valid_input(client):
    """POST /predict should return 200 and a realistic 0–20 score for valid student features."""
    response = client.post("/predict", json=VALID_STUDENT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_grade" in data
    assert "rounded_grade" in data
    assert "performance_level" in data
    assert 0.0 <= data["predicted_grade"] <= 20.0
    assert 0 <= data["rounded_grade"] <= 20
    assert data["status"] == "success"


def test_predict_endpoint_invalid_categorical(client):
    """POST /predict should reject invalid categorical values with 422."""
    payload = VALID_STUDENT_PAYLOAD.copy()
    payload["school"] = "INVALID_SCHOOL"  # only 'GP' or 'MS' allowed
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_out_of_bounds_numerical(client):
    """POST /predict should reject numerical values out of defined bounds with 422."""
    payload = VALID_STUDENT_PAYLOAD.copy()
    payload["age"] = 99  # Valid age is 15-22
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_missing_feature(client):
    """POST /predict should reject incomplete payload missing required fields with 422."""
    payload = VALID_STUDENT_PAYLOAD.copy()
    del payload["studytime"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_ignores_g1_g2(client):
    """Ensure earlier grades G1/G2 are not used or required; sending extra fields shouldn't crash."""
    payload = VALID_STUDENT_PAYLOAD.copy()
    payload["G1"] = 18
    payload["G2"] = 19
    response = client.post("/predict", json=payload)
    # Pydantic by default ignores extra fields or accepts them without error
    assert response.status_code == 200
