from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_companies_endpoint():
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 90

def test_get_company_endpoint():
    response = client.get("/api/v1/companies/HDFCBANK")
    assert response.status_code == 200
    assert response.json()["company_id"] == "HDFCBANK"

def test_invalid_company_endpoint():
    response = client.get("/api/v1/companies/INVALID999")
    assert response.status_code == 404

def test_screener_endpoint():
    response = client.get("/api/v1/screener?preset=quality")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
