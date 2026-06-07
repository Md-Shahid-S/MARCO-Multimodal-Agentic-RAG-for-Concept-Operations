# test_multimodal_processing.py
import json
import os
import sys
from multimodal.agent import preprocess_artifact

def test_yaml_processing():
    print("--- Testing YAML Processing ---")
    yaml_path = "test_pipeline.yml"
    if not os.path.exists(yaml_path):
        print(f"Error: {yaml_path} not found.")
        return

    result = preprocess_artifact(yaml_path)
    print(f"Artifact Type: {result.get('artifact_type')}")
    print(f"Query Enrichment: {result.get('query_enrichment')}")
    print("\nNormalised Concepts:")
    for concept in result.get("normalised_concepts", {}).get("concepts", []):
        print(f"  - {concept.get('devops_concept')} <-> {concept.get('msa_concept')} ({concept.get('taxonomy_category')})")
    
    print("\nMissing Elements:")
    for missing in result.get("normalised_concepts", {}).get("missing", []):
        print(f"  - {missing}")
    print("-" * 30)

def test_terraform_processing():
    print("\n--- Testing Terraform Processing ---")
    tf_content = """
resource "aws_ecs_service" "main" {
  name            = "hello-world"
  cluster         = "my-cluster"
  task_definition = "my-task"
  desired_count   = 3
}

resource "aws_api_gateway_rest_api" "api" {
  name = "my-api"
}

resource "vault_secret" "db_password" {
  path = "secret/db"
  data_json = jsonencode({
    password = "supersecret"
  })
}
"""
    tf_path = "sample_test.tf"
    with open(tf_path, "w") as f:
        f.write(tf_content)

    try:
        result = preprocess_artifact(tf_path)
        print(f"Artifact Type: {result.get('artifact_type')}")
        print(f"Query Enrichment: {result.get('query_enrichment')}")
        print("\nNormalised Concepts:")
        for concept in result.get("normalised_concepts", {}).get("concepts", []):
            print(f"  - {concept.get('devops_concept')} <-> {concept.get('msa_concept')} ({concept.get('taxonomy_category')})")
        
        print("\nMissing Elements:")
        for missing in result.get("normalised_concepts", {}).get("missing", []):
            print(f"  - {missing}")
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)
    print("-" * 30)

def test_vision_processing_mock():
    # Since we can't easily run Gemini Vision without real API keys and images in this environment,
    # we can explain how it would work based on the code.
    print("\n--- Vision Processing (Explanation) ---")
    print("The Vision Processor (multimodal/vision_processor.py) uses Google Gemini 2.0 Flash.")
    print("It takes an image (PNG, JPG) or PDF of an architecture diagram.")
    print("The prompt (DIAGRAM_PROMPT) asks Gemini to identify DevOps/MSA components and map them to the taxonomy.")
    print("Example Output from Gemini would be:")
    mock_gemini_output = {
        "components": [
            {"component_name": "Kubernetes Cluster", "taxonomy_category": "Deployment Automation", "mapping_direction": "both"},
            {"component_name": "Prometheus", "taxonomy_category": "Observability", "mapping_direction": "DevOps"},
            {"component_name": "API Gateway", "taxonomy_category": "Scalability", "mapping_direction": "MSA"}
        ],
        "missing_categories": ["Security"]
    }
    print(json.dumps(mock_gemini_output, indent=2))
    print("\nThe multimodal/agent.py then normalises this using concept_normaliser.py")
    print("-" * 30)

if __name__ == "__main__":
    test_yaml_processing()
    test_terraform_processing()
    test_vision_processing_mock()
