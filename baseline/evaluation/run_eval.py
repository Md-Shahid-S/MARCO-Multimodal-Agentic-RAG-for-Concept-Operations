# baseline/evaluation/run_eval.py
import json, argparse, os, sys
# Ensure baseline root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.metrics import precision_at_k, ndcg_at_k, rae_at_k
from rag_engine import run_retriever
from proposed_solution.agents.state import MARCOState

def evaluate_baseline(queries_path: str, k_values: list = [3, 5, 10]) -> dict:
    print(f"Loading queries from {queries_path}...")
    with open(queries_path) as f:
        queries = json.load(f)

    all_results = []
    for query_item in queries:
        query  = query_item["query"]
        gold   = query_item.get("gold_labels", {})

        state: MARCOState = {
            "original_query":      query, "artifact_context": "",
            "intent":              "", "sub_questions": [query], "taxonomy_categories": [],
            "retrieved_candidates":[], "retrieval_attempt": 0,
            "graded_candidates":   [], "hallucination_risk": False,
            "retry_needed":        False, "retry_reason": "",
            "final_mappings":      [], "reasoning_trace": [], "confidence_scores": []
        }
        
        state = run_retriever(state)
        ranked = [(c["id"], c.get("rerank_score",0)) for c in state["retrieved_candidates"]]

        metrics = {}
        for k in k_values:
            ranked_ids = [r[0] for r in ranked[:k]]
            labels = [gold.get(str(rid), gold.get(rid, 0)) for rid in ranked_ids]
            metrics[f"P@{k}"]    = precision_at_k(labels, k)
            metrics[f"nDCG@{k}"] = ndcg_at_k(labels, k)
            
        metrics["RAE@5"] = rae_at_k(ranked, gold, 5)
        all_results.append({"query": query, "metrics": metrics, "ranked": ranked})

    # Aggregate
    aggregate = {m: round(sum(r["metrics"][m] for r in all_results)/len(all_results), 4) 
                 for m in all_results[0]["metrics"].keys()}
    aggregate["n_queries"] = len(all_results)
    
    os.makedirs("evaluation/results", exist_ok=True)
    with open("evaluation/results/baseline_only.json","w") as f:
        json.dump({"aggregate": aggregate, "per_query": all_results}, f, indent=2)
        
    print(json.dumps(aggregate, indent=2))
    return aggregate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default="data/base/eval_queries_50.json") # Relative to baseline root
    args = parser.parse_args()
    
    # Check if data exists in baseline root
    q_path = args.queries
    if not os.path.exists(q_path):
        q_path = "../proposed_solution/data/base/eval_queries_50.json"
        
    evaluate_baseline(q_path)
