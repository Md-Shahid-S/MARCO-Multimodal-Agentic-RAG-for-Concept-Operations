# multimodal/yaml_parser.py
import yaml, re

CICD_CONCEPT_MAP = {
    "stages":      ("CI/CD",             "Service Deployment Pipeline"),
    "deploy":      ("Deployment Automation", "Automated Service Deployment"),
    "test":        ("Automated Testing", "Microservice Load Testing"),
    "docker":      ("Containerisation",  "Containerised Microservices"),
    "kubernetes":  ("Container Orchestration", "Independent Service Deployment"),
    "helm":        ("Deployment Automation", "Service Composition"),
    "terraform":   ("Infrastructure as Code", "Cloud-Native Setup"),
    "monitor":     ("Monitoring",        "Runtime Diagnostics"),
    "secrets":     ("Secrets Management","Secure Service Deployment"),
    "lint":        ("Code Quality",      "Service Modularisation"),
    "scan":        ("DevSecOps",         "Access Control"),
    "cache":       ("Build Optimisation","Service Performance"),
}

def parse_cicd_yaml(file_path: str) -> dict:
    with open(file_path) as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            return {"error": f"Invalid YAML: {e}"}

    content_lower = open(file_path).read().lower()
    found_concepts = []
    for keyword, (devops_concept, msa_concept) in CICD_CONCEPT_MAP.items():
        if keyword in content_lower:
            found_concepts.append({
                "devops_concept": devops_concept,
                "msa_concept":    msa_concept,
                "source_keyword": keyword,
                "taxonomy_category": _infer_category(devops_concept)
            })

    # Detect missing critical stages
    missing = []
    critical = ["test", "deploy", "monitor", "scan"]
    for c in critical:
        if c not in content_lower:
            missing.append(f"No {c} stage detected")

    raw_stages = []
    if isinstance(data, dict):
        raw_stages = list(data.get("stages", data.get("jobs", {}).keys()))

    return {
        "artifact_type":    "cicd_yaml",
        "detected_concepts": found_concepts,
        "missing_signals":  missing,
        "raw_stages":       raw_stages
    }

def _infer_category(devops_concept: str) -> str:
    category_map = {
        "CI/CD": "Deployment Automation", "Deployment": "Deployment Automation",
        "Container": "Deployment Automation", "Infrastructure": "Configuration",
        "Monitoring": "Observability", "Secrets": "Security",
        "DevSecOps": "Security", "Testing": "Scalability"
    }
    for k, v in category_map.items():
        if k.lower() in devops_concept.lower():
            return v
    return "Deployment Automation"


# ... (Keep all your existing code above) ...

if __name__ == "__main__":
    import json
    import os
    
    # We will test it using the GitHub Actions YAML you already have
    test_file = "setup-new-org-repo.yml"
    
    print(f"🔍 Running MARCO YAML Preprocessor on: {test_file}")
    print("-" * 50)
    
    if os.path.exists(test_file):
        # Run the parser
        result = parse_cicd_yaml(test_file)
        
        # Print the result as formatted JSON for the research paper
        print(json.dumps(result, indent=2))
    else:
        print(f"⚠️ Error: Could not find '{test_file}'. Please ensure the file is in the same directory.")