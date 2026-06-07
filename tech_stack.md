# MARCO Framework: Technical Stack

The MARCO (Multimodal Agentic RAG) framework is built using a modern, multi-layered technology stack designed for high-precision architectural alignment.

---

### 1. Core Languages & Orchestration
- **Python (3.12+):** Primary language for all agent logic, parsing, and evaluation.
- **LangGraph:** Orchestrates the stateful, self-correcting 4-agent workflow (Planner → Retriever → Critic → Generator).
- **LangChain:** Unified interface for integrating multiple LLM providers and tool-calling logic.

### 2. Large Language Model (LLM) Backbone
- **Groq API (Llama-3.1-8b-instant):** Powers high-speed reasoning for the **Planner** and **Critic** agents.
- **Google Gemini 2.0 Flash:** Used for multimodal **Vision Processing** (diagram analysis) and final **Response Synthesis**.
- **Hugging Face:** Hosts the **Cross-Encoder** reranking models (`ms-marco-MiniLM-L-6-v2`) used for fine-grained retrieval.

### 3. Vector Database & Hybrid Retrieval
- **FAISS (HNSW Index):** Provides high-performance dense vector similarity search for over 300+ DevOps-MSA concept pairs.
- **ChromaDB:** Persistent storage for document metadata and concept definitions.
- **Rank-BM25:** Implements sparse keyword-based retrieval to complement dense search.
- **Sentence-Transformers:** Generates semantic embeddings using the `all-MiniLM-L6-v2` model.

### 4. Multimodal Processing & Ingestion
- **Gemini Vision API:** Extracts structural patterns from software architecture diagrams and monitoring dashboards.
- **python-hcl2 & PyYAML:** Advanced parsers for Infrastructure-as-Code (Terraform) and CI/CD pipelines (GitHub Actions/GitLab).
- **arXiv API:** Automated ingestion daemon that fetches the latest research papers to keep the knowledge base updated.

### 5. Uncertainty & Reliability Engineering
- **MAPIE (Conformal Prediction):** Attaches calibrated confidence bounds (High/Medium/Low) to every recommendation.
- **RAGAS:** Provides real-time faithfulness and relevancy grading within the Critic agent to prevent hallucinations.
- **NetCal & Scikit-Learn:** Used for calculating Expected Calibration Error (ECE) and building reliability diagrams.

### 6. User Interface & Visualization
- **Streamlit:** Interactive web dashboard for text queries, artifact uploads, and real-time agent reasoning traces.
- **Matplotlib & Seaborn:** Generates evaluation plots, ablation study charts, and reliability diagrams for the research paper.
