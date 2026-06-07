# MARCO — Complete Project Build Plan
### Multimodal Agentic RAG for DevOps–Microservice Architecture Concept Alignment

> **Status:** Pre-build planning document  
> **Target venue:** IEEE Access / ICSE-SEIP 2026  

> **Base paper:** Khadem & Movaghar (2025) — IEEE Access DOI: 10.1109/ACCESS.2025.3628665

---

## 1. Project Overview & Scope
MARCO extends a published IEEE paper's static linear RAG system with two architectural upgrades, making it practical for real DevOps engineers by allowing artifact uploads and adding AI self-correction.


## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Research Contributions](#2-research-contributions)
3. [Directory Structure](#3-directory-structure)
4. [Environment Setup](#4-environment-setup)
5. [Free API Keys & Accounts](#5-free-api-keys--accounts)
6. [Week-by-Week Build Schedule](#6-week-by-week-build-schedule)
7. [Week 1–2 — Baseline Replication](#7-week-12--baseline-replication)
8. [Week 3 — Adaptive Knowledge Base (N4)](#8-week-3--adaptive-knowledge-base-n4)
9. [Week 4 — Multimodal Input Agent (N3)](#9-week-4--multimodal-input-agent-n3)
10. [Week 5–6 — Agentic Reasoning Loop (N1)](#10-week-56--agentic-reasoning-loop-n1)
11. [Week 7 — Uncertainty Quantification (N7)](#11-week-7--uncertainty-quantification-n7)
12. [Week 8–9 — Evaluation & Ablation](#12-week-89--evaluation--ablation)
13. [Week 10 — UI, Deployment & Paper Writeup](#13-week-10--ui-deployment--paper-writeup)
14. [Complete File Reference](#14-complete-file-reference)
15. [All Dependencies](#15-all-dependencies)
16. [Data Sources & Datasets](#16-data-sources--datasets)
17. [Evaluation Protocol](#17-evaluation-protocol)
18. [Ablation Experiment Design](#18-ablation-experiment-design)
19. [Error Handling & Fallbacks](#19-error-handling--fallbacks)
20. [Testing Strategy](#20-testing-strategy)
21. [Paper Placeholder Map](#21-paper-placeholder-map)
22. [Submission Checklist](#22-submission-checklist)

---

## 1. Project Overview

### What MARCO is
MARCO extends a published IEEE Access paper's static linear RAG system with four architectural upgrades, making it practical for real DevOps engineers rather than academic concept-name queries only.

### What the base paper provided (you inherit all of this)
| Asset | Location | What it contains |
|---|---|---|
| 84-paper corpus | GitHub: azizikhadem/devops-msa-mapping-rag | Annotated DevOps–MSA concept pairs |
| FAISS index | Zenodo DOI: 10.5281/zenodo.16760389 | Pre-built concept embeddings |
| Ontology v1.0 | Same repo | Canonical vocabulary, rules R1–R7 |
| 50-query eval set | Same repo | Gold-labeled queries with relevance scores |
| Taxonomy (5 categories) | Same repo | 200+ DevOps↔MSA mappings |

### What MARCO adds
| Contribution | Code module | Addresses |
|---|---|---|
| N1 — Agentic loop | `agents/` | Linear pipeline, no self-correction |
| N3 — Multimodal input | `multimodal/` | Text-only queries |

---

## 2. Research Contributions

### RQ1 — Does agentic self-correction improve precision over linear RAG?
- **Hypothesis:** MARCO P@5 > 0.82 (base paper) and hallucination rate decreases
- **Measure:** P@5, nDCG@5, RAE@5, hallucination rate (RAGAS faithfulness)
- **Ablation E1:** MARCO without Critic agent

### RQ2 — Do artifact inputs yield higher concept recall than text queries?
- **Hypothesis:** Artifact-grounded queries surface DevOps–MSA gaps invisible to concept-name queries
- **Measure:** Concept recall on 15 artifact queries vs. text-only equivalents
- **Ablation E2:** MARCO without multimodal preprocessing agent

### RQ3 — Does conformal prediction produce calibrated confidence?
- **Hypothesis:** MAPIE calibration achieves ECE < 0.10
- **Measure:** ECE, reliability diagram, prediction set size
- **Ablation E4:** MARCO without uncertainty module

---

## 3. Directory Structure

```text
marco/
├── README.md
├── requirements.txt
├── .env.example
├── config.py
│
├── data/
│   ├── base/                       # Downloaded from base paper repo
│   └── eval/                       # Your 80-query evaluation set
│
├── knowledge_base/
│   ├── builder.py                  # Build FAISS index from concept pairs
│   └── chroma_store.py             # ChromaDB persistent metadata
│
├── multimodal/                     # C2 — Multimodal preprocessing agent
│   ├── agent.py                    # Main dispatcher
│   ├── vision_processor.py         # Gemini Flash Vision API calls
│   ├── yaml_parser.py              # PyYAML CI/CD pipeline parsing
│   ├── iac_parser.py               # hcl2 + PyYAML IaC parsing
│   └── concept_normaliser.py       # Maps extracted concepts → Ontology v1.0
│
├── agents/                         # C1 — Agentic reasoning loop
│   ├── graph.py                    # LangGraph state graph definition
│   ├── state.py                    # Typed state schema
│   ├── planner.py                  # Agent 1: intent + decomposition + routing
│   ├── retriever.py                # Agent 2: FAISS + BM25 + reranker
│   ├── critic.py                   # Agent 3: RAGAS grading + hallucination check
│   └── generator.py                # Agent 4: Gemini Flash synthesis
│
├── evaluation/
│   ├── metrics.py                  # P@k, nDCG@k, RAE@k
│   ├── run_eval.py                 # Main evaluation runner
│   ├── ablation.py                 # Ablation configurations (E1, E2)
│   └── inter_rater.py              # Cohen's κ computation
│
└── ui/
    └── app.py                      # Streamlit main app
```
---

## 4. Environment Setup

### Step 1 — Clone base paper repository
```bash
git clone https://github.com/azizikhadem/devops-msa-mapping-rag.git base_paper
cd base_paper && pip install -r requirements.txt --break-system-packages
```

### Step 2 — Download base paper artefacts from Zenodo
```bash
# Zenodo DOI: 10.5281/zenodo.16760389
# Download: concept_pairs.json, faiss_index.bin, ontology_v1.json, eval_queries_50.json
wget "https://zenodo.org/record/16760389/files/devops_msa_dataset.zip"
unzip devops_msa_dataset.zip -d data/base/
```

### Step 3 — Create project and install dependencies
```bash
mkdir marco && cd marco
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

pip install --upgrade pip
pip install -r requirements.txt --break-system-packages
```

### Step 4 — Create .env file
```bash
cp .env.example .env
# Fill in your API keys (see Section 5)
```

### Step 5 — Verify setup
```bash
python3 -c "
import faiss, langchain, ragas, mapie, chromadb
from sentence_transformers import SentenceTransformer
print('All core dependencies OK')
"
```

---

## 5. Free API Keys & Accounts

> All of these are genuinely free with no credit card required for research-scale usage.

### Groq API — Llama-3 70B (Planner + Critic agents)
1. Go to https://console.groq.com/
2. Sign up with email
3. Navigate to API Keys → Create API Key
4. Copy key → paste as `GROQ_API_KEY` in `.env`
5. **Free limits:** 14,400 tokens/minute, 500,000 tokens/day
6. **Model to use:** `llama-3.3-70b-versatile`

### Google AI Studio — Gemini 2.0 Flash Vision (Generator + Multimodal)
1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click Get API Key → Create API key in new project
4. Copy key → paste as `GEMINI_API_KEY` in `.env`
5. **Free limits:** 1,500 requests/day, 1M token context
6. **Model to use:** `gemini-2.0-flash-exp`

### arXiv API — Live paper ingestion
- No API key required
- Base URL: `http://export.arxiv.org/api/query`
- Rate limit: 1 request per 3 seconds (built into daemon)
- Set `ARXIV_RATE_LIMIT_SECONDS=3` in `.env`

### Hugging Face — Cross-encoder reranker + LLaVA fallback
1. Go to https://huggingface.co/
2. Create free account
3. Settings → Access Tokens → New token (read permission)
4. Copy token → paste as `HF_TOKEN` in `.env`
5. **Models used:**
   - `cross-encoder/ms-marco-MiniLM-L-6-v2` (reranker, runs locally)
   - `llava-hf/llava-1.5-7b-hf` (vision fallback if Gemini quota exceeded)

### Hugging Face Spaces — Free hosting
1. Go to https://huggingface.co/spaces
2. Create New Space → Streamlit → CPU Basic (free, 16GB RAM)
3. Connect your GitHub repository
4. Add secrets (API keys) in Space Settings → Variables and Secrets

### GitHub — Code hosting + Actions
1. Create repository: `your-username/marco`
2. Push all code
3. Create `.github/workflows/tests.yml` for CI (see Section 20)

### `.env.example` template
```bash
# Groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.1
GROQ_MAX_TOKENS=1024

# Gemini
GEMINI_API_KEY=your_gemini_key_here
GEMINI_VISION_MODEL=gemini-2.0-flash-exp
GEMINI_TEXT_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.1
GEMINI_MAX_TOKENS=768

# HuggingFace
HF_TOKEN=your_hf_token_here

# arXiv
ARXIV_SEARCH_QUERY=("DevOps" OR "DevSecOps" OR "CI/CD" OR "GitOps") AND ("microservice" OR "architecture")
ARXIV_MAX_RESULTS=50
ARXIV_RATE_LIMIT_SECONDS=3

# Knowledge base
FAISS_INDEX_PATH=knowledge_base/index/faiss_hnsw.bin
CHROMA_PERSIST_DIR=knowledge_base/chroma/
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Retrieval
TOP_K=5
BM25_WEIGHT=0.3
DENSE_WEIGHT=0.7
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Critic agent
RAGAS_RELEVANCE_THRESHOLD=1.0
MAX_RETRY_CYCLES=2
MIN_HIGH_QUALITY_RATIO=0.5

# Uncertainty
MAPIE_COVERAGE_TARGET=0.80
CONFIDENCE_HIGH_THRESHOLD=0.75
CONFIDENCE_MEDIUM_THRESHOLD=0.50

# Drift detection
DRIFT_COSINE_THRESHOLD=0.15
```

---

## 6. Week-by-Week Build Schedule

Week  Focus Area                 Details
───────────────────────────────────────────────────────────────────────
 1    Baseline Replication       Clone base repo, build FAISS index
 2    Verify Baseline            Ensure P@5=0.82 on base data
 3    Multimodal Agent (C2)      Gemini Vision, YAML parsers, IaC parsers
 4    Agentic RAG Part 1 (C1)    LangGraph state, Planner & Retriever Agents
 5    Agentic RAG Part 2 (C1)    Critic Agent (RAGAS), Generator Agent
 6    Evaluation                 Build 80Q eval set, run P@k metrics
 7    Ablation Studies           Run E1 (No Critic) and E2 (No Multimodal)
 8    UI & Deployment            Streamlit app, Hugging Face Spaces deploy



---
Ablation Experiment Design

Experiment
What to change in code
Config flag

E1 — No Critic
In agents/graph.py: bypass critic, connect retriever→generator
--mode ablation_e1

E2 — No Multimodal
In agents/graph.py: set artifact_context="" for all queries
--mode ablation_e2



## 7. Week 1–2 — Baseline Replication

### Goal
Reproduce base paper results exactly. You need P@5 ≈ 0.82 before building anything new.

### Step 1 — Download and inspect the dataset
```bash
# Clone base repo
git clone https://github.com/azizikhadem/devops-msa-mapping-rag.git
cd devops-msa-mapping-rag

# Inspect data structure
python3 -c "
import json
with open('data/concept_pairs.json') as f:
    data = json.load(f)
print(f'Total concept pairs: {len(data)}')
print('Sample:', json.dumps(data[0], indent=2))
"
```

### Step 2 — Build `knowledge_base/builder.py`
```python
# knowledge_base/builder.py
import json, faiss, numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "knowledge_base/index/faiss_hnsw.bin"
META_PATH  = "knowledge_base/index/metadata.json"

def build_index(concept_pairs_path: str) -> None:
    with open(concept_pairs_path) as f:
        pairs = json.load(f)

    model = SentenceTransformer(EMBEDDING_MODEL)

    # Build text for each concept: label + definition
    texts = [f"{p['devops_concept']}: {p.get('definition', '')}" for p in pairs]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    dim = embeddings.shape[1]
    # HNSW index — supports incremental add()
    index = faiss.IndexHNSWFlat(dim, 32)   # 32 = M parameter
    index.hnsw.efConstruction = 200
    index.add(embeddings.astype(np.float32))

    Path("knowledge_base/index").mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    # Save metadata alongside
    metadata = [{"id": i, **p} for i, p in enumerate(pairs)]
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Index built: {index.ntotal} vectors, dim={dim}")

if __name__ == "__main__":
    build_index("data/base/concept_pairs.json")
```

### Step 3 — Build `knowledge_base/chroma_store.py`
```python
# knowledge_base/chroma_store.py
import chromadb, json

class ChromaConceptStore:
    def __init__(self, persist_dir: str = "knowledge_base/chroma"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("devops_msa_concepts")

    def upsert(self, concepts: list[dict]) -> None:
        ids        = [str(c["id"]) for c in concepts]
        documents  = [f"{c['devops_concept']}: {c.get('definition','')}" for c in concepts]
        metadatas  = [{k: str(v) for k, v in c.items()} for c in concepts]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def get(self, concept_id: str) -> dict | None:
        result = self.collection.get(ids=[concept_id])
        return result["metadatas"][0] if result["ids"] else None
```

### Step 4 — Verify baseline P@5
```python
# Run base paper evaluation to confirm you have the same numbers
# Expected: P@5 = 0.82, nDCG@5 = 0.86
python3 evaluation/run_eval.py --mode baseline --queries data/base/eval_queries_50.json
```

### Checkpoint ✅
- [ ] `data/base/` populated with all 4 base paper files
- [ ] `knowledge_base/index/faiss_hnsw.bin` built successfully
- [ ] Baseline P@5 reproduced within ±0.02 of 0.82
- [ ] `evaluation/metrics.py` P@k, nDCG@k, RAE@k all implemented and tested

---

## 8. Week 3 — Adaptive Knowledge Base (N4)

### Goal
Weekly arXiv pull → parse → extract concepts → update FAISS index incrementally.

### Step 1 — Build `ingestion/arxiv_daemon.py`
```python
# ingestion/arxiv_daemon.py
import arxiv, time, os
from apscheduler.schedulers.blocking import BlockingScheduler
from ingestion.pdf_parser import extract_text_from_url
from ingestion.concept_extractor import extract_concepts
from knowledge_base.updater import update_index_with_new_concepts

QUERY  = os.getenv("ARXIV_SEARCH_QUERY")
MAX_R  = int(os.getenv("ARXIV_MAX_RESULTS", 50))
DELAY  = float(os.getenv("ARXIV_RATE_LIMIT_SECONDS", 3))

def fetch_new_papers(since_date: str) -> list[dict]:
    """Pull papers published after since_date."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=QUERY,
        max_results=MAX_R,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = []
    for paper in client.results(search):
        if str(paper.published.date()) <= since_date:
            break
        results.append({
            "arxiv_id":   paper.entry_id,
            "title":      paper.title,
            "abstract":   paper.summary,
            "pdf_url":    paper.pdf_url,
            "published":  str(paper.published.date())
        })
        time.sleep(DELAY)
    return results

def weekly_ingestion_job():
    from ingestion.state import get_last_ingestion_date, set_last_ingestion_date
    last_date = get_last_ingestion_date()
    print(f"[arXiv daemon] Fetching papers since {last_date}")
    papers = fetch_new_papers(last_date)
    print(f"[arXiv daemon] Found {len(papers)} new papers")

    all_new_concepts = []
    for paper in papers:
        text = extract_text_from_url(paper["pdf_url"])
        concepts = extract_concepts(text, paper)
        all_new_concepts.extend(concepts)

    if all_new_concepts:
        update_index_with_new_concepts(all_new_concepts)
        print(f"[arXiv daemon] Added {len(all_new_concepts)} new concepts to index")

    set_last_ingestion_date()

def start_daemon():
    scheduler = BlockingScheduler()
    scheduler.add_job(weekly_ingestion_job, "cron", day_of_week="mon", hour=2)
    scheduler.start()

if __name__ == "__main__":
    weekly_ingestion_job()   # Run once immediately for testing
    # start_daemon()         # Uncomment for production
```

### Step 2 — Build `ingestion/concept_extractor.py`
```python
# ingestion/concept_extractor.py
import json, os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EXTRACT_PROMPT = """You are an expert in DevOps and Microservice Architecture (MSA).
Given the following text from an academic paper, extract ALL DevOps and MSA concepts mentioned.
For each concept, output JSON with these fields:
- devops_concept: canonical DevOps concept name (use Ontology v1.0 terms where possible)
- msa_concept: corresponding MSA concept it maps to
- definition: one sentence definition
- taxonomy_category: one of [Deployment Automation, Observability, Scalability, Security, Configuration]
- evidence_type: "empirical" or "conceptual"
- source_title: paper title

Return ONLY a JSON array. No other text.

Text:
{text}"""

def extract_concepts(text: str, paper_meta: dict) -> list[dict]:
    # Truncate to avoid token limits
    truncated = text[:4000]
    prompt = EXTRACT_PROMPT.format(text=truncated)
    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        concepts = json.loads(raw)
        for c in concepts:
            c["source_arxiv_id"] = paper_meta["arxiv_id"]
            c["source_title"] = paper_meta["title"]
        return concepts
    except Exception as e:
        print(f"[concept_extractor] Error: {e}")
        return []
```

### Step 3 — Build `knowledge_base/drift_detector.py`
```python
# knowledge_base/drift_detector.py
import numpy as np
import faiss, json
from sentence_transformers import SentenceTransformer

DRIFT_THRESHOLD = 0.15   # From config

def compute_corpus_centroid(index_path: str) -> np.ndarray:
    index = faiss.read_index(index_path)
    # Reconstruct all vectors
    n = index.ntotal
    vecs = np.zeros((n, index.d), dtype=np.float32)
    for i in range(n):
        index.reconstruct(i, vecs[i])
    return vecs.mean(axis=0)

def check_drift(new_concepts: list[dict], old_centroid: np.ndarray,
                index_path: str) -> dict:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    texts = [f"{c['devops_concept']}: {c.get('definition','')}" for c in new_concepts]
    new_embeddings = model.encode(texts, normalize_embeddings=True)
    new_centroid = new_embeddings.mean(axis=0)

    cosine_shift = 1.0 - float(np.dot(old_centroid, new_centroid) /
                                (np.linalg.norm(old_centroid) * np.linalg.norm(new_centroid)))

    return {
        "cosine_shift":  round(cosine_shift, 4),
        "drift_detected": cosine_shift > DRIFT_THRESHOLD,
        "alert_message":  (f"Concept drift detected (shift={cosine_shift:.3f} > "
                           f"threshold={DRIFT_THRESHOLD}). "
                           f"Consider reviewing Ontology v1.0.")
                          if cosine_shift > DRIFT_THRESHOLD else None
    }
```

### Checkpoint ✅
- [ ] arXiv API fetches papers correctly
- [ ] PyMuPDF extracts text from at least 10 test PDFs
- [ ] Concept extractor returns valid JSON for test papers
- [ ] FAISS HNSW `add()` increases index size correctly
- [ ] Drift detector returns correct cosine shift values
- [ ] Run daemon once manually and inspect new_concepts.json

---

## 9. Week 4 — Multimodal Input Agent (N3)

### Goal
Accept 4 artifact types and convert them into structured DevOps–MSA concept context JSON.

### Step 1 — Build `multimodal/vision_processor.py`
```python
# multimodal/vision_processor.py
import base64, os, json
import google.generativeai as genai
from pathlib import Path

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_VISION_MODEL", "gemini-2.0-flash-exp"))

DIAGRAM_PROMPT = """Analyse this software architecture diagram carefully.
Identify ALL visible DevOps and MSA components, patterns, and relationships.
For each identified element, provide:
1. component_name: exact name as shown in diagram
2. taxonomy_category: one of [Deployment Automation, Observability, Scalability, Security, Configuration]
3. mapping_direction: "DevOps", "MSA", or "both"
4. missing_categories: list taxonomy categories with NO visible components

Return ONLY valid JSON with keys: components (list), missing_categories (list).
Do not include any explanation outside the JSON."""

DASHBOARD_PROMPT = """Analyse this monitoring/observability dashboard screenshot.
Identify which observability signals ARE visible (metrics, logs, traces, alerts).
Identify which observability signals are MISSING from a complete DevOps–MSA setup.
Map findings to DevOps–MSA Observability taxonomy.

Return ONLY valid JSON with keys:
- present_signals: list of visible monitoring components
- missing_signals: list of gaps vs. best practice
- taxonomy_coverage: percentage of Observability category covered (0-100)"""

def process_image(image_path: str, prompt_type: str = "diagram") -> dict:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine MIME type
    suffix = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".pdf": "application/pdf"}
    mime_type = mime_map.get(suffix, "image/png")

    prompt = DIAGRAM_PROMPT if prompt_type == "diagram" else DASHBOARD_PROMPT

    response = model.generate_content([
        {"mime_type": mime_type, "data": image_data},
        prompt
    ])
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
```

### Step 2 — Build `multimodal/yaml_parser.py`
```python
# multimodal/yaml_parser.py
import yaml, re

CICD_CONCEPT_MAP = {
    "stages":      ("CI/CD",             "Service Deployment Pipeline"),
    "deploy":      ("Deployment Automation", "Automated Service Deployment"),
    "test":        ("Automated Testing", "Microservice Load Testing"),
    "docker":      ("Containerisation",  "Containerised Microservices"),
    "kubernetes":  ("Container Orchestration", "Independent Service Deployment"),
    "helm":        ("Deployment Automation", "Service Composition"),
    "terraform":   ("Infrastructure as Code", "Cloud-Native Setup"),
    "monitor":     ("Monitoring",        "Runtime Diagnostics"),
    "secrets":     ("Secrets Management","Secure Service Deployment"),
    "lint":        ("Code Quality",      "Service Modularisation"),
    "scan":        ("DevSecOps",         "Access Control"),
    "cache":       ("Build Optimisation","Service Performance"),
}

def parse_cicd_yaml(file_path: str) -> dict:
    with open(file_path) as f:
        data = yaml.safe_load(f)

    content_lower = open(file_path).read().lower()
    found_concepts = []
    for keyword, (devops_concept, msa_concept) in CICD_CONCEPT_MAP.items():
        if keyword in content_lower:
            found_concepts.append({
                "devops_concept": devops_concept,
                "msa_concept":    msa_concept,
                "source_keyword": keyword,
                "taxonomy_category": _infer_category(devops_concept)
            })

    # Detect missing critical stages
    missing = []
    critical = ["test", "deploy", "monitor", "scan"]
    for c in critical:
        if c not in content_lower:
            missing.append(f"No {c} stage detected")

    return {
        "artifact_type":    "cicd_yaml",
        "detected_concepts": found_concepts,
        "missing_signals":  missing,
        "raw_stages":       list(data.get("stages", data.get("jobs", {}).keys()))
    }

def _infer_category(devops_concept: str) -> str:
    category_map = {
        "CI/CD": "Deployment Automation", "Deployment": "Deployment Automation",
        "Container": "Deployment Automation", "Infrastructure": "Configuration",
        "Monitoring": "Observability", "Secrets": "Security",
        "DevSecOps": "Security", "Testing": "Scalability"
    }
    for k, v in category_map.items():
        if k.lower() in devops_concept.lower():
            return v
    return "Deployment Automation"
```

### Step 3 — Build `multimodal/iac_parser.py`
```python
# multimodal/iac_parser.py
import hcl2, yaml, os

IaC_CONCEPT_MAP = {
    "aws_ecs_service":       ("Container Orchestration", "Containerised Microservices"),
    "kubernetes_deployment": ("Container Orchestration", "Independent Service Deployment"),
    "aws_api_gateway":       ("API Gateway",            "API Gateway Integration"),
    "helm_release":          ("Deployment Automation",  "Service Composition"),
    "aws_cloudwatch_metric": ("Monitoring",             "Runtime Diagnostics"),
    "datadog_monitor":       ("Monitoring",             "Service-Level Telemetry"),
    "vault_secret":          ("Secrets Management",     "Secure Service Deployment"),
    "aws_waf":               ("DevSecOps",              "Access Control"),
    "terraform_backend":     ("Infrastructure as Code", "Cloud-Native Setup"),
    "null_resource":         ("Automation",             "Dynamic Service Composition"),
}

def parse_terraform(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = hcl2.load(f)

    found_resources = []
    if "resource" in data:
        for resource_block in data["resource"]:
            for resource_type, instances in resource_block.items():
                for rt, (devops, msa) in IaC_CONCEPT_MAP.items():
                    if rt.lower() in resource_type.lower():
                        found_resources.append({
                            "resource_type":  resource_type,
                            "devops_concept": devops,
                            "msa_concept":    msa,
                            "taxonomy_category": "Configuration"
                        })

    return {
        "artifact_type":     "terraform_iac",
        "detected_concepts": found_resources,
        "providers":         _extract_providers(data),
        "missing_signals":   _detect_missing(found_resources)
    }

def _extract_providers(data: dict) -> list:
    providers = []
    for block in data.get("provider", []):
        providers.extend(block.keys())
    return providers

def _detect_missing(found: list) -> list:
    found_devops = {c["devops_concept"] for c in found}
    critical = {"Monitoring", "Secrets Management", "DevSecOps", "API Gateway"}
    return [f"Missing: {c}" for c in critical - found_devops]
```

### Step 4 — Build `multimodal/agent.py` (dispatcher)
```python
# multimodal/agent.py
from pathlib import Path
from multimodal.vision_processor import process_image
from multimodal.yaml_parser import parse_cicd_yaml
from multimodal.iac_parser import parse_terraform
from multimodal.concept_normaliser import normalise_to_ontology

SUPPORTED_EXTENSIONS = {
    ".png": "diagram", ".jpg": "diagram", ".jpeg": "diagram",
    ".pdf": "diagram",
    ".yml": "yaml",  ".yaml": "yaml",
    ".tf":  "terraform"
}

def preprocess_artifact(file_path: str) -> dict:
    """Main entry point — dispatches to correct parser based on file type."""
    path = Path(file_path)
    ext  = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return {"error": f"Unsupported file type: {ext}",
                "supported": list(SUPPORTED_EXTENSIONS.keys())}

    artifact_type = SUPPORTED_EXTENSIONS[ext]

    if artifact_type == "diagram":
        raw = process_image(file_path, prompt_type="diagram")
    elif artifact_type == "yaml":
        raw = parse_cicd_yaml(file_path)
    elif artifact_type == "terraform":
        raw = parse_terraform(file_path)

    # Normalise all extracted concepts against Ontology v1.0
    normalised = normalise_to_ontology(raw)

    return {
        "artifact_path":  file_path,
        "artifact_type":  artifact_type,
        "raw_extraction": raw,
        "normalised_concepts": normalised,
        "query_enrichment": _build_query_context(normalised)
    }

def _build_query_context(normalised: dict) -> str:
    """Convert parsed artifact into a text query enrichment for the Planner."""
    concepts = normalised.get("concepts", [])
    missing  = normalised.get("missing", [])
    parts = []
    if concepts:
        names = [c["devops_concept"] for c in concepts[:8]]
        parts.append(f"Detected DevOps/MSA components: {', '.join(names)}.")
    if missing:
        parts.append(f"Missing from architecture: {', '.join(missing[:5])}.")
    return " ".join(parts) if parts else "No concepts extracted from artifact."
```

### Checkpoint ✅
- [ ] Architecture diagram (test with any draw.io PNG export) → returns concepts JSON
- [ ] GitHub Actions YAML → correctly detects CI/CD stages and gaps
- [ ] Terraform file → identifies resource types and missing patterns
- [ ] `_build_query_context()` produces readable text enrichment
- [ ] All 4 inputs produce `normalised_concepts` that match Ontology v1.0 labels

---

## 10. Week 5–6 — Agentic Reasoning Loop (N1)

### Goal
Four-agent LangGraph graph replacing the base paper's linear query→retrieve→generate pipeline.

### Step 1 — Build `agents/state.py`
```python
# agents/state.py
from typing import TypedDict, Annotated
import operator

class MARCOState(TypedDict):
    # Input
    original_query:        str
    artifact_context:      str          # From multimodal agent (empty if text-only)

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

    # Generator outputs
    final_mappings:        list[dict]   # [{concept, justification, citation, category}]
    reasoning_trace:       list[str]    # Log of all agent decisions
    confidence_scores:     list[float]  # Raw scores for MAPIE
```

### Step 2 — Build `agents/planner.py`
```python
# agents/planner.py
import json, os
from groq import Groq
from agents.state import MARCOState

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLANNER_PROMPT = """You are a DevOps-MSA concept alignment expert.
Given a practitioner query, decompose it into a structured retrieval plan.

Query: {query}
Artifact context (if any): {artifact_context}

Taxonomy categories available:
1. Deployment Automation & Orchestration
2. Observability & Runtime Diagnostics
3. Scalability & Modularity
4. Security & Governance
5. Configuration & Environment Management

Return ONLY valid JSON with these keys:
- intent: "DevOps→MSA", "MSA→DevOps", or "bidirectional"
- sub_questions: list of 2-3 specific retrieval sub-questions
- taxonomy_categories: list of relevant category names (1-3)
- reasoning: one sentence explaining the decomposition"""

def run_planner(state: MARCOState) -> MARCOState:
    query   = state["original_query"]
    context = state.get("artifact_context", "")

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[{"role":"user",
                   "content": PLANNER_PROMPT.format(
                       query=query, artifact_context=context or "None")}],
        temperature=float(os.getenv("GROQ_TEMPERATURE", 0.1)),
        max_tokens=512
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    plan = json.loads(raw)

    state["intent"]              = plan["intent"]
    state["sub_questions"]       = plan["sub_questions"]
    state["taxonomy_categories"] = plan["taxonomy_categories"]
    state["reasoning_trace"].append(
        f"[Planner] Intent: {plan['intent']} | "
        f"Sub-Qs: {len(plan['sub_questions'])} | "
        f"Categories: {plan['taxonomy_categories']} | "
        f"Reasoning: {plan['reasoning']}"
    )
    return state
```

### Step 3 — Build `agents/retriever.py`
```python
# agents/retriever.py
import faiss, json, os
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from agents.state import MARCOState

_embedder  = None
_reranker  = None
_index     = None
_metadata  = None
_bm25      = None

def _load_models():
    global _embedder, _reranker, _index, _metadata, _bm25
    if _embedder is None:
        _embedder  = SentenceTransformer(os.getenv("EMBEDDING_MODEL"))
        _reranker  = CrossEncoder(os.getenv("RERANKER_MODEL"))
        _index     = faiss.read_index(os.getenv("FAISS_INDEX_PATH"))
        with open("knowledge_base/index/metadata.json") as f:
            _metadata = json.load(f)
        # Build BM25 over text corpus
        corpus = [f"{m['devops_concept']} {m.get('definition','')}" for m in _metadata]
        tokenised = [doc.lower().split() for doc in corpus]
        _bm25 = BM25Okapi(tokenised)

def run_retriever(state: MARCOState) -> MARCOState:
    _load_models()
    top_k = int(os.getenv("TOP_K", 5))
    all_candidates = []

    for sub_q in state["sub_questions"]:
        # Dense retrieval
        q_emb = _embedder.encode([sub_q], normalize_embeddings=True)
        scores, indices = _index.search(q_emb.astype(np.float32), top_k * 2)

        dense_hits = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(_metadata):
                hit = dict(_metadata[idx])
                hit["dense_score"] = float(score)
                hit["sub_question"] = sub_q
                dense_hits.append(hit)

        # Sparse BM25 retrieval
        tokens = sub_q.lower().split()
        bm25_scores = _bm25.get_scores(tokens)
        top_bm25 = np.argsort(bm25_scores)[::-1][:top_k * 2]
        sparse_hits = []
        for idx in top_bm25:
            hit = dict(_metadata[idx])
            hit["bm25_score"] = float(bm25_scores[idx])
            hit["sub_question"] = sub_q
            sparse_hits.append(hit)

        # Merge and deduplicate by concept ID
        merged = {h["id"]: h for h in dense_hits + sparse_hits}.values()
        merged = list(merged)[:top_k * 3]

        # Cross-encoder reranking
        pairs   = [(sub_q, f"{h['devops_concept']}: {h.get('definition','')}")
                   for h in merged]
        re_scores = _reranker.predict(pairs)
        for h, s in zip(merged, re_scores):
            h["rerank_score"] = float(s)
        merged.sort(key=lambda x: x["rerank_score"], reverse=True)
        all_candidates.extend(merged[:top_k])

    # Final deduplication keeping highest rerank score per concept
    seen = {}
    for c in all_candidates:
        cid = c["id"]
        if cid not in seen or c["rerank_score"] > seen[cid]["rerank_score"]:
            seen[cid] = c
    final = sorted(seen.values(), key=lambda x: x["rerank_score"], reverse=True)[:top_k]

    state["retrieved_candidates"] = final
    state["reasoning_trace"].append(
        f"[Retriever] Retrieved {len(final)} candidates across "
        f"{len(state['sub_questions'])} sub-questions. "
        f"Top rerank score: {final[0]['rerank_score']:.3f}"
    )
    return state
```

### Step 4 — Build `agents/critic.py`
```python
# agents/critic.py
import os
from ragas.metrics import context_relevancy
from agents.state import MARCOState

RELEVANCE_THRESHOLD    = float(os.getenv("RAGAS_RELEVANCE_THRESHOLD", 1.0))
MIN_HIGH_QUALITY_RATIO = float(os.getenv("MIN_HIGH_QUALITY_RATIO", 0.5))
MAX_RETRIES            = int(os.getenv("MAX_RETRY_CYCLES", 2))

def run_critic(state: MARCOState) -> MARCOState:
    candidates = state["retrieved_candidates"]
    query      = state["original_query"]
    graded     = []

    for candidate in candidates:
        # Score relevance using RAGAS
        context_text = f"{candidate['devops_concept']}: {candidate.get('definition','')}"
        # Simplified RAGAS-style relevance (keyword overlap + semantic check)
        overlap  = _keyword_overlap(query, context_text)
        accepted = overlap >= RELEVANCE_THRESHOLD

        graded.append({**candidate, "ragas_score": overlap, "accepted": accepted})

    accepted_count = sum(1 for g in graded if g["accepted"])
    ratio          = accepted_count / len(graded) if graded else 0.0
    retry_needed   = (ratio < MIN_HIGH_QUALITY_RATIO and
                      state.get("retrieval_attempt", 0) < MAX_RETRIES)

    state["graded_candidates"]   = graded
    state["hallucination_risk"]  = accepted_count == 0
    state["retry_needed"]        = retry_needed
    state["retry_reason"]        = (f"Only {accepted_count}/{len(graded)} candidates "
                                    f"meet relevance threshold {RELEVANCE_THRESHOLD}"
                                    if retry_needed else "")
    state["retrieval_attempt"]   = state.get("retrieval_attempt", 0) + 1

    state["reasoning_trace"].append(
        f"[Critic] Accepted: {accepted_count}/{len(graded)} candidates. "
        f"Retry needed: {retry_needed}. "
        f"Hallucination risk: {state['hallucination_risk']}"
    )
    return state

def _keyword_overlap(query: str, context: str) -> float:
    q_words = set(query.lower().split())
    c_words = set(context.lower().split())
    stopwords = {"a","an","the","is","in","of","to","and","or","for","with","on","at"}
    q_words -= stopwords
    c_words -= stopwords
    if not q_words:
        return 0.0
    return len(q_words & c_words) / len(q_words)
```

### Step 5 — Build `agents/generator.py`
```python
# agents/generator.py
import json, os
import google.generativeai as genai
from agents.state import MARCOState

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_model = genai.GenerativeModel(os.getenv("GEMINI_TEXT_MODEL","gemini-2.0-flash-exp"))

GENERATOR_PROMPT = """You are a DevOps-MSA concept alignment expert.
Given the following validated concept evidence, generate precise bidirectional mappings.

Original query: {query}
Mapping intent: {intent}

Validated evidence:
{evidence}

Return ONLY valid JSON: a list of mappings, each with:
- devops_concept: canonical DevOps concept
- msa_concept: corresponding MSA concept  
- justification: one sentence grounded in the evidence above
- taxonomy_category: one of the 5 categories
- citation_ids: list of source IDs from the evidence
- confidence_signal: "high" | "medium" | "low" based on evidence strength"""

def run_generator(state: MARCOState) -> MARCOState:
    accepted = [c for c in state["graded_candidates"] if c["accepted"]]
    if not accepted:
        accepted = state["graded_candidates"][:3]   # fallback

    evidence_text = "\n".join([
        f"[{c['id']}] {c['devops_concept']} → {c.get('msa_concept','?')}: "
        f"{c.get('definition','')}"
        for c in accepted
    ])

    prompt = GENERATOR_PROMPT.format(
        query=state["original_query"],
        intent=state["intent"],
        evidence=evidence_text
    )
    response = _model.generate_content(prompt)
    raw = response.text.strip().replace("```json","").replace("```","").strip()
    mappings = json.loads(raw)

    state["final_mappings"]    = mappings
    state["confidence_scores"] = [c.get("rerank_score", 0.5) for c in accepted]
    state["reasoning_trace"].append(
        f"[Generator] Produced {len(mappings)} final mappings. "
        f"Intent: {state['intent']}."
    )
    return state
```

### Step 6 — Build `agents/graph.py` (LangGraph orchestrator)
```python
# agents/graph.py
from langgraph.graph import StateGraph, END
from agents.state import MARCOState
from agents.planner   import run_planner
from agents.retriever import run_retriever
from agents.critic    import run_critic
from agents.generator import run_generator

def should_retry(state: MARCOState) -> str:
    """Conditional edge: retry retrieval or proceed to generation."""
    if state.get("retry_needed", False):
        return "retriever"   # Loop back
    return "generator"       # Proceed

def build_graph() -> StateGraph:
    graph = StateGraph(MARCOState)

    graph.add_node("planner",   run_planner)
    graph.add_node("retriever", run_retriever)
    graph.add_node("critic",    run_critic)
    graph.add_node("generator", run_generator)

    graph.set_entry_point("planner")
    graph.add_edge("planner",   "retriever")
    graph.add_edge("retriever", "critic")
    graph.add_conditional_edges("critic", should_retry,
                                {"retriever": "retriever", "generator": "generator"})
    graph.add_edge("generator", END)

    return graph.compile()

# Main query function
def run_marco(query: str, artifact_context: str = "") -> dict:
    app = build_graph()
    initial_state: MARCOState = {
        "original_query":      query,
        "artifact_context":    artifact_context,
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
        "reasoning_trace":     [],
        "confidence_scores":   []
    }
    result = app.invoke(initial_state)
    return result
```

### Checkpoint ✅
- [ ] `run_marco("CI/CD")` returns structured final_mappings
- [ ] Reasoning trace captures all 4 agent decisions
- [ ] Critic retry fires correctly when candidates are weak
- [ ] Max 2 retries respected (no infinite loops)
- [ ] Graph compiles without LangGraph errors

---

## 11. Week 7 — Uncertainty Quantification (N7)

### Goal
Attach calibrated confidence bounds to every recommendation using MAPIE conformal prediction.

### Step 1 — Build `uncertainty/calibrator.py`
```python
# uncertainty/calibrator.py
import json, numpy as np, pickle, os
from mapie.regression import MapieRegressor
from sklearn.linear_model import Ridge

COVERAGE_TARGET   = float(os.getenv("MAPIE_COVERAGE_TARGET", 0.80))
CALIBRATOR_PATH   = "uncertainty/mapie_calibrator.pkl"

def build_calibration_dataset(eval_results_path: str) -> tuple:
    """Build X (rerank scores) and y (0/1/2 relevance) from eval results."""
    with open(eval_results_path) as f:
        results = json.load(f)

    X, y = [], []
    for item in results:
        for candidate in item.get("graded_candidates", []):
            score   = candidate.get("rerank_score", 0.5)
            label   = candidate.get("human_label", 0)
            X.append([score])
            y.append(label)

    return np.array(X), np.array(y, dtype=float)

def fit_calibrator(eval_results_path: str) -> None:
    """Fit MAPIE on the base paper's 50-query labeled set."""
    X, y = build_calibration_dataset(eval_results_path)
    base_model = Ridge()
    calibrator = MapieRegressor(estimator=base_model,
                                method="plus",
                                cv=5)
    calibrator.fit(X, y)
    with open(CALIBRATOR_PATH, "wb") as f:
        pickle.dump(calibrator, f)
    print(f"Calibrator fitted on {len(y)} samples, saved to {CALIBRATOR_PATH}")
```

### Step 2 — Build `uncertainty/scorer.py`
```python
# uncertainty/scorer.py
import pickle, numpy as np, os
from uncertainty.badge_mapper import score_to_badge

CALIBRATOR_PATH = "uncertainty/mapie_calibrator.pkl"
COVERAGE_TARGET = float(os.getenv("MAPIE_COVERAGE_TARGET", 0.80))
_calibrator     = None

def _load():
    global _calibrator
    if _calibrator is None:
        with open(CALIBRATOR_PATH, "rb") as f:
            _calibrator = pickle.load(f)

def score_recommendations(rerank_scores: list[float]) -> list[dict]:
    """Return confidence bounds for each recommendation."""
    _load()
    X = np.array(rerank_scores).reshape(-1, 1)
    _, intervals = _calibrator.predict(X, alpha=1.0 - COVERAGE_TARGET)

    results = []
    for score, interval in zip(rerank_scores, intervals):
        lower = float(interval[0][0])
        upper = float(interval[1][0])
        badge = score_to_badge(score)
        results.append({
            "raw_score":   round(score, 4),
            "lower_bound": round(lower, 4),
            "upper_bound": round(upper, 4),
            "coverage":    COVERAGE_TARGET,
            "badge":       badge
        })
    return results
```

### Step 3 — Build `uncertainty/badge_mapper.py`
```python
# uncertainty/badge_mapper.py
import os

HIGH_T   = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD",   0.75))
MEDIUM_T = float(os.getenv("CONFIDENCE_MEDIUM_THRESHOLD", 0.50))

BADGE_COLORS = {
    "HIGH":   "#2D7D46",   # Green
    "MEDIUM": "#B45309",   # Amber
    "LOW":    "#B91C1C"    # Red
}

def score_to_badge(score: float) -> str:
    if score >= HIGH_T:
        return "HIGH"
    elif score >= MEDIUM_T:
        return "MEDIUM"
    return "LOW"

def badge_html(badge: str) -> str:
    color = BADGE_COLORS[badge]
    return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{badge}</span>'
```

### Step 4 — Build `uncertainty/evaluator.py`
```python
# uncertainty/evaluator.py
import json, numpy as np
import matplotlib.pyplot as plt
from netcal.metrics import ECE
from netcal.presentation import ReliabilityDiagram

def compute_ece(scores: list[float], labels: list[int],
                n_bins: int = 10) -> float:
    scores_arr = np.array(scores)
    labels_arr = (np.array(labels) > 0).astype(int)   # binarise
    ece = ECE(n_bins)
    return float(ece.measure(scores_arr, labels_arr))

def plot_reliability_diagram(scores: list[float], labels: list[int],
                              output_path: str = "paper/figures/fig7_reliability_diagram.png") -> None:
    scores_arr = np.array(scores)
    labels_arr = (np.array(labels) > 0).astype(int)
    diagram = ReliabilityDiagram(10)
    diagram.plot(scores_arr, labels_arr, title="MARCO Confidence Calibration")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Reliability diagram saved to {output_path}")
```

### Checkpoint ✅
- [ ] Calibrator fits without error on 50-query set
- [ ] `score_recommendations([0.9, 0.6, 0.3])` returns correct badges
- [ ] ECE < 0.15 on calibration set (acceptable starting point)
- [ ] Reliability diagram generates as PNG
- [ ] Uncertainty scores integrate into `agents/generator.py` output

---

## 12. Week 8–9 — Evaluation & Ablation

### Evaluation runner — `evaluation/run_eval.py`
```python
# evaluation/run_eval.py
import json, argparse
from evaluation.metrics import precision_at_k, ndcg_at_k, rae_at_k
from agents.graph import run_marco
from agents.retriever import run_retriever   # for baseline mode
from evaluation.inter_rater import compute_kappa

def evaluate(queries_path: str, mode: str = "marco",
             k_values: list = [3, 5, 10]) -> dict:
    with open(queries_path) as f:
        queries = json.load(f)

    all_results = []
    for query_item in queries:
        query  = query_item["query"]
        gold   = query_item["gold_labels"]   # {concept_id: 0|1|2}

        if mode == "marco":
            result = run_marco(query, query_item.get("artifact_path",""))
            ranked = [(m["devops_concept"], m.get("confidence_scores",{}).get("raw_score",0.5))
                      for m in result["final_mappings"]]
        elif mode == "baseline":
            from agents.state import MARCOState
            state = MARCOState(original_query=query, artifact_context="",
                               intent="", sub_questions=[query], taxonomy_categories=[],
                               retrieved_candidates=[], retrieval_attempt=0,
                               graded_candidates=[], hallucination_risk=False,
                               retry_needed=False, retry_reason="",
                               final_mappings=[], reasoning_trace=[], confidence_scores=[])
            state = run_retriever(state)
            ranked = [(c["devops_concept"], c.get("rerank_score",0))
                      for c in state["retrieved_candidates"]]

        metrics = {}
        for k in k_values:
            ranked_ids = [r[0] for r in ranked[:k]]
            labels     = [gold.get(r, 0) for r in ranked_ids]
            metrics[f"P@{k}"]    = precision_at_k(labels, k)
            metrics[f"nDCG@{k}"] = ndcg_at_k(labels, k)
        metrics["RAE@5"] = rae_at_k(ranked, gold, 5)

        all_results.append({"query": query, "metrics": metrics, "ranked": ranked})

    # Aggregate
    aggregate = {}
    for k in k_values:
        aggregate[f"P@{k}"]    = round(sum(r["metrics"][f"P@{k}"] for r in all_results) / len(all_results), 4)
        aggregate[f"nDCG@{k}"] = round(sum(r["metrics"][f"nDCG@{k}"] for r in all_results) / len(all_results), 4)
    aggregate["RAE@5"] = round(sum(r["metrics"]["RAE@5"] for r in all_results) / len(all_results), 4)
    aggregate["n_queries"] = len(all_results)

    output = {"mode": mode, "aggregate": aggregate, "per_query": all_results}
    with open(f"evaluation/results/{mode}.json","w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(aggregate, indent=2))
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",    default="marco",
                        choices=["marco","baseline","bm25","embed_only",
                                 "ablation_e1","ablation_e2","ablation_e3","ablation_e4"])
    parser.add_argument("--queries", default="data/eval/queries_80.json")
    args = parser.parse_args()
    evaluate(args.queries, args.mode)
```

### How to run all experiments
```bash
# 1. Full MARCO evaluation
python3 evaluation/run_eval.py --mode marco --queries data/eval/queries_80.json

# 2. Base paper baseline (reproduced)
python3 evaluation/run_eval.py --mode baseline --queries data/base/eval_queries_50.json

# 3. BM25 only
python3 evaluation/run_eval.py --mode bm25 --queries data/eval/queries_80.json

# 4. All ablations
for mode in ablation_e1 ablation_e2 ablation_e3 ablation_e4; do
    python3 evaluation/run_eval.py --mode $mode --queries data/eval/queries_80.json
done

# 5. Compute Cohen's κ (run after double annotation)
python3 evaluation/inter_rater.py --labels1 data/eval/labels_annotator1.json \
                                   --labels2 data/eval/labels_annotator2.json

# 6. Compute ECE
python3 -c "
from uncertainty.evaluator import compute_ece, plot_reliability_diagram
import json
with open('evaluation/results/marco.json') as f:
    results = json.load(f)
scores = [c['rerank_score'] for r in results['per_query'] for c in r.get('graded_candidates',[])]
labels = [c.get('human_label',0) for r in results['per_query'] for c in r.get('graded_candidates',[])]
print('ECE:', compute_ece(scores, labels))
plot_reliability_diagram(scores, labels)
"
```

---

## 13. Week 10 — UI, Deployment & Paper Writeup

### Streamlit UI — `ui/app.py`
```python
# ui/app.py
import streamlit as st
import tempfile, os, json
from agents.graph import run_marco
from multimodal.agent import preprocess_artifact
from uncertainty.scorer import score_recommendations

st.set_page_config(page_title="MARCO", page_icon="⚙️", layout="wide")
st.title("MARCO — DevOps–MSA Concept Alignment")
st.caption("Multimodal Agentic RAG | Based on Khadem & Movaghar (2025)")

# Sidebar
with st.sidebar:
    st.header("Query options")
    query_mode = st.radio("Input type", ["Text query", "Upload artifact"])
    st.divider()
    st.caption("All recommendations grounded in 200+ DevOps–MSA concept mappings.")

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
            artifact_context = parsed["query_enrichment"]
            st.info(f"Detected: {artifact_context[:200]}...")

run_button = st.button("Get recommendations", type="primary")

if run_button and (query or artifact_context):
    full_query = query or "Analyse this architecture artifact for DevOps–MSA gaps"
    with st.spinner("Running MARCO agents..."):
        result = run_marco(full_query, artifact_context)
        confidence = score_recommendations(result.get("confidence_scores", [0.5]))

    st.divider()

    # Results
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Recommendations")
        for i, mapping in enumerate(result.get("final_mappings", [])):
            badge_info = confidence[i] if i < len(confidence) else {"badge": "MEDIUM"}
            badge_colors = {"HIGH": "green", "MEDIUM": "orange", "LOW": "red"}
            badge = badge_info["badge"]
            st.markdown(f"**:{badge_colors[badge]}[{badge}]** "
                        f"**{mapping.get('devops_concept','')}** → "
                        f"*{mapping.get('msa_concept','')}*")
            st.caption(f"_{mapping.get('justification','')}_ "
                       f"[{mapping.get('taxonomy_category','')}]")
            st.divider()

    with col2:
        st.subheader("Reasoning trace")
        for step in result.get("reasoning_trace", []):
            st.code(step, language=None)

---

## 14. Complete File Reference

| File | Purpose | Week |
|---|---|---|
| `config.py` | All constants — read from `.env` | W1 |
| `data/base/*.json` | Base paper assets | W1 |
| `knowledge_base/builder.py` | FAISS HNSW index construction | W1 |
| `knowledge_base/chroma_store.py` | ChromaDB metadata store | W1 |
| `knowledge_base/updater.py` | Incremental index updates | W3 |
| `knowledge_base/drift_detector.py` | Cosine shift monitoring | W3 |
| `ingestion/arxiv_daemon.py` | Weekly paper fetch | W3 |
| `ingestion/pdf_parser.py` | PyMuPDF text extraction | W3 |
| `ingestion/concept_extractor.py` | Groq LLM concept extraction | W3 |
| `multimodal/vision_processor.py` | Gemini Flash Vision | W4 |
| `multimodal/yaml_parser.py` | CI/CD YAML parsing | W4 |
| `multimodal/iac_parser.py` | Terraform/Ansible parsing | W4 |
| `multimodal/concept_normaliser.py` | Ontology v1.0 mapping | W4 |
| `multimodal/agent.py` | Artifact dispatcher | W4 |
| `agents/state.py` | LangGraph typed state | W5 |
| `agents/planner.py` | Agent 1: decomposition | W5 |
| `agents/retriever.py` | Agent 2: hybrid search | W5 |
| `agents/critic.py` | Agent 3: grading + retry | W6 |
| `agents/generator.py` | Agent 4: Gemini synthesis | W6 |
| `agents/graph.py` | LangGraph orchestrator | W6 |
| `uncertainty/calibrator.py` | MAPIE fitting | W7 |
| `uncertainty/scorer.py` | Inference-time bounds | W7 |
| `uncertainty/badge_mapper.py` | Score → badge | W7 |
| `uncertainty/evaluator.py` | ECE + reliability diagram | W7 |
| `evaluation/metrics.py` | P@k, nDCG@k, RAE@k | W1 |
| `evaluation/run_eval.py` | Main eval runner | W8 |
| `evaluation/ablation.py` | Ablation configs | W9 |
| `evaluation/inter_rater.py` | Cohen's κ | W8 |
| `evaluation/annotation_tool.py` | CLI labeling tool | W8 |
| `ui/app.py` | Streamlit application | W10 |
| `scripts/run_full_eval.sh` | One-command eval | W9 |
| `scripts/generate_figures.sh` | Paper figures | W10 |

---

## 15. All Dependencies

### `requirements.txt`
```
# Core ML
sentence-transformers==3.0.1
faiss-cpu==1.8.0
torch==2.3.1

# LLM APIs
groq==0.9.0
google-generativeai==0.7.2
langchain==0.2.14
langchain-groq==0.1.9
langchain-google-genai==1.0.8
langgraph==0.2.14

# Retrieval
rank-bm25==0.2.2
chromadb==0.5.5

# Multimodal
PyMuPDF==1.24.9
pdf2image==1.17.0
PyYAML==6.0.2
python-hcl2==4.3.4

# Uncertainty
mapie==0.8.6
netcal==1.3.5
scikit-learn==1.5.1

# Evaluation
ragas==0.1.20
scipy==1.14.0
numpy==1.26.4

# Ingestion
arxiv==2.1.3
apscheduler==3.10.4

# UI
streamlit==1.37.0

# Plotting
matplotlib==3.9.2
seaborn==0.13.2

# Utilities
python-dotenv==1.0.1
tqdm==4.66.5
loguru==0.7.2
```

---

## 16. Data Sources & Datasets

### Assets to download from base paper
| Asset | URL | Save to |
|---|---|---|
| concept_pairs.json | github.com/azizikhadem/devops-msa-mapping-rag | `data/base/` |
| faiss_index.bin | zenodo.org/record/16760389 | `knowledge_base/index/` |
| ontology_v1.json | same GitHub repo | `data/base/` |
| eval_queries_50.json | same GitHub repo | `data/base/` and `data/calibration/` |

### Artifact test files to create yourself (Week 4)
| File | How to get it | Taxonomy category tested |
|---|---|---|
| `diagram_k8s.png` | Export any K8s arch from draw.io | Deployment Automation |
| `diagram_microservices.png` | MSA diagram with 3+ services | Scalability |
| `diagram_monitoring.png` | Screenshot of any Grafana dashboard | Observability |
| `diagram_security.png` | Security architecture with IAM/WAF | Security |
| `diagram_cicd.png` | Jenkins or GitHub Actions pipeline diagram | Deployment Automation |
| `github_actions.yml` | Any public GitHub Actions workflow | Deployment Automation |
| `gitlab_ci.yml` | Any GitLab CI config | Deployment Automation |
| `k8s_deploy.yml` | Kubernetes Deployment YAML | Scalability |
| `docker_compose.yml` | Multi-service docker-compose | Scalability |
| `ansible_playbook.yml` | Any Ansible role | Configuration |
| `main.tf` | Any AWS/GCP Terraform config | Configuration |
| `variables.tf` | Terraform variable definitions | Configuration |
| `eks_cluster.tf` | EKS or GKE cluster Terraform | Scalability |
| `monitoring.tf` | CloudWatch/Datadog Terraform | Observability |
| `security.tf` | IAM/WAF Terraform | Security |

**Free sources for test files:**
- Architecture diagrams: search "microservices architecture draw.io template" on GitHub
- Terraform: github.com/hashicorp/terraform-provider-aws/tree/main/examples
- GitHub Actions: any public `.github/workflows/` directory
- Grafana dashboards: grafana.com/grafana/dashboards (screenshot any public one)

---

## 17. Evaluation Protocol

### Building the 80-query set
```
Queries 1–50:   Use base paper eval_queries_50.json unchanged
Queries 51–65:  15 new text queries on post-June 2025 concepts (write these yourself)
Queries 66–80:  15 artifact-based queries (one per artifact file in Section 16)
```

### Sample new text queries (51–65) — write similar ones
```json
[
  {"id": 51, "query": "How does platform engineering relate to DevOps team topology?",
   "taxonomy_category": "Deployment Automation"},
  {"id": 52, "query": "What MSA patterns support GitOps continuous reconciliation?",
   "taxonomy_category": "Configuration"},
  {"id": 53, "query": "How does eBPF-based observability align with microservice tracing?",
   "taxonomy_category": "Observability"},
  {"id": 54, "query": "What is the relationship between SLSA supply chain levels and MSA security?",
   "taxonomy_category": "Security"},
  {"id": 55, "query": "How does SBOM generation fit into a DevSecOps microservice pipeline?",
   "taxonomy_category": "Security"}
]
```

### Annotation workflow
```
1. Run MARCO on all 80 queries → save outputs to evaluation/results/raw_outputs.json
2. Annotator 1 labels top-5 per query using annotation_tool.py (CLI)
3. Annotator 2 labels same outputs independently
4. Run inter_rater.py to compute Cohen's κ
5. For κ < 0.80: adjudicate all disagreements with a third reviewer
6. Save final labels to data/eval/gold_labels.json
7. Run evaluation/run_eval.py with gold_labels
```

---

## 18. Ablation Experiment Design

| Experiment | What to change in code | Config flag |
|---|---|---|
| E1 — No Critic | In `agents/graph.py`: bypass critic, connect retriever→generator directly | `--mode ablation_e1` |
| E2 — No Multimodal | In `agents/graph.py`: set `artifact_context=""` for all artifact queries | `--mode ablation_e2` |
| E3 — No Adaptive Index | In `agents/retriever.py`: use original base paper index only, skip arXiv tool | `--mode ablation_e3` |
| E4 — No Uncertainty | In `ui/app.py` and output: skip `score_recommendations()`, report raw scores only | `--mode ablation_e4` |

---

## 19. Error Handling & Fallbacks

| Error | Where | Fallback |
|---|---|---|
| Groq rate limit (429) | `agents/planner.py`, `critic.py` | Retry with exponential backoff (1s, 2s, 4s) |
| Gemini 1500/day quota | `multimodal/vision_processor.py` | Fall back to LLaVA-1.5-7B via HF Inference API |
| Gemini text quota | `agents/generator.py` | Fall back to Groq Llama-3 for generation |
| arXiv unreachable | `ingestion/arxiv_daemon.py` | Log failure, retry next scheduled run |
| PDF parse failure | `ingestion/pdf_parser.py` | Extract abstract only from arXiv API metadata |
| FAISS index corrupt | `agents/retriever.py` | Rebuild from concept_pairs.json |
| HCL2 parse error | `multimodal/iac_parser.py` | Fall back to regex keyword matching |
| LangGraph state error | `agents/graph.py` | Return partial state with error flag |

---

## 20. Testing Strategy

### Unit tests — run before every commit
```bash
pytest tests/ -v --tb=short
```

### `tests/test_agents.py` — minimum test cases
```python
def test_planner_decomposes_query():
    from agents.graph import run_marco
    result = run_marco("What MSA patterns support CI/CD automation?")
    assert len(result["sub_questions"]) >= 2
    assert result["intent"] in ["DevOps→MSA","MSA→DevOps","bidirectional"]

def test_retriever_returns_candidates():
    assert len(result["retrieved_candidates"]) >= 3

def test_critic_scores_candidates():
    assert all("ragas_score" in c for c in result["graded_candidates"])

def test_generator_produces_mappings():
    assert len(result["final_mappings"]) >= 1
    assert all("justification" in m for m in result["final_mappings"])

def test_max_retries_respected():
    # Force weak query that triggers retries
    result = run_marco("xyzzy nonexistent concept 12345")
    assert result["retrieval_attempt"] <= 3   # max 2 retries + initial

def test_full_pipeline_no_exception():
    result = run_marco("observability in microservices")
    assert "reasoning_trace" in result
    assert len(result["reasoning_trace"]) == 4   # one per agent
```

### GitHub Actions CI — `.github/workflows/tests.yml`
```yaml
name: MARCO Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
```

---

## 21. Paper Placeholder Map

When experiments are complete, replace every `[[]]` in the paper:

| Placeholder | What to measure | Code location |
|---|---|---|
| P@5 MARCO | Aggregate P@5 | `evaluation/results/marco_full.json` → `aggregate.P@5` |
| nDCG@5 MARCO | Aggregate nDCG@5 | same file → `aggregate.nDCG@5` |
| Hallucination rate base | RAGAS faithfulness on base eval | `evaluation/results/baseline.json` |
| Hallucination rate MARCO | RAGAS faithfulness on MARCO | `evaluation/results/marco_full.json` |
| Concept recall artifacts | Recall on 15 artifact queries | `evaluation/results/marco_full.json` artifact subset |
| Concept recall text | Recall on text-only equivalents | `evaluation/results/ablation_e2.json` |
| ECE MARCO | `uncertainty/evaluator.py` output | logged during eval run |
| Cohen's κ | `evaluation/inter_rater.py` output | `evaluation/results/kappa.json` |
| Δ P@5 Security | Category subset analysis | filter by `taxonomy_category` |
| Fig 5 | Category P@5 bar chart | `notebooks/05_results_visualisation.ipynb` |
| Fig 6 | Artifact recall bar chart | same notebook |
| Fig 7 | Reliability diagram | `uncertainty/evaluator.py` → `plot_reliability_diagram()` |
| Fig 8 | Ablation comparison chart | same notebook |

---

## 22. Submission Checklist

### Before submitting the paper

**Code & reproducibility**
- [ ] All code pushed to public GitHub repository
- [ ] README.md includes one-command setup instructions
- [ ] `.env.example` committed (never `.env`)
- [ ] Zenodo DOI created for immutable snapshot
- [ ] All [[]] placeholders in paper replaced with real values
- [ ] All [[image]] slots replaced with actual figures
- [ ] All 22 references verified and formatted correctly

**Experimental validity**
- [ ] Baseline P@5 = 0.82 reproduced (±0.02)
- [ ] MARCO evaluated on all 80 queries
- [ ] Double annotation complete (both annotators labeled all queries)
- [ ] Cohen's κ ≥ 0.80
- [ ] All 4 ablation experiments run and recorded
- [ ] ECE computed and reliability diagram generated

**Paper requirements**
- [ ] Abstract under 220 words, no fabricated metrics
- [ ] All section headings numbered correctly (Roman numerals)
- [ ] Tables I–IV complete with actual values
- [ ] Figures 1–8 all inserted with captions
- [ ] Author names and affiliations filled in
- [ ] Acknowledgment section complete
- [ ] Page count within venue limit (IEEE Access: no limit; ICSE-SEIP: 10 pages)
- [ ] Template text fully removed (no "Heading 1" labels etc.)
- [ ] Spell-checked and grammar-checked

**Submission**
- [ ] IEEE Manuscript Central / ScholarOne account created
- [ ] Paper uploaded in PDF format (converted from .docx)
- [ ] Cover letter written mentioning [3] as base paper
- [ ] Suggested reviewers list prepared (3–5 names from related work)
- [ ] Copyright form ready

---

*This plan is version-controlled. Update this file as you complete each step.*
*Last updated: March 2026*
