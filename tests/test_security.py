import os
from app.security.secret_manager import SecretManagerClient


def test_secret_manager_env_fallback(monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "mock-api-key-value-999")
    monkeypatch.setenv("USE_SECRET_MANAGER", "false")
    
    client = SecretManagerClient(project_id="test-project")
    secret = client.get_secret("test_api_key")
    assert secret == "mock-api-key-value-999"


def test_secret_manager_default():
    client = SecretManagerClient(project_id="test-project")
    secret = client.get_secret("non_existent_key", default="fallback_default")
    assert secret == "fallback_default"
