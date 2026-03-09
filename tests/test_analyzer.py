import pytest
from app.analyzer import ABAnalyzer

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
