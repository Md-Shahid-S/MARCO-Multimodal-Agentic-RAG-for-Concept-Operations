# evaluation/run_eval.py
import json, argparse, os, sys, time, re
from tqdm import tqdm
# Ensure proposed_solution root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.metrics import precision_at_k, ndcg_at_k, rae_at_k
from agents.retriever import run_retriever
from agents.graph import run_marco
from agents.state import MARCOState

def calculate_hallucination(result: dict) -> bool:
    candidates_text = " ".join([
        c.get("devops_concept", "") + " " + c.get("msa_concept", "") 
        for c in result.get("retrieved_candidates", [])
    ]).lower()
    
    mappings = result.get("final_mappings", [])
    if not mappings:
        return False
        
    for m in mappings:
        devops = m.get("devops_concept", "").lower()
        msa = m.get("msa_concept", "").lower()
        # If the generated concept string isn't anywhere in the candidate text, flag it
        if devops not in candidates_text and msa not in candidates_text:
            return True 
    return False

def evaluate(queries_path: str, mode: str = "marco", k_values: list = [3, 5, 10], limit: int = None) -> dict:
    print(f"Running evaluation in mode: {mode}")
    print(f"Loading queries from {queries_path}...")
    if not os.path.exists(queries_path):
        print(f"Error: {queries_path} not found.")
        return {}
        
    with open(queries_path) as f:
        queries = json.load(f)

    if limit:
        queries = queries[:limit]

    all_results = []
    hallucinations = 0

    pbar = tqdm(queries, desc=f"Evaluating {mode}")
    for i, query_item in enumerate(pbar):
        query  = query_item["query"]
        gold   = query_item.get("gold_labels", {})
        artifact_context = query_item.get("artifact_context", "")

        pbar.set_description(f"Eval: {query[:30]}...")

        start_time = time.time()

        if mode == "baseline":
            state: MARCOState = {
                "original_query":      query, "artifact_context": "",
                "intent":              "", "sub_questions": [query], "taxonomy_categories": [],
                "retrieved_candidates":[], "retrieval_attempt": 0,
                "graded_candidates":   [], "hallucination_risk": False,
                "retry_needed":        False, "retry_reason": "",
                "final_mappings":      [], "out_of_scope_notes": "", "reasoning_trace": [], 
                "confidence_scores": [], "ablation": ""
            }
            state = run_retriever(state)
            # In baseline mode, the ranked list is derived directly from retrieved candidates,
            # as there is no Generator to create final_mappings.
            retrieved_candidates = state.get("retrieved_candidates", [])
            # Extract IDs and actual relevance scores, deduplicating while preserving order.
            ranked = []
            seen = set()
            for c in retrieved_candidates:
                rid = c.get("id")
                if rid is not None and str(rid) not in seen:
                    seen.add(str(rid))
                    ranked.append((rid, c.get("score", 1.0)))
            result_state = state
        elif mode == "marco":
            try:
                result_state = run_marco(query, artifact_context)
                raw_ids = []
                for m in result_state.get("final_mappings", []):
                    # Check both 'sources' (new prompt) and 'citation_ids' (old prompt)
                    citations = m.get("sources", m.get("citation_ids", []))
                    if citations:
                        raw_str = str(citations[0])
                        # Extract strictly the numbers from "ID: 452" -> "452"
                        numeric_id = re.sub(r'\D', '', raw_str) 
                        if numeric_id:
                            raw_ids.append(numeric_id)
                unique_ids = list(dict.fromkeys(raw_ids))
                ranked = [(rid, 1.0) for rid in unique_ids]
            except Exception as e:
                print(f"[RunEval] Error running MARCO on query {i}: {e}")
                result_state = {}
                ranked = []
        elif mode == "ablation_e1":
            try:
                result_state = run_marco(query, artifact_context, ablation="e1")
                raw_ids = []
                for m in result_state.get("final_mappings", []):
                    # Check both 'sources' (new prompt) and 'citation_ids' (old prompt)
                    citations = m.get("sources", m.get("citation_ids", []))
                    if citations:
                        raw_str = str(citations[0])
                        # Extract strictly the numbers from "ID: 452" -> "452"
                        numeric_id = re.sub(r'\D', '', raw_str) 
                        if numeric_id:
                            raw_ids.append(numeric_id)
                unique_ids = list(dict.fromkeys(raw_ids))
                ranked = [(rid, 1.0) for rid in unique_ids]
            except Exception as e:
                print(f"[RunEval] Error running Ablation E1 on query {i}: {e}")
                result_state = {}
                ranked = []
        elif mode == "ablation_e2":
            try:
                result_state = run_marco(query, artifact_context, ablation="e2")
                raw_ids = []
                for m in result_state.get("final_mappings", []):
                    # Check both 'sources' (new prompt) and 'citation_ids' (old prompt)
                    citations = m.get("sources", m.get("citation_ids", []))
                    if citations:
                        raw_str = str(citations[0])
                        # Extract strictly the numbers from "ID: 452" -> "452"
                        numeric_id = re.sub(r'\D', '', raw_str) 
                        if numeric_id:
                            raw_ids.append(numeric_id)
                unique_ids = list(dict.fromkeys(raw_ids))
                ranked = [(rid, 1.0) for rid in unique_ids]
            except Exception as e:
                print(f"[RunEval] Error running Ablation E2 on query {i}: {e}")
                result_state = {}
                ranked = []
        else:
            ranked = []
            result_state = {}

        end_time = time.time()
        latency = end_time - start_time

        if calculate_hallucination(result_state):
            hallucinations += 1

        metrics = {}
        for k in k_values:
            ranked_ids = [r[0] for r in ranked[:k]]
            labels = [gold.get(str(rid), gold.get(rid, 0)) for rid in ranked_ids]
            metrics[f"P@{k}"]    = precision_at_k(labels, k)
            metrics[f"nDCG@{k}"] = ndcg_at_k(labels, k)
            
        metrics["RAE@5"] = rae_at_k(ranked, gold, 5)
        metrics["latency_seconds"] = round(latency, 2)
        all_results.append({"query": query, "metrics": metrics, "ranked": ranked})

    # Aggregate
    aggregate = {m: round(sum(r["metrics"][m] for r in all_results)/len(all_results), 4) 
                 for m in all_results[0]["metrics"].keys()}
    aggregate["n_queries"] = len(all_results)
    aggregate["hallucination_rate"] = round(hallucinations / len(all_results), 4) if all_results else 0
    
    os.makedirs("evaluation/results", exist_ok=True)
    with open(f"evaluation/results/{mode}_results.json","w") as f:
        json.dump({"mode": mode, "aggregate": aggregate, "per_query": all_results}, f, indent=2)
        
    print("\n--- AGGREGATE RESULTS ---")
    print(json.dumps(aggregate, indent=2))
    return aggregate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="marco", choices=["marco","baseline","ablation_e1","ablation_e2"])
    parser.add_argument("--queries", default="data/base/eval_queries_50.json")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of queries for a quick test")
    args = parser.parse_args()
    
    evaluate(args.queries, args.mode, limit=args.limit)
