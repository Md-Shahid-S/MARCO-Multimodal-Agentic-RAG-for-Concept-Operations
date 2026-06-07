# knowledge_base/chroma_store.py
import chromadb, json
from pathlib import Path

class ChromaConceptStore:
    def __init__(self, persist_dir: str = "knowledge_base/chroma"):
        # Ensure persist_dir exists
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("devops_msa_concepts")

    def upsert(self, concepts: list[dict]) -> None:
        ids        = [str(c["id"]) for c in concepts]
        documents  = [f"{c['devops_concept']}: {c.get('definition','')}" for c in concepts]
        # Metadata must be simple types (str, int, float, bool)
        metadatas  = [{k: str(v) for k, v in c.items()} for c in concepts]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def get(self, concept_id: str) -> dict | None:
        result = self.collection.get(ids=[concept_id])
        return result["metadatas"][0] if result["ids"] else None

if __name__ == "__main__":
    # Test/Initialize with metadata.json
    import os
    store = ChromaConceptStore()
    meta_path = "knowledge_base/index/metadata.json"
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            metadata = json.load(f)
        store.upsert(metadata)
        print(f"Upserted {len(metadata)} concepts to ChromaDB")
