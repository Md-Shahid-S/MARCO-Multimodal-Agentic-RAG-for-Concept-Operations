# knowledge_base/builder.py
import json, faiss, numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "knowledge_base/index/faiss_hnsw.bin"
META_PATH  = "knowledge_base/index/metadata.json"

def build_index(concept_pairs_path: str) -> None:
    print(f"Loading concept pairs from {concept_pairs_path}...")
    with open(concept_pairs_path) as f:
        pairs = json.load(f)

    print(f"Loading model {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Build text for each concept: label + definition
    print("Encoding embeddings...")
    texts = [f"{p['devops_concept']}: {p.get('definition', '')}" for p in pairs]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    dim = embeddings.shape[1]
    print(f"Building HNSW index with dimension {dim}...")
    # HNSW index — supports incremental add()
    index = faiss.IndexHNSWFlat(dim, 32)   # 32 = M parameter
    index.hnsw.efConstruction = 200
    index.add(embeddings.astype(np.float32))

    # Ensure output directory exists relative to current working directory
    # If run from 'marco' dir, it will be 'knowledge_base/index/'
    output_dir = Path("knowledge_base/index")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(output_dir / "faiss_hnsw.bin"))

    # Save metadata alongside
    metadata = [{"id": i, **p} for i, p in enumerate(pairs)]
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Index built: {index.ntotal} vectors, dim={dim}")

if __name__ == "__main__":
    # Path relative to project root 'marco'
    build_index("data/base/concept_pairs.json")
