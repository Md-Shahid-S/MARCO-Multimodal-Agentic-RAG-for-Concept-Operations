# agents/state.py
from typing import TypedDict, Annotated
import operator

class MARCOState(TypedDict):
    # Input
    original_query:        str
    artifact_context:      str          # From multimodal agent (empty if text-only)

    # Clarification (Human-in-the-loop)
    requires_clarification: bool
    clarification_message:  str

    # Planner outputs
    intent:                str          # "DevOps→MSA" | "MSA→DevOps" | "bidirectional"
    sub_questions:         list[str]
    taxonomy_categories:   list[str]

    # Retriever outputs
    retrieved_candidates:  list[dict]   # [{concept, definition, score, source}]
    retrieval_attempt:     int          # 0, 1, or 2 (max retries)

    # Critic outputs
    graded_candidates:     list[dict]   # [{...candidate, ragas_score, accepted: bool}]
    hallucination_risk:    bool
    retry_needed:          bool
    retry_reason:          str

    # Generator outputs (Explainable RAG)
    context_analysis:      str          # Explanation of how chunks relate to query
    final_resolution:      str          # Synthesized answer
    suggested_next_steps:  list[str]    # Follow-up questions
    
    final_mappings:        list[dict]   # [{devops_concept, msa_concept, explanation, ...}]
    out_of_scope_notes:    str          # Notes for non-DevOps/MSA technologies
    reasoning_trace:       list[str]    # Log of all agent decisions
    confidence_scores:     list[float]  # Raw scores
    ablation:              str          # Evaluation ablation mode (e.g. "e1", "e2")
