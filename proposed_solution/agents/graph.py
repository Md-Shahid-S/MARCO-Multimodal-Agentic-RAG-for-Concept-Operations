# agents/graph.py
from langgraph.graph import StateGraph, END
from agents.state import MARCOState
from agents.planner   import run_planner
from agents.retriever import run_retriever
from agents.critic    import run_critic
from agents.generator import run_generator
import sys

def should_retry(state: MARCOState) -> str:
    """Conditional edge: retry retrieval or proceed to generation."""
    if state.get("ablation") == "e1":
        return "generator" # Skip retry for E1 ablation
    if state.get("retry_needed", False):
        return "retriever"   # Loop back
    return "generator"       # Proceed

def check_ambiguity(state: MARCOState) -> str:
    """Conditional edge: check if human clarification is required."""
    # Only pause if explicitly marked ambiguous AND no sub-questions were generated to attempt a general answer
    if state.get("requires_clarification", False) and not state.get("sub_questions"):
        return "human_input"
    return "retriever"

def human_input_node(state: MARCOState) -> MARCOState:
    """Pause execution for clarification if ambiguous."""
    clarification = state.get("clarification_message", "Could you provide more details?")
    
    # Always raise InterruptedError to surface the clarification question 
    # to the API layer (FastAPI/Streamlit/Next.js) for human-in-the-loop flows.
    raise InterruptedError(clarification)

    # Clear flags so it doesn't loop infinitely upon next invoke
    state["requires_clarification"] = False
    state["clarification_message"] = ""
    
    if "reasoning_trace" not in state:
        state["reasoning_trace"] = []
    state["reasoning_trace"].append("[Human Input] Clarification requested and received.")
    
    return state

def build_graph() -> StateGraph:
    graph = StateGraph(MARCOState)

    graph.add_node("planner",   run_planner)
    graph.add_node("human_input", human_input_node)
    graph.add_node("retriever", run_retriever)
    graph.add_node("critic",    run_critic)
    graph.add_node("generator", run_generator)

    graph.set_entry_point("planner")
    
    # Planner -> ambiguity check -> human or retrieve
    graph.add_conditional_edges("planner", check_ambiguity, {"human_input": "human_input", "retriever": "retriever"})
    
    # Human -> back to Planner
    graph.add_edge("human_input", "planner")
    
    graph.add_edge("retriever", "critic")
    graph.add_conditional_edges("critic", should_retry,
                                {"retriever": "retriever", "generator": "generator"})
    graph.add_edge("generator", END)

    return graph.compile()

# Main query function
def run_marco(query: str, artifact_context: str = "", ablation: str = None) -> dict:
    app = build_graph()
    initial_state: MARCOState = {
        "original_query":      query,
        "artifact_context":    artifact_context if ablation != "e2" else "",
        "intent":              "",
        "sub_questions":       [],
        "taxonomy_categories": [],
        "retrieved_candidates":[],
        "retrieval_attempt":   0,
        "graded_candidates":   [],
        "hallucination_risk":  False,
        "retry_needed":        False,
        "retry_reason":        "",
        "final_mappings":      [],
        "out_of_scope_notes":  "",
        "reasoning_trace":     [],
        "confidence_scores":   [],
        "ablation":            ablation or ""
    }
    result = app.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Test script for the entire graph
    res = run_marco("How do I securely deploy containerized microservices?", "")
    import json
    print(json.dumps(res, indent=2))
