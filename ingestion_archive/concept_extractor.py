# ingestion/concept_extractor.py
import json, os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EXTRACT_PROMPT = """You are an expert in DevOps and Microservice Architecture (MSA).
Given the following text from an academic paper, extract ALL DevOps and MSA concepts mentioned.
For each concept, output JSON with these fields:
- devops_concept: canonical DevOps concept name (use Ontology v1.0 terms where possible)
- msa_concept: corresponding MSA concept it maps to
- definition: one sentence definition
- taxonomy_category: one of [Deployment Automation, Observability, Scalability, Security, Configuration]
- evidence_type: "empirical" or "conceptual"
- source_title: paper title

Return ONLY a JSON array. No other text.

Text:
{text}"""

def extract_concepts(text: str, paper_meta: dict) -> list[dict]:
    # Truncate to avoid token limits. Llama-3-70b-versatile usually handles ~8k context.
    # The system dictates 4000 characters to be safe for a single prompt iteration.
    truncated = text[:4000]
    prompt = EXTRACT_PROMPT.format(text=truncated)
    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        concepts = json.loads(raw)
        
        # Add metadata source
        for c in concepts:
            c["source_arxiv_id"] = paper_meta.get("arxiv_id", "")
            c["source_title"] = paper_meta.get("title", "")
        return concepts
    except Exception as e:
        print(f"[concept_extractor] Error extracting from '{paper_meta.get('title', 'Unknown')}': {e}")
        return []

if __name__ == "__main__":
    # Test block
    res = extract_concepts("This paper discusses continuous integration and kubernetes deployments for auto-scaling.", {"title": "Test Paper", "arxiv_id": "test_id"})
    print("Test extraction:", res)
