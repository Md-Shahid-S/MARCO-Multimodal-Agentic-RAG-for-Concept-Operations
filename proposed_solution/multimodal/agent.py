# multimodal/agent.py
from pathlib import Path
from multimodal.vision_processor import process_image
from multimodal.yaml_parser import parse_cicd_yaml
from multimodal.iac_parser import parse_terraform
from multimodal.concept_normaliser import normalise_to_ontology

SUPPORTED_EXTENSIONS = {
    ".png": "diagram", ".jpg": "diagram", ".jpeg": "diagram",
    ".pdf": "diagram",
    ".yml": "yaml",  ".yaml": "yaml",
    ".tf":  "terraform"
}

def preprocess_artifact(file_path: str) -> dict:
    """Main entry point — dispatches to correct parser based on file type."""
    path = Path(file_path)
    ext  = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return {"error": f"Unsupported file type: {ext}",
                "supported": list(SUPPORTED_EXTENSIONS.keys())}

    artifact_type = SUPPORTED_EXTENSIONS[ext]

    if artifact_type == "diagram":
        raw = process_image(file_path, prompt_type="diagram")
    elif artifact_type == "yaml":
        raw = parse_cicd_yaml(file_path)
    elif artifact_type == "terraform":
        raw = parse_terraform(file_path)

    # Normalise all extracted concepts against Ontology v1.0
    normalised = normalise_to_ontology(raw)

    return {
        "artifact_path":  file_path,
        "artifact_type":  artifact_type,
        "raw_extraction": raw,
        "normalised_concepts": normalised,
        "query_enrichment": _build_query_context(normalised)
    }

def _build_query_context(normalised: dict) -> str:
    """Convert parsed artifact into a text query enrichment for the Planner."""
    if "error" in normalised:
        return f"Error parsing artifact: {normalised['error']}"

    concepts = normalised.get("concepts", [])
    missing  = normalised.get("missing", [])
    parts = []
    
    if concepts:
        names = [c["devops_concept"] for c in concepts[:8] if isinstance(c, dict) and "devops_concept" in c]
        if names:
            parts.append(f"Detected DevOps/MSA components: {', '.join(names)}.")
            
    if missing:
        parts.append(f"Missing from architecture: {', '.join(missing[:5])}.")
        
    return " ".join(parts) if parts else "No concepts extracted from artifact."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = preprocess_artifact(sys.argv[1])
        import json
        print(json.dumps(res, indent=2))
    else:
        print("Provide a file path to test (e.g., test.tf or test.yml)")
