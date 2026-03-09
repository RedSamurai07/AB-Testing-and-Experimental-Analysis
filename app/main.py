from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import os
from app.analyzer import ABAnalyzer

app = FastAPI(title="A/B Testing Analysis API")

# Setup MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("AB_Testing_Analysis")

class AnalysisRequest(BaseModel):
    control_conversions: int
    control_users: int
    treatment_conversions: int
    treatment_users: int
    experiment_name: str = "default_experiment"

@app.get("/")
def read_root():
    return {"message": "A/B Testing Analysis API is running. Use /analyze for POST requests."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze(request: AnalysisRequest):
    if request.control_users <= 0 or request.treatment_users <= 0:
        raise HTTPException(status_code=400, detail="User counts must be greater than zero")
        
    # Run analyses
    z_results = ABAnalyzer.run_z_test(
        request.control_conversions, request.control_users,
        request.treatment_conversions, request.treatment_users
    )
    
    bayesian_results = ABAnalyzer.run_bayesian_analysis(
        request.control_conversions, request.control_users,
        request.treatment_conversions, request.treatment_users
    )
    
    srm_results = ABAnalyzer.check_srm(
        request.control_users, request.treatment_users
    )
    
    # Log to MLflow
    with mlflow.start_run(run_name=request.experiment_name):
        mlflow.log_params({
            "control_users": request.control_users,
            "treatment_users": request.treatment_users,
            "control_conversions": request.control_conversions,
            "treatment_conversions": request.treatment_conversions
        })
        mlflow.log_metrics({
            "p_value": z_results["p_value"],
            "lift": z_results["lift"],
            "prob_treatment_wins": bayesian_results["prob_treatment_wins"]
        })
        
    return {
        "frequentist": z_results,
        "bayesian": bayesian_results,
        "srm": srm_results
    }
