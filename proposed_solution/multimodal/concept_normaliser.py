# multimodal/concept_normaliser.py
def normalise_to_ontology(raw: dict) -> dict:
    """Standardizes parsed dictionary shapes into a consistent ontology format for the Planner."""
    if "error" in raw:
        return {"concepts": [], "missing": [], "error": raw["error"]}

    concepts = []
    missing = []

    if raw.get("artifact_type") == "cicd_yaml" or raw.get("artifact_type") == "terraform_iac":
        concepts = raw.get("detected_concepts", [])
        missing = raw.get("missing_signals", [])
    else:
        # Expected structure from vision_processor
        raw_components = raw.get("components", raw.get("present_signals", []))
        if isinstance(raw_components, list):
            for c in raw_components:
                # Normalise image output to expected keys
                if isinstance(c, dict):
                    concepts.append({
                        "devops_concept": c.get("component_name", c.get("signal_name", "Unknown")),
                        "msa_concept": "Unknown (derived from vision)",
                        "taxonomy_category": c.get("taxonomy_category", "Unknown")
                    })
                elif isinstance(c, str):
                    concepts.append({
                        "devops_concept": c,
                        "msa_concept": "Unknown",
                        "taxonomy_category": "Unknown"
                    })
        
        missing = raw.get("missing_categories", raw.get("missing_signals", []))

    return {
        "concepts": concepts,
        "missing": missing
    }
