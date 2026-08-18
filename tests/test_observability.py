import json
from app.observability.pii_redactor import PIIRedactor
from app.observability.tracer import tracer


def test_pii_redaction_email():
    redactor = PIIRedactor()
    raw = "Please send updates to alex.developer@example.com and team@fintechglobal.com."
    sanitized = redactor.redact_text(raw)
    assert "alex.developer@example.com" not in sanitized
    assert "a***@example.com" in sanitized


def test_pii_redaction_api_keys():
    redactor = PIIRedactor()
    raw = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and API key AIzaSyD3x918237498172349182374912384."
    sanitized = redactor.redact_text(raw)
    assert "[REDACTED_BEARER_TOKEN]" in sanitized
    assert "[REDACTED_API_KEY]" in sanitized


def test_pii_redaction_dict():
    redactor = PIIRedactor()
    data = {
        "customer_name": "Acme Inc",
        "contact_email": "john.doe@acme.com",
        "secret_token": "super_secret_12345",
        "notes": "Call +1-555-123-4567 for support."
    }
    sanitized = redactor.redact_dict(data)
    assert sanitized["secret_token"] == "[REDACTED_SECRET]"
    assert "john.doe@acme.com" not in sanitized["contact_email"]
    assert sanitized["customer_name"] == "Acme Inc"


def test_opentelemetry_tracer_span():
    with tracer.trace_span("test_span", {"user_email": "test@google.com", "step": 1}) as span:
        assert span is not None
        assert span.is_recording()
