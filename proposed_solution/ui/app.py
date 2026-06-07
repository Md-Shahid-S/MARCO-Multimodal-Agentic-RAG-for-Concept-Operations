# proposed_solution/ui/app.py
import streamlit as st
import tempfile, os, json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.graph import run_marco
from multimodal.agent import preprocess_artifact

st.set_page_config(page_title="MARCO", page_icon="⚙️", layout="wide")
st.title("MARCO — DevOps–MSA Concept Alignment")
st.caption("Multimodal Agentic RAG | Groq & Gemini Flash | Project Specification Audit Compliant")

# Sidebar
with st.sidebar:
    st.header("Query options")
    query_mode = st.radio("Input type", ["Text query", "Upload artifact"])
    st.divider()
    st.info("MARCO uses Groq Llama-3 for reasoning and Gemini Flash for multimodal understanding.")
    st.caption("All recommendations grounded in a static index of 300+ concept pairs.")

# Main input
artifact_context = ""
if query_mode == "Text query":
    query = st.text_area("Enter your DevOps or MSA concept / question:",
                         placeholder="e.g. How should I add observability to my Kubernetes deployment?",
                         height=100)
else:
    uploaded_file = st.file_uploader(
        "Upload architecture diagram, CI/CD YAML, dashboard screenshot, or IaC file",
        type=["png","jpg","pdf","yml","yaml","tf"]
    )
    query = st.text_input("Optional: add a specific question about this artifact")
    if uploaded_file:
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        with st.spinner("Parsing artifact..."):
            parsed = preprocess_artifact(tmp_path)
            artifact_context = parsed.get("query_enrichment", "")
            if artifact_context:
                st.info(f"Context Extracted: {artifact_context[:200]}...")
            if "error" in parsed:
                st.error(parsed["error"])

run_button = st.button("Get Recommendations", type="primary")

if run_button and (query or artifact_context):
    full_query = query or "Analyse this architecture artifact for DevOps–MSA gaps"
    
    # Store the conversation history in session state to handle multi-turn
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = full_query
    else:
        # If this is a follow-up, append it
        if query and query != st.session_state.chat_history:
            st.session_state.chat_history += f"\n[User Clarification]: {query}"
            full_query = st.session_state.chat_history

    with st.spinner("Running MARCO agents..."):
        try:
            result = run_marco(full_query, artifact_context)
            
            # Reset history on successful complete run
            st.session_state.chat_history = ""
            
            st.divider()

            # Display Image and Vision Analysis if an image was uploaded
            if query_mode == "Upload artifact" and uploaded_file and uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Create two columns: Left for Image, Right for Analysis
                img_col1, img_col2 = st.columns([1, 1.2])

                with img_col1:
                    st.image(uploaded_file, caption="Uploaded Artifact", use_container_width=True)

                with img_col2:
                    tab1, tab2, tab3 = st.tabs(["🖼️ Image Explanation", "🛠️ Components", "📚 Related Docs"])
                    
                    with tab1:
                        st.write(result.get("context_analysis", "No explanation available."))
                        
                    with tab2:
                        # Display the components found by Gemini Vision
                        for item in parsed.get("normalised_concepts", {}).get("concepts", []):
                            st.info(f"**{item.get('devops_concept', 'Unknown')}**: {item.get('taxonomy_category', 'Unknown')}")
                            
                    with tab3:
                        # Display the actual retrieved documents with IDs
                        for doc in result.get("graded_candidates", []):
                            with st.expander(f"Source ID: {doc.get('id', 'N/A')}"):
                                st.write(doc.get('definition', 'No description available.'))
                                st.caption(f"Relevance: {doc.get('score', 'N/A')}")
                st.divider()

            # Results
            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader("💡 MARCO Architectural Analysis")
                
                # Context Analysis
                context_analysis = result.get("context_analysis", "")
                if context_analysis:
                    st.markdown(f"#### **🔍 Context Analysis**")
                    st.write(context_analysis)

                # Conversational Answer
                final_resolution = result.get("final_resolution", "")
                if final_resolution:
                    st.markdown(f"#### **✅ Final Resolution**")
                    st.info(final_resolution)
                
                # Check for Out of Scope Notes
                out_of_scope = result.get("out_of_scope_notes", "")
                if out_of_scope:
                    st.warning(f"⚠️ **Scope Note:** {out_of_scope}")

                st.divider()
                st.subheader("🛠️ Architectural Mappings")

                mappings = result.get("final_mappings", [])
                if not mappings:
                    st.warning("No mappings found. The Critic agent may have rejected the retrieved evidence.")
                
                for mapping in mappings:
                    st.markdown(f"### **{mapping.get('devops_concept','')}** ⟷ ***{mapping.get('msa_concept','')}***")
                    
                    # Detailed Explanation
                    explanation = mapping.get('explanation') or mapping.get('justification', 'No detailed explanation available.')
                    st.markdown(f"> {explanation}")
                    
                    # Metadata & Sources
                    sources = mapping.get('sources', [])
                    source_str = ", ".join([f"`[{s}]`" for s in sources]) if sources else "`System KB`"
                    st.caption(f"**Category:** `{mapping.get('taxonomy_category','')}` | **Sources:** {source_str}")
                    st.divider()
                
                # Suggested Next Steps
                next_steps = result.get("suggested_next_steps", [])
                if next_steps:
                    st.subheader("✨ Suggested Next Steps")
                    for step in next_steps:
                        st.markdown(f"- {step}")

            with col2:
                st.subheader("🧠 Reasoning Trace & Context")
                
                # Show Retrieved Chunks
                chunks = result.get("graded_candidates", [])
                if chunks:
                    with st.expander(f"View Retrieved Context Chunks ({len([c for c in chunks if c.get('accepted')])})", expanded=True):
                        for chunk in [c for c in chunks if c.get('accepted')]:
                            st.markdown(f"**Source:** `{chunk.get('reference_name', f'Doc {chunk.get('id')}')}`")
                            st.info(f"{chunk.get('devops_concept')} → {chunk.get('msa_concept')}: {chunk.get('definition')}")
                            
                st.divider()
                st.markdown("#### Agentic Log")
                for step in result.get("reasoning_trace", []):
                    st.info(step)
                
                with st.expander("View Raw State"):
                    st.json(result)
                    
        except InterruptedError as e:
            st.divider()
            st.warning("### 🤔 Clarification Needed")
            st.info(str(e))
            st.markdown("The Planner agent paused execution because your query was too ambiguous to retrieve accurate architectural mappings. **Please type your clarification in the main input box above and click 'Get Recommendations' again to continue.**")
            
        except Exception as e:
            st.error(f"Execution Error: {e}")
            import traceback
            st.code(traceback.format_exc())
