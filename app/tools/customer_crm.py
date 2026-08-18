from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from app.memory.state_manager import (
    CustomerProfile,
    LookupCustomerInput,
    RegisterCustomerInput,
    ToolErrorResponse,
    ToolStatus,
)
from app.observability.tracer import tracer

# Pre-populated CRM database representing key enterprise customer archetypes
CUSTOMER_DATABASE: Dict[str, Dict[str, Any]] = {
    "fintech global": {
        "name": "FinTech Global Bank",
        "industry": "Financial Services & Banking",
        "tech_stack": ["Google Cloud", "Google Kubernetes Engine (GKE)", "Cloud Spanner", "Cloud Armor", "BigQuery"],
        "priorities": ["Security & Governance", "Audit Compliance", "Metrics & Monitoring", "Low-Latency Data Processing"],
        "tier": "Enterprise Tier 1",
        "contact_email": "cloud-arch@fintechglobal.com",
        "notes": "Highly regulated. Strict policies on LLM governance, token auditing, and Prometheus/Cloud Monitoring integration."
    },
    "fintech global bank": {
        "name": "FinTech Global Bank",
        "industry": "Financial Services & Banking",
        "tech_stack": ["Google Cloud", "Google Kubernetes Engine (GKE)", "Cloud Spanner", "Cloud Armor", "BigQuery"],
        "priorities": ["Security & Governance", "Audit Compliance", "Metrics & Monitoring", "Low-Latency Data Processing"],
        "tier": "Enterprise Tier 1",
        "contact_email": "cloud-arch@fintechglobal.com",
        "notes": "Highly regulated. Strict policies on LLM governance, token auditing, and Prometheus/Cloud Monitoring integration."
    },
    "streammedia ai": {
        "name": "MediaStream Studios",
        "industry": "Digital Media & Entertainment",
        "tech_stack": ["Vertex AI", "Gemini 1.5 Pro", "Gemini 2.5 Flash", "Cloud Storage", "Cloud Run"],
        "priorities": ["Agentic Video Processing", "Multimodal GenAI", "Partner Models (Claude/Llama)", "High-Throughput Content Generation"],
        "tier": "Enterprise Growth",
        "contact_email": "ai-team@mediastreamstudios.com",
        "notes": "Focused on media indexing, automated video understanding, and multi-model routing."
    },
    "mediastream studios": {
        "name": "MediaStream Studios",
        "industry": "Digital Media & Entertainment",
        "tech_stack": ["Vertex AI", "Gemini 1.5 Pro", "Gemini 2.5 Flash", "Cloud Storage", "Cloud Run"],
        "priorities": ["Agentic Video Processing", "Multimodal GenAI", "Partner Models (Claude/Llama)", "High-Throughput Content Generation"],
        "tier": "Enterprise Growth",
        "contact_email": "ai-team@mediastreamstudios.com",
        "notes": "Focused on media indexing, automated video understanding, and multi-model routing."
    },
    "devops cloudworks": {
        "name": "DevOps CloudWorks",
        "industry": "Developer Tooling & SaaS",
        "tech_stack": ["CodeMender CLI", "Cloud Build", "Artifact Registry", "Terraform", "Google ADK"],
        "priorities": ["Developer Productivity", "Sandboxed Agent Tool Execution", "CI/CD Automation", "CLI Tooling"],
        "tier": "Standard Enterprise",
        "contact_email": "engineering@devopscloudworks.com",
        "notes": "Looking to automate coding agent workflows with strict workstation sandboxing."
    },
    "retail pulse": {
        "name": "Retail Pulse",
        "industry": "E-Commerce & Retail",
        "tech_stack": ["Gemini Enterprise Agent Platform", "Vertex AI Search", "Cloud SQL", "Pub/Sub"],
        "priorities": ["Customer Feedback Analysis", "Conversational Support Agents", "Latency Optimization", "Agent Observability"],
        "tier": "Enterprise Tier 1",
        "contact_email": "infra@retailpulse.com",
        "notes": "Deploying customer-facing conversational agents and sentiment feedback collection."
    }
}


def lookup_customer_profile(customer_name: str) -> Union[CustomerProfile, ToolErrorResponse]:
    """Retrieves customer profile, tech stack, industry, and architectural priorities from CRM.
    
    Args:
        customer_name: Name of the customer organization to look up.
        
    Returns:
        CustomerProfile with full organization metadata, or ToolErrorResponse with recovery steps.
        
    Recovery Guidance:
        If an error occurs or customer is unknown, use register_or_update_customer_profile to create a new profile.
    """
    with tracer.trace_span("lookup_customer_profile", {"customer_name": customer_name}):
        try:
            # Validate input schema
            validated_input = LookupCustomerInput(customer_name=customer_name)
        except ValidationError as e:
            tracer.warning("crm_validation_error", f"Invalid customer lookup input: {str(e)}")
            return ToolErrorResponse(
                error_type="INVALID_INPUT_ARGUMENT",
                error_message=f"Customer name validation failed: {str(e)}",
                recovery_instructions="Provide a valid customer organization name with at least 2 characters (e.g. 'FinTech Global Bank' or 'Retail Pulse').",
                suggested_action="lookup_customer_profile",
                valid_options=list(CUSTOMER_DATABASE.keys())
            )
            
        key = validated_input.customer_name.strip().lower()
        if key in CUSTOMER_DATABASE:
            data = CUSTOMER_DATABASE[key]
            tracer.info("crm_lookup_success", f"Found existing CRM profile for {customer_name}", profile=data)
            return CustomerProfile(**data)
        
        # Fuzzy match
        for k, v in CUSTOMER_DATABASE.items():
            if k in key or key in k or any(part in key for part in k.split() if len(part) > 4):
                tracer.info("crm_lookup_fuzzy", f"Matched '{customer_name}' to '{v['name']}'", profile=v)
                return CustomerProfile(**v)
        
        # Dynamic profile fallback
        dynamic_profile = {
            "name": customer_name.strip().title(),
            "industry": "Technology & Cloud Computing",
            "tech_stack": ["Google Cloud Platform", "Gemini Enterprise", "Cloud Run"],
            "priorities": ["AI Innovation", "Cloud Cost Optimization", "Developer Productivity", "Security"],
            "tier": "Standard Enterprise",
            "contact_email": f"team@{customer_name.strip().lower().replace(' ', '')}.com",
            "notes": "Custom generated enterprise profile based on user prompt."
        }
        tracer.info("crm_dynamic_profile", f"Created dynamic profile for new customer: {customer_name}", profile=dynamic_profile)
        return CustomerProfile(**dynamic_profile)


def register_or_update_customer_profile(
    name: Optional[str] = None,
    customer_name: Optional[str] = None,
    industry: str = "Technology & Cloud Computing",
    tech_stack: Optional[List[str]] = None,
    priorities: Optional[List[str]] = None,
    tier: str = "Standard Enterprise",
    contact_email: Optional[str] = None,
    notes: Optional[str] = None
) -> Union[CustomerProfile, ToolErrorResponse]:
    """Registers or updates a customer profile in the CRM database.
    
    Args:
        name: Official name of the customer organization.
        customer_name: Alias for name.
        industry: Primary industry vertical.
        tech_stack: List of Google Cloud / partner services used.
        priorities: Architectural priorities.
        tier: Customer account tier.
        contact_email: Primary contact email.
        notes: Special requirements.
        
    Returns:
        CustomerProfile containing the updated profile, or ToolErrorResponse with recovery steps.
    """
    target_name = (name or customer_name or "").strip()
    with tracer.trace_span("update_customer_profile", {"name": target_name}):
        try:
            validated = RegisterCustomerInput(
                name=target_name,
                industry=industry,
                tech_stack=tech_stack or ["Google Cloud Platform"],
                priorities=priorities or ["Cloud Modernization"],
                tier=tier,
                contact_email=contact_email,
                notes=notes
            )
        except ValidationError as e:
            tracer.warning("crm_update_validation_error", f"Invalid register input: {str(e)}")
            return ToolErrorResponse(
                error_type="VALIDATION_ERROR",
                error_message=f"Could not register customer profile: {str(e)}",
                recovery_instructions="Ensure 'name' is non-empty string, 'tech_stack' is a list of technology names, and 'priorities' is a list of strings.",
                suggested_action="register_or_update_customer_profile"
            )
            
        key = validated.name.lower()
        profile_dict = validated.model_dump()
        CUSTOMER_DATABASE[key] = profile_dict
        tracer.info("crm_profile_updated", f"Successfully registered/updated profile for {validated.name}", profile=profile_dict)
        return CustomerProfile(**profile_dict)
