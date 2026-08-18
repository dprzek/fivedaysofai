import json
from typing import Any, Dict, Optional
from app.memory.state_manager import CustomerProfile
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


def lookup_customer_profile(customer_name: str) -> Dict[str, Any]:
    """Retrieves customer profile, tech stack, industry, and architectural priorities from CRM.
    
    Args:
        customer_name: Name of the customer organization to look up.
        
    Returns:
        A dictionary containing customer profile metadata or a dynamically generated profile if not found.
    """
    with tracer.trace_span("lookup_customer_profile", {"customer_name": customer_name}):
        key = customer_name.strip().lower()
        if key in CUSTOMER_DATABASE:
            data = CUSTOMER_DATABASE[key]
            tracer.info("crm_lookup_success", f"Found existing CRM profile for {customer_name}", profile=data)
            return data
        
        # Fuzzy / partial match
        for k, v in CUSTOMER_DATABASE.items():
            if k in key or key in k or any(part in key for part in k.split() if len(part) > 4):
                tracer.info("crm_lookup_fuzzy", f"Matched '{customer_name}' to '{v['name']}'", profile=v)
                return v
        
        # Dynamic profile generation for unknown customer
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
        return dynamic_profile


def register_or_update_customer_profile(
    name: Optional[str] = None,
    customer_name: Optional[str] = None,
    industry: str = "Technology",
    tech_stack: Optional[list] = None,
    priorities: Optional[list] = None,
    tier: str = "Standard Enterprise",
    contact_email: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Registers or updates a customer profile in the CRM database."""
    target_name = (name or customer_name or "Enterprise Customer").strip()
    with tracer.trace_span("update_customer_profile", {"name": target_name}):
        key = target_name.lower()
        profile_data = {
            "name": target_name,
            "industry": industry.strip(),
            "tech_stack": tech_stack or ["Google Cloud"],
            "priorities": priorities or ["Cloud Modernization"],
            "tier": tier,
            "contact_email": contact_email or f"team@{key.replace(' ', '')}.com",
            "notes": notes or "Updated by agent during customer onboarding."
        }
        CUSTOMER_DATABASE[key] = profile_data
        tracer.info("crm_profile_updated", f"Successfully registered/updated profile for {target_name}", profile=profile_data)
        return profile_data
