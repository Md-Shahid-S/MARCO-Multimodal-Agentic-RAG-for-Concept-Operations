# evaluation/metrics.py
import numpy as np

def precision_at_k(labels: list[int], k: int) -> float:
    """Precision at K: proportion of relevant items in top K."""
    if not labels or k == 0:
        return 0.0
    labels = labels[:k]
    relevant_count = sum(1 for label in labels if label > 0)
    return relevant_count / k

def ndcg_at_k(labels: list[int], k: int) -> float:
    """Normalized Discounted Cumulative Gain at K."""
    if not labels or k == 0:
        return 0.0
    labels = labels[:k]
    
    # Calculate DCG
    dcg = sum((2**label - 1) / np.log2(idx + 2) for idx, label in enumerate(labels))
    
    # Calculate IDCG (ideal DCG where labels are sorted descending)
    ideal_labels = sorted(labels, reverse=True)
    idcg = sum((2**label - 1) / np.log2(idx + 2) for idx, label in enumerate(ideal_labels))
    
    if idcg == 0:
        return 0.0
    return dcg / idcg


def rae_at_k(ranked: list[tuple], gold: dict, k: int, avg_mappings_in_dataset: float = 4.0) -> float:
    """
    Retrieval Accuracy Equivalent at K.
    Calculated exactly as defined by Khadem & Movaghar (2025):
    (Number of relevant items in Top K) / (Average human-validated mappings per query)
    """
    if not ranked or k == 0:
        return 0.0
    
    # ranked format: [(concept_id, score), ...]
    ranked_ids = [r[0] for r in ranked[:k]]
    
    # Extract gold labels for ranked items
    item_scores = [gold.get(str(rid), gold.get(rid, 0)) for rid in ranked_ids]
    
    # R_q(k): Number of retrieved items at k with a label >= 1
    r_q_k = sum(1 for score in item_scores if score >= 1)
    
    # Divide by the average number of mappings per query in your gold dataset
    # (Note: You need to set 'avg_mappings_in_dataset' to whatever the average 
    # number of gold mappings is across your 50 eval queries).
    return r_q_k / avg_mappings_in_dataset
