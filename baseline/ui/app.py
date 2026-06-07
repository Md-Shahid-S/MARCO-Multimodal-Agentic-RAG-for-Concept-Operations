import streamlit as st
import os
import sys

# Ensure project root is in path so we can import from both baseline and proposed_solution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from rag_engine import run_retriever
from proposed_solution.agents.state import MARCOState
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Baseline RAG", page_icon="🔍", layout="wide")
st.title("Base Model — DevOps–MSA Concept Alignment")
st.caption("Linear RAG Pipeline | Based on Khadem & Movaghar (2025)")

# Sidebar
with st.sidebar:
    st.header("Query Options")
    st.info("The Base Paper uses a linear RAG approach. It only accepts text-based queries, without multi-modal capabilities or agentic self-correction.")
    top_k = st.slider("Number of recommendations to retrieve (Top K)", min_value=1, max_value=10, value=5)

# Main input
query = st.text_input("Enter your DevOps or MSA concept / question:", 
                      placeholder="e.g. How do I monitor microservices?")

run_button = st.button("Get Recommendations", type="primary")

if run_button and query:
    with st.spinner("Running Baseline Hybrid Search (Dense + BM25 + Cross-Encoder)..."):
        # Set up the state specifically for the baseline model (no artifact context)
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
        
        try:
            # Optionally set the TOP_K environment variable if your retriever respects it
            os.environ["TOP_K"] = str(top_k)
            
            result = run_retriever(state)
            candidates = result.get("retrieved_candidates", [])
            
            st.divider()
            
            if not candidates:
                st.warning("No concepts retrieved. Please try another query.")
            else:
                st.subheader("Recommendations (Ranked by Cross-Encoder Score)")
                for i, hit in enumerate(candidates[:top_k]):
                    score = hit.get('rerank_score', 0)
                    devops = hit.get('devops_concept', 'N/A')
                    msa = hit.get('msa_concept', 'N/A')
                    definition = hit.get('definition', '')
                    category = hit.get('taxonomy_category', 'Uncategorized')
                    
                    # Highlight top result
                    if i == 0:
                        st.markdown(f"### 🥇 **{devops}** ⟷ ***{msa}***")
                        st.markdown(f"**Score:** `{score:.3f}` | **Category:** `{category}`")
                        st.markdown(f"**Definition:** {definition}")
                        st.divider()
                    else:
                        with st.expander(f"**{devops}** ⟷ **{msa}** (Score: {score:.3f})"):
                            st.write(f"**Category:** `{category}`")
                            st.write(f"**Definition:** {definition}")
                            
        except Exception as e:
            st.error(f"Error running retriever: {e}")
