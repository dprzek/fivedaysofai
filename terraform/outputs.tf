output "service_url" {
  description = "The URL of the deployed Cloud Run agent service."
  value       = google_cloud_run_v2_service.agent_service.uri
}

output "service_account_email" {
  description = "The IAM service account attached to the agent runtime."
  value       = google_service_account.agent_sa.email
}

output "secret_manager_secret_id" {
  description = "The ID of the Secret Manager secret for API keys."
  value       = google_secret_manager_secret.agent_api_key.secret_id
}
