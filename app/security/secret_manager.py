import os
from typing import Optional
from app.observability.tracer import tracer


class SecretManagerClient:
    """Google Cloud Secret Manager client with seamless local environment fallback.
    
    Securely accesses secrets (API keys, DB connection strings, webhooks) from
    Google Cloud Secret Manager in production or falls back to environment variables in local dev.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "adk-dev-485808")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google.cloud import secretmanager
                self._client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                tracer.warning("secret_manager_init_fallback", f"Could not initialize SecretManagerServiceClient: {str(e)}")
                self._client = False
        return self._client

    def get_secret(self, secret_id: str, version_id: str = "latest", default: Optional[str] = None) -> Optional[str]:
        """Retrieves secret value from Secret Manager or environment variables."""
        with tracer.trace_span("get_secret", {"secret_id": secret_id, "version": version_id}):
            # Check local environment first if Secret Manager is disabled
            use_sm = os.getenv("USE_SECRET_MANAGER", "false").lower() == "true"
            env_val = os.getenv(secret_id.upper())
            
            if not use_sm and env_val is not None:
                tracer.info("secret_resolved_env", f"Resolved secret {secret_id} from environment variable")
                return env_val

            client = self._get_client()
            if client:
                try:
                    name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
                    response = client.access_secret_version(request={"name": name})
                    secret_val = response.payload.data.decode("UTF-8")
                    tracer.info("secret_resolved_sm", f"Resolved secret {secret_id} from Google Secret Manager")
                    return secret_val
                except Exception as e:
                    tracer.warning("secret_sm_access_failed", f"Failed to access secret {secret_id} from Secret Manager: {str(e)}. Falling back to env.")

            if env_val is not None:
                return env_val
            return default


secret_client = SecretManagerClient()
