variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID to deploy the Agent to."
  default     = "adk-dev-485808"
}

variable "region" {
  type        = string
  description = "The Google Cloud region for services (e.g. us-central1)."
  default     = "us-central1"
}

variable "service_name" {
  type        = string
  description = "Name of the Cloud Run agent service."
  default     = "personalized-cloud-newsletter-agent"
}

variable "container_image" {
  type        = string
  description = "Container image tag in Artifact Registry / GCR."
  default     = "gcr.io/adk-dev-485808/personalized-cloud-newsletter-agent:latest"
}

variable "fast_model" {
  type        = string
  description = "Fast model for extraction and classification."
  default     = "gemini-2.5-flash"
}

variable "reasoning_model" {
  type        = string
  description = "Reasoning model for executive synthesis and quality critic."
  default     = "gemini-1.5-pro"
}

variable "min_instances" {
  type        = number
  description = "Minimum Cloud Run instances for zero cold starts."
  default     = 1
}

variable "max_instances" {
  type        = number
  description = "Maximum Cloud Run instances."
  default     = 10
}
