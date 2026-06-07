# marco_ops.py
import os
import sys
import json
import argparse
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multimodal.vision_processor import process_image
from multimodal.agent import preprocess_artifact
from agents.graph import run_marco

def op_vision(image_path: str):
    """Operation 1: Vision Processing only."""
    print(f"\n[Vision] Processing image: {image_path}...")
    try:
        result = process_image(image_path, prompt_type="diagram")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error in Vision: {e}")

def op_file(file_path: str):
    """Operation 2: File (YAML/TF) Processing only."""
    print(f"\n[File] Parsing artifact: {file_path}...")
    try:
        result = preprocess_artifact(file_path)
        # We only print the raw extraction and normalised concepts for clarity
        output = {
            "type": result.get("artifact_type"),
            "normalised": result.get("normalised_concepts"),
            "enrichment": result.get("query_enrichment")
        }
        print(json.dumps(output, indent=2))
        return result
    except Exception as e:
        print(f"Error in File Parsing: {e}")

def op_rag(query: str, context: str = ""):
    """Operation 3: RAG Operation only."""
    print(f"\n[RAG] Running query: '{query}'")
    if context:
        print(f"[RAG] Using context: {context[:100]}...")
    
    try:
        result = run_marco(query, context)
        
        print("\n--- RESOLUTION ---")
        print(result.get("final_resolution"))
        
        print("\n--- MAPPINGS ---")
        for m in result.get("final_mappings", []):
            print(f"- {m.get('devops_concept')} <-> {m.get('msa_concept')} ({m.get('taxonomy_category')})")
        
        return result
    except InterruptedError as e:
        print(f"\n[RAG] Clarification needed: {e}")
    except Exception as e:
        print(f"Error in RAG: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MARCO Operations Script")
    subparsers = parser.add_subparsers(dest="command", help="Operation to perform")

    # Vision Subcommand
    vis_parser = subparsers.add_parser("vision", help="Process an architecture diagram")
    vis_parser.add_argument("path", help="Path to image file")

    # File Subcommand
    file_parser = subparsers.add_parser("file", help="Parse CI/CD or IaC files")
    file_parser.add_argument("path", help="Path to YAML or TF file")

    # RAG Subcommand
    rag_parser = subparsers.add_parser("rag", help="Run Agentic RAG query")
    rag_parser.add_argument("query", help="User query")
    rag_parser.add_argument("--file", help="Optional artifact file to enrich query")

    args = parser.parse_args()

    if args.command == "vision":
        op_vision(args.path)
    elif args.command == "file":
        op_file(args.path)
    elif args.command == "rag":
        context = ""
        if args.file:
            # Check if file exists
            if os.path.exists(args.file):
                res = preprocess_artifact(args.file)
                context = res.get("query_enrichment", "")
            else:
                print(f"Warning: File {args.file} not found. Running without context.")
        op_rag(args.query, context)
    else:
        parser.print_help()
