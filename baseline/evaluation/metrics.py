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

def rae_at_k(ranked: list[tuple], gold: dict, k: int) -> float:
    """Retrieval Accuracy Equivalent at K.
    Custom metric defined by Khadem & Movaghar (2025). 
    Approximated as average relevance score of retrieved items relative to max possible.
    """
    if not ranked or k == 0:
        return 0.0
    
    # ranked format: [(concept_id, score), ...]
    ranked_ids = [r[0] for r in ranked[:k]]
    
    # Extract gold labels for ranked items (handle string vs int keys)
    item_scores = [gold.get(str(rid), gold.get(rid, 0)) for rid in ranked_ids]
    
    # RAE could be interpreted as the mean relevance mapped to [0,1]
    # Assuming gold labels are in {0, 1, 2}
    max_label = 2.0
    return (sum(item_scores) / k) / max_label
