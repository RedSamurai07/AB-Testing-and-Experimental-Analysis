import pytest
from unittest.mock import patch, MagicMock
from app.analyzer import ABAnalyzer
from app import main
from app.main import AnalysisRequest, read_root, health_check, analyze

# --- Foundational Unit Tests ---
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

# --- Core FastAPI Function Testing (Sweeps app/main.py completely) ---

@pytest.mark.asyncio
async def test_read_root_direct():
    """Covers line execution for the root landing function."""
    res = await read_root()
    assert "A/B Testing Analysis API" in res["message"]

@pytest.mark.asyncio
async def test_health_check_direct():
    """Covers line execution for the /health function."""
    res = await health_check()
    assert res["status"] == "healthy"

@pytest.mark.asyncio
async def test_analyze_invalid_input_validation():
    """Triggers the input evaluation constraint error gate directly."""
    req = AnalysisRequest(
        control_conversions=0,
        control_users=0,
        treatment_conversions=0,
        treatment_users=0,
        experiment_name="test"
    )
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await analyze(req)
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
@patch('app.main.mlflow')
async def test_analyze_valid_pipeline_execution(mock_mlflow):
    """Mocks out mlflow engine to successfully walk through every statement of calculation."""
    # Mock context managers for mlflow.start_run()
    mock_run = MagicMock()
    mock_mlflow.start_run.return_with = mock_run
    
    req = AnalysisRequest(
        control_conversions=100,
        control_users=1000,
        treatment_conversions=120,
        treatment_users=1000,
        experiment_name="success_experiment"
    )
    
    res = await analyze(req)
    assert "frequentist" in res
    assert "bayesian" in res