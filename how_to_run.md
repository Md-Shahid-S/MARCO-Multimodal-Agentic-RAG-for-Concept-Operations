# How to Run and Evaluate: MARCO vs. Baseline

This guide provides instructions for running and evaluating the **Baseline RAG** (from the 2025 IEEE paper) and the **Proposed MARCO Framework**.

---

## 1. Prerequisites
Ensure you are in the project root and your virtual environment is activated:
```bash
# From project root
source venv/bin/activate
```

Ensure your `.env` file is configured with the necessary API keys (`GROQ_API_KEY`, `GEMINI_API_KEY`).

---

## 2. Baseline Model (Base Paper)

### A. Run a Single Query
To run the baseline model for a specific DevOps/MSA query:
```bash
cd baseline
python3 main.py
```
*(Note: You can edit `baseline/main.py` to change the query text at the bottom of the file.)*

### B. Evaluate the Baseline
To run the full evaluation suite (50 queries) for the baseline model:
```bash
cd baseline
python3 evaluation/run_eval.py
```
**Output:** The results will be saved to `baseline/evaluation/results/baseline_only.json`.

---

## 3. Proposed MARCO Model

### A. Run the Interactive UI
The proposed model features a Streamlit-based UI for interactive queries and artifact uploads:
```bash
cd proposed_solution
streamlit run ui/app.py
```
- **Text Query:** Enter any DevOps concept query.
- **Multimodal:** Upload architecture diagrams (PNG/PDF), CI/CD YAML, or Terraform files.

### B. Run a Batch Evaluation
To evaluate the proposed MARCO framework across all benchmarks (including multimodal and text queries):
```bash
cd proposed_solution
# Full MARCO evaluation
python3 evaluation/run_eval.py --mode marco --queries data/base/eval_queries_50.json
```

### C. Run Ablation Studies
To verify the impact of specific components (Critic Agent, Multimodal, etc.):
```bash
cd proposed_solution
# Ablation E1 (No Critic Agent)
python3 evaluation/run_eval.py --mode ablation_e1

# Ablation E2 (No Multimodal Grounding)
python3 evaluation/run_eval.py --mode ablation_e2
```

---

## 4. Understanding Results
Both evaluation scripts output performance metrics including:
- **P@k (Precision at k):** Percentage of retrieved concepts that are relevant.
- **nDCG@5:** Normalized Discounted Cumulative Gain (ranking quality).
- **Hallucination Rate:** Percentage of queries that generated non-existent concepts.

The final comparison of these metrics can be found in the generated `project_review_summary.txt`.
