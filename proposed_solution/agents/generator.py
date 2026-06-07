# agents/generator.py
import json, os
from groq import Groq
from agents.state import MARCOState
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GENERATOR_PROMPT = """You are an expert DevOps and Microservices Architect providing an Explainable RAG response. 
Your goal is to provide a comprehensive, production-grade, structured response grounded in empirical evidence.

[INPUT DATA]
- User Query: {query}
- Mapping Intent: {intent}
- Artifact Context (Visual/Code Analysis): {artifact_context} 
- Planner Clarification: {clarification_msg}
- Validated Evidence: {evidence}

[INSTRUCTIONS]
1. Explainable Analysis: Start by explaining HOW the provided Artifact Context (if any) and the Validated Evidence directly address the user's specific problem.
2. Grounded Synthesis: Provide a final resolution that synthesizes the answer. If the query is about a specific file (Artifact Context), the answer MUST reference specific lines or logic from that file.
3. Strict Scope: If the evidence does not contain a specific mapping, use 'out_of_scope_notes' to explain what is missing. Do not invent mappings.
4. Source Attribution: Every mapping MUST include the exact Source IDs from the evidence to ensure 100% traceability.
5. Narrative Citations: Never use raw document IDs (e.g., "ID: 553") in the conversational text of the context_analysis or final_resolution. Instead, synthesize the actual technical content or refer to the source's title. Reserve raw IDs strictly for the sources array in the mappings JSON.

[OUTPUT FORMAT]
Return ONLY a raw JSON object (no markdown, no preamble):
{{
  "context_analysis": "Detailed explanation of WHY this evidence matters to the specific artifact and query provided.",
  "final_resolution": "The clear, direct answer. If a clarification_msg exists and remains unresolved, weave it in as a 'for more precision, please specify...' note.",
  "mappings": [
    {{
      "devops_concept": "canonical DevOps concept",
      "msa_concept": "corresponding MSA concept",
      "justification": "Detailed explanation of how this specific mapping applies to the user's artifact.",
      "taxonomy_category": "One of: Scalability, Observability, Deployment Automation, Security, Collaboration",
      "sources": ["ID: 123", "Source Title"]
    }}
  ],
  "suggested_next_steps": ["Clarification message if provided", "Follow-up 2", "Follow-up 3"],
  "out_of_scope_notes": "Notes on technologies or concepts mentioned by the user that are NOT in our knowledge base."
}}"""

import time

def run_generator(state: MARCOState) -> MARCOState:
    accepted = [c for c in state.get("graded_candidates", []) if c.get("accepted")]
    if not accepted:
        # Fallback to top 3 if none formally passed the critic
        accepted = state.get("graded_candidates", [])[:3]

    evidence_text = "\n".join([
        f"[ID: {c.get('id', '?')} | Source: {c.get('reference_name', 'System KB')}] {c.get('devops_concept', '?')} → {c.get('msa_concept','?')}: {c.get('definition','')}"
        for c in accepted
    ])

    prompt = GENERATOR_PROMPT.format(
        query=state["original_query"],
        intent=state.get("intent", "bidirectional"),
        artifact_context=state.get("artifact_context", "No artifact provided."),
        clarification_msg=state.get("clarification_message", "None"),
        evidence=evidence_text if evidence_text else "No strong evidence found."
    )
    
    context_analysis = ""
    final_resolution = ""
    suggested_next_steps = []
    mappings = []
    out_of_scope = ""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024
            )
            raw = response.choices[0].message.content.strip()
            # Clean up any potential markdown fences
            raw = raw.replace("```json", "").replace("```", "").strip()
            output_data = json.loads(raw)
            
            context_analysis = output_data.get("context_analysis", "")
            final_resolution = output_data.get("final_resolution", "")
            suggested_next_steps = output_data.get("suggested_next_steps", [])
            mappings = output_data.get("mappings", [])
            out_of_scope = output_data.get("out_of_scope_notes", "")
            break
        except Exception as e:
            if attempt == 2:
                print(f"[Generator] Error generating mappings with Groq: {e}")
            time.sleep(2)

    state["context_analysis"]     = context_analysis
    state["final_resolution"]     = final_resolution
    state["suggested_next_steps"] = suggested_next_steps
    state["final_mappings"]       = mappings
    # out_of_scope_notes is not in MARCOState yet, but we'll include it in the trace
    
    if "reasoning_trace" not in state:
        state["reasoning_trace"] = []
        
    state["reasoning_trace"].append(
        f"[Generator] Produced {len(mappings)} mappings. "
        f"Scope Notes: {out_of_scope if out_of_scope else 'All in-scope'}"
    )
    
    # We'll store out_of_scope in a new field for the UI to read
    state["out_of_scope_notes"] = out_of_scope
    
    return state
