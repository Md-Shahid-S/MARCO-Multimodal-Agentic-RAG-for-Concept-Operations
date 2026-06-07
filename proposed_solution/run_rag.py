# run_rag.py
import sys
import argparse
from marco_ops import op_rag
from multimodal.agent import preprocess_artifact

def main():
    parser = argparse.ArgumentParser(description="Run MARCO RAG Operation")
    parser.add_argument("query", help="The question to ask")
    parser.add_argument("--file", help="Optional artifact to provide context")
    
    args = parser.parse_args()
    
    context = ""
    if args.file:
        try:
            res = preprocess_artifact(args.file)
            context = res.get("query_enrichment", "")
        except Exception as e:
            print(f"Error loading context: {e}")
            
    op_rag(args.query, context)

if __name__ == "__main__":
    main()
