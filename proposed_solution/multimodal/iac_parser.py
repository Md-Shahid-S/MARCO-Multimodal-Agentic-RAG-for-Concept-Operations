# multimodal/iac_parser.py
import hcl2, yaml, os

IaC_CONCEPT_MAP = {
    "aws_ecs_service":       ("Container Orchestration", "Containerised Microservices"),
    "kubernetes_deployment": ("Container Orchestration", "Independent Service Deployment"),
    "aws_api_gateway":       ("API Gateway",            "API Gateway Integration"),
    "helm_release":          ("Deployment Automation",  "Service Composition"),
    "aws_cloudwatch_metric": ("Monitoring",             "Runtime Diagnostics"),
    "datadog_monitor":       ("Monitoring",             "Service-Level Telemetry"),
    "vault_secret":          ("Secrets Management",     "Secure Service Deployment"),
    "aws_waf":               ("DevSecOps",              "Access Control"),
    "terraform_backend":     ("Infrastructure as Code", "Cloud-Native Setup"),
    "null_resource":         ("Automation",             "Dynamic Service Composition"),
}

def parse_terraform(file_path: str) -> dict:
    try:
        with open(file_path, "r") as f:
            data = hcl2.load(f)
    except Exception as e:
        return {"error": f"Invalid HCL: {e}"}

    found_resources = []
    if "resource" in data:
        for resource_block in data["resource"]:
            for resource_type, instances in resource_block.items():
                for rt, (devops, msa) in IaC_CONCEPT_MAP.items():
                    if rt.lower() in resource_type.lower():
                        found_resources.append({
                            "resource_type":  resource_type,
                            "devops_concept": devops,
                            "msa_concept":    msa,
                            "taxonomy_category": "Configuration"
                        })

    return {
        "artifact_type":     "terraform_iac",
        "detected_concepts": found_resources,
        "providers":         _extract_providers(data),
        "missing_signals":   _detect_missing(found_resources)
    }

def _extract_providers(data: dict) -> list:
    providers = []
    for block in data.get("provider", []):
        providers.extend(block.keys())
    return providers

def _detect_missing(found: list) -> list:
    found_devops = {c["devops_concept"] for c in found}
    critical = {"Monitoring", "Secrets Management", "DevSecOps", "API Gateway"}
    return [f"Missing: {c}" for c in critical - found_devops]



# ... (Keep all your existing code above) ...

if __name__ == "__main__":
    import json
    import tempfile
    
    # Create a temporary dummy Terraform file for testing
    dummy_tf_content = """
    provider "aws" { region = "us-east-1" }
    resource "aws_ecs_service" "backend_service" { name = "marco-backend" }
    resource "vault_secret" "db_credentials" { path = "secret/database" }
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(dummy_tf_content)
        temp_path = f.name

    print(f"🔍 Running MARCO IaC Preprocessor...")
    print("-" * 50)
    
    try:
        result = parse_terraform(temp_path)
        print(json.dumps(result, indent=2))
    finally:
        os.remove(temp_path) # Clean up the temp file