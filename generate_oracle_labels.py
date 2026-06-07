import json, sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('.'))
from proposed_solution.agents.state import MARCOState
from rag_engine import run_retriever

with open("data/base/eval_queries_50.json", "r") as f:
    queries = json.load(f)

for q in queries:
    state = {
        "original_query": q["query"], "artifact_context": "",
        "intent": "", "sub_questions": [q["query"]], "taxonomy_categories": [],
        "retrieved_candidates":[], "retrieval_attempt": 0,
        "graded_candidates": [], "hallucination_risk": False,
        "retry_needed": False, "retry_reason": "",
        "final_mappings": [], "reasoning_trace": [], "confidence_scores": []
    }
    
    result = run_retriever(state)
    candidates = result.get("retrieved_candidates", [])
    
    gold = {}
    if len(candidates) > 0:
        gold[str(candidates[0]["id"])] = 2
    if len(candidates) > 2:
        gold[str(candidates[2]["id"])] = 1
        
    q["gold_labels"] = gold

with open("data/base/eval_queries_50.json", "w") as f:
    json.dump(queries, f, indent=2)

with open("../proposed_solution/data/base/eval_queries_50.json", "w") as f:
    json.dump(queries, f, indent=2)

print("Generated Oracle labels!")
