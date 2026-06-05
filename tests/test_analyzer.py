import sys
from unittest.mock import MagicMock

# 1. Globally mock mlflow before importing app modules to prevent initialization crashes
sys.modules['mlflow'] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from app.analyzer import ABAnalyzer
from app.main import app

# Initialize the clean FastAPI TestClient wrapper
client = TestClient(app)

# 2. Core ABAnalyzer Logic Tests (100% Analyzer Coverage)
def test_z_test_significant():
    results = ABAnalyzer.run_z_test(100, 1000, 150, 1000)
    assert results["significant"] is True
    assert results["lift"] > 0

def test_z_test_not_significant():
    results = ABAnalyzer.run_z_test(100, 1000, 105, 1000)
    assert results["significant"] is False

def test_bayesian_recommendation():
    results = ABAnalyzer.run_bayesian_analysis(100, 1000, 200, 1000)
    assert results["recommendation"] == "SHIP"

def test_srm_detected():
    results = ABAnalyzer.check_srm(1000, 1500)
    assert results["srm_detected"] is True

def test_srm_not_detected():
    results = ABAnalyzer.check_srm(1000, 1005)
    assert results["srm_detected"] is False

# 3. Core FastAPI Endpoint Tests (Sweeps app/main.py through 100%)
def test_read_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "A/B Testing Analysis API" in response.json()["message"]

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_endpoint_invalid_input():
    payload = {
        "control_conversions": 0,
        "control_users": 0,
        "treatment_conversions": 0,
        "treatment_users": 0,
        "experiment_name": "error_validation"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 400
    assert "User counts must be greater than zero" in response.json()["detail"]

def test_analyze_endpoint_success_pipeline():
    payload = {
        "control_conversions": 100,
        "control_users": 1000,
        "treatment_conversions": 150,
        "treatment_users": 1000,
        "experiment_name": "successful_experiment_run"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert "frequentist" in json_data
    assert "bayesian" in json_data
    assert "srm" in json_data  # Changed from "arm" to "srm" to match actual code response