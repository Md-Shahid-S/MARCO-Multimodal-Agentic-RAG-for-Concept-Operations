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
        from dotenv import load_dotenv
        load_dotenv()
        
        embed_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        reranker_model_name = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        index_path = os.getenv("FAISS_INDEX_PATH", "knowledge_base/index/faiss_hnsw.bin")
        
        _embedder  = SentenceTransformer(embed_model_name)
        _reranker  = CrossEncoder(reranker_model_name)
        _index     = faiss.read_index(index_path)
        with open("knowledge_base/index/metadata.json") as f:
            _metadata = json.load(f)
        # Build BM25 over text corpus
        corpus = [f"{m.get('devops_concept', '')} {m.get('definition','')}" for m in _metadata]
        tokenised = [doc.lower().split() for doc in corpus]
        _bm25 = BM25Okapi(tokenised)

def run_retriever(state: MARCOState) -> MARCOState:
    _load_models()
    top_k = int(os.getenv("TOP_K", 5))
    all_candidates = []

    # Ensure we have sub_questions to search (fallback to original query)
    sub_questions = state.get("sub_questions")
    if not sub_questions:
        sub_questions = [state["original_query"]]

    for sub_q in sub_questions:
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
            if idx >= 0 and idx < len(_metadata):
                hit = dict(_metadata[idx])
                hit["bm25_score"] = float(bm25_scores[idx])
                hit["sub_question"] = sub_q
                sparse_hits.append(hit)

        # Merge and deduplicate by concept ID
        merged = {h["id"]: h for h in dense_hits + sparse_hits}.values()
        merged = list(merged)[:top_k * 3]

        if not merged:
            continue

        # Cross-encoder reranking
        pairs   = [(sub_q, f"{h.get('devops_concept', '')}: {h.get('definition','')}")
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
    
    if "reasoning_trace" not in state:
        state["reasoning_trace"] = []
    
    trace_msg = (f"[Retriever] Retrieved {len(final)} candidates across "
                 f"{len(sub_questions)} sub-questions. ")
    if final:
        trace_msg += f"Top rerank score: {final[0]['rerank_score']:.3f}"
    
    state["reasoning_trace"].append(trace_msg)
    
    return state
