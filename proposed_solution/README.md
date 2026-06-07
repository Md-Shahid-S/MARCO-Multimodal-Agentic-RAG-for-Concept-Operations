# MARCO: Multimodal Agentic RAG for DevOps–Microservice Architecture Concept Alignment

MARCO is an advanced AI-driven system designed to bridge the conceptual gap between **DevOps practices** and **Microservice Architecture (MSA)**. It utilizes a state-of-the-art **Multimodal Agentic Retrieval-Augmented Generation (RAG)** pipeline to analyze text queries, architecture diagrams, CI/CD configurations, and Infrastructure-as-Code (IaC) files, providing mathematically grounded and verified concept mappings.

This project implements the methodology outlined by Khadem & Movaghar (2025).

---

## 🌟 Key Features

1. **Multimodal Artifact Understanding:** 
   - Uses **Google Gemini 1.5/2.0 Flash** to visually analyze cloud architecture diagrams.
   - Structurally parses CI/CD pipelines (YAML) and Terraform files (HCL) to extract infrastructure intent.
2. **Agentic Reasoning Loop (LangGraph & Groq):** 
   - **Planner:** Decomposes complex user queries into structured sub-questions.
   - **Retriever:** Fetches context from a hybrid FAISS (Dense) + BM25 (Sparse) index, reranked via Cross-Encoders.
   - **Critic:** Evaluates retrieved evidence for relevance, triggering autonomous retries to prevent hallucinations.
   - **Generator:** Synthesizes final bidirectional DevOps-MSA mappings.
3. **Continuous Knowledge Ingestion:** 
   - An autonomous background daemon (`arxiv_daemon.py`) fetches new academic papers, extracts concepts, checks for semantic drift, and incrementally updates the ChromaDB and FAISS vector stores.
4. **Uncertainty Quantification:** 
   - Applies **Conformal Prediction (MAPIE)** to output statistically calibrated confidence bounds (HIGH/MEDIUM/LOW badges) for every recommendation.
5. **Interactive Dashboard:** 
   - A rich **Streamlit** user interface for querying and artifact uploads.

---

## 🛠️ Architecture

```text
marco/
├── agents/             # LangGraph reasoning loop (Planner, Retriever, Critic, Generator)
├── evaluation/         # P@K, nDCG@K, RAE@K metrics and evaluation runners
├── ingestion/          # ArXiv fetching, PDF parsing, and Groq LLM concept extraction
├── knowledge_base/     # FAISS HNSW index, ChromaDB, and semantic drift detection
├── multimodal/         # Gemini Vision processor, YAML, and Terraform parsers
├── uncertainty/        # MAPIE conformal prediction and reliability calibration
├── ui/                 # Streamlit dashboard
└── data/               # Raw datasets and evaluation queries
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Access to [Groq API](https://console.groq.com/) (for fast Llama-3 text reasoning)
- Access to [Google Gemini API](https://aistudio.google.com/) (for multimodal vision processing)

### 2. Installation

Clone the repository and set up the virtual environment:

```bash
git clone https://github.com/yourusername/MARCO.git
cd MARCO
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```
Edit `.env` and configure:
- `GROQ_API_KEY=your_groq_key`
- `GEMINI_API_KEY=your_gemini_key`

### 4. Running the Dashboard

Start the interactive Streamlit UI:

```bash
PYTHONPATH=. streamlit run ui/app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Background Jobs & Evaluation

**Run the ArXiv Ingestion Daemon** (Fetches new papers and updates the knowledge base):
```bash
PYTHONPATH=. python3 ingestion/arxiv_daemon.py
```

**Run the Baseline Evaluation** (Calculates system metrics against gold-standard queries):
```bash
PYTHONPATH=. python3 evaluation/run_eval.py --mode baseline --queries data/base/eval_queries_50.json
```

---

## 📚 Acknowledgments
Built based on the theoretical framework for aligning DevOps and MSA conceptual taxonomies using Agentic RAG and Conformal Prediction.
