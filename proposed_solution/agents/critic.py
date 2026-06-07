# agents/critic.py
import os
from agents.state import MARCOState
from dotenv import load_dotenv

load_dotenv()

RELEVANCE_THRESHOLD    = float(os.getenv("RAGAS_RELEVANCE_THRESHOLD", 0.2)) # Lowered from 1.0 to handle standard keyword matching variance
MIN_HIGH_QUALITY_RATIO = float(os.getenv("MIN_HIGH_QUALITY_RATIO", 0.5))
MAX_RETRIES            = int(os.getenv("MAX_RETRY_CYCLES", 2))

def run_critic(state: MARCOState) -> MARCOState:
    candidates = state.get("retrieved_candidates", [])
    query      = state["original_query"]
    graded     = []

    for candidate in candidates:
        # Score relevance using simplified string overlap
        context_text = f"{candidate.get('devops_concept', '')}: {candidate.get('definition','')}"
        overlap  = _keyword_overlap(query, context_text)
        accepted = overlap >= RELEVANCE_THRESHOLD

        graded.append({**candidate, "ragas_score": overlap, "accepted": accepted})

    accepted_count = sum(1 for g in graded if g["accepted"])
    ratio          = accepted_count / len(graded) if graded else 0.0
    
    current_attempt = state.get("retrieval_attempt", 0)
    retry_needed   = (ratio < MIN_HIGH_QUALITY_RATIO and current_attempt < MAX_RETRIES)

    state["graded_candidates"]   = graded
    state["hallucination_risk"]  = accepted_count == 0
    state["retry_needed"]        = retry_needed
    state["retry_reason"]        = (f"Only {accepted_count}/{len(graded)} candidates "
                                    f"meet relevance threshold {RELEVANCE_THRESHOLD}"
                                    if retry_needed else "")
    state["retrieval_attempt"]   = current_attempt + 1

    if "reasoning_trace" not in state:
        state["reasoning_trace"] = []

    state["reasoning_trace"].append(
        f"[Critic] Accepted: {accepted_count}/{len(graded)} candidates. "
        f"Retry needed: {retry_needed}. "
        f"Hallucination risk: {state['hallucination_risk']}"
    )
    return state

import string

def _keyword_overlap(query: str, context: str) -> float:
    # Remove punctuation and lowercase
    translator = str.maketrans('', '', string.punctuation)
    q_clean = query.lower().translate(translator)
    c_clean = context.lower().translate(translator)
    
    q_words = set(q_clean.split())
    c_words = set(c_clean.split())
    
    stopwords = {"a","an","the","is","in","of","to","and","or","for","with","on","at","what","how","should","i","use","if","am"}
    q_words -= stopwords
    
    if not q_words:
        return 0.0
        
    # Check if query words are sub-strings in the context (handles plurals like deployment vs deployments)
    match_count = 0
    for qw in q_words:
        if any(qw in cw or cw in qw for cw in c_words):
            match_count += 1
            
    return match_count / len(q_words)
