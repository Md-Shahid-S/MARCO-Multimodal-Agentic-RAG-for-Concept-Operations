# baseline/main.py
import os, json
from rag_engine import run_retriever
from proposed_solution.agents.state import MARCOState # For structure
from dotenv import load_dotenv

load_dotenv()

def run_baseline_query(query: str):
    print(f"Running Baseline RAG for: {query}")
    state: MARCOState = {
        "original_query":      query,
        "artifact_context":    "",
        "intent":              "",
        "sub_questions":       [query],
        "taxonomy_categories": [],
        "retrieved_candidates":[],
        "retrieval_attempt":   0,
        "graded_candidates":   [],
        "hallucination_risk":  False,
        "retry_needed":        False,
        "retry_reason":        "",
        "final_mappings":      [],
        "reasoning_trace":     [],
        "confidence_scores":   []
    }
    
    # Run the retriever logic (Dense + BM25 + Cross-Encoder Rerank)
    result = run_retriever(state)
    
    print("\n--- BASE PAPER RECOMMENDATIONS ---")
    for i, c in enumerate(result["retrieved_candidates"]):
        print(f"{i+1}. {c.get('devops_concept','')} ⟷ {c.get('msa_concept','')}")
        print(f"   Score: {c.get('rerank_score', 0.0):.3f}")
        print(f"   Source: {c.get('source_title', 'Base Paper Dataset')}")
        print("-" * 20)

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "How do I monitor microservices?"
    run_baseline_query(q)
