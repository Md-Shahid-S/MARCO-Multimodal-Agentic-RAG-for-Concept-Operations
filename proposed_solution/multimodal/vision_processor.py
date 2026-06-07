# multimodal/vision_processor.py
import base64, os, json
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash-image"))

DIAGRAM_PROMPT = """Analyse this software architecture diagram carefully.
Identify ALL visible DevOps and MSA components, patterns, and relationships.
For each identified element, provide:
1. component_name: exact name as shown in diagram
2. taxonomy_category: one of [Deployment Automation, Observability, Scalability, Security, Configuration]
3. mapping_direction: "DevOps", "MSA", or "both"
4. missing_categories: list taxonomy categories with NO visible components

Return ONLY valid JSON with keys: components (list), missing_categories (list).
Do not include any explanation outside the JSON."""

DASHBOARD_PROMPT = """Analyse this monitoring/observability dashboard screenshot.
Identify which observability signals ARE visible (metrics, logs, traces, alerts).
Identify which observability signals are MISSING from a complete DevOps–MSA setup.
Map findings to DevOps–MSA Observability taxonomy.

Return ONLY valid JSON with keys:
- present_signals: list of visible monitoring components
- missing_signals: list of gaps vs. best practice
- taxonomy_coverage: percentage of Observability category covered (0-100)"""

def process_image(image_path: str, prompt_type: str = "diagram") -> dict:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Determine MIME type
    suffix = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".pdf": "application/pdf"}
    mime_type = mime_map.get(suffix, "image/png")

    prompt = DIAGRAM_PROMPT if prompt_type == "diagram" else DASHBOARD_PROMPT

    response = model.generate_content([
        {"mime_type": mime_type, "data": image_data},
        prompt
    ])
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)



# ... (Keep all your existing code above) ...

if __name__ == "__main__":
    import json
    
    # We will test it using the Netflix diagram
    test_image = "Netflix.png"
    
    print(f"🔍 Running MARCO Vision Preprocessor on: {test_image}")
    print("-" * 50)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ Error: GEMINI_API_KEY not found in environment variables.")
    elif os.path.exists(test_image):
        try:
            # We use the diagram prompt
            result = process_image(test_image, prompt_type="diagram")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"⚠️ Error processing image: {e}")
    else:
        print(f"⚠️ Error: Could not find '{test_image}'. Please ensure the file exists.")