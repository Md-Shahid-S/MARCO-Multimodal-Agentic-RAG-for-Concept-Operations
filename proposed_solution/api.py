import os
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import uvicorn
import tempfile
import shutil
import os
import sys

# Add current directory to path so we can import agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.graph import run_marco
from multimodal.agent import preprocess_artifact, SUPPORTED_EXTENSIONS

app = FastAPI(
    title="MARCO AI API",
    description="Backend API for Multimodal Agentic RAG for DevOps–MSA Concept Alignment",
    version="1.0.0"
)

# Enable CORS for Next.js frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "message": "MARCO AI API is running"}

@app.get("/metadata")
async def get_metadata():
    """Returns system metadata like supported file extensions."""
    return {
        "supported_extensions": list(SUPPORTED_EXTENSIONS.keys()),
        "artifact_types": list(set(SUPPORTED_EXTENSIONS.values())),
        "version": "1.0.0"
    }

@app.post("/chat")
async def chat_endpoint(
    query: str = Form(...),      # Must match "query"
    file: UploadFile = File(None) # Must match "file"
):
    """Main chat endpoint that handles text queries and optional file artifacts."""
    artifact_context = ""
    parsed_artifact = None
    
    if file:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            return {"status": "error", "message": f"Unsupported file type: {suffix}"}

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            # Process the artifact (Diagram, YAML, TF, etc.)
            parsed_artifact = preprocess_artifact(tmp_path)
            artifact_context = parsed_artifact.get("query_enrichment", "")
            os.remove(tmp_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise HTTPException(status_code=500, detail=f"Error processing artifact: {str(e)}")

    # Run the Agentic RAG workflow
    try:
        result = run_marco(query, artifact_context)
        return {
            "status": "success",
            "context_analysis": result.get("context_analysis", ""),
            "final_resolution": result.get("final_resolution", ""),
            "suggested_next_steps": result.get("suggested_next_steps", []),
            "answer": result.get("final_mappings", []),
            "retrieved_chunks": result.get("graded_candidates", []),
            "reasoning": result.get("reasoning_trace", []),
            "out_of_scope_notes": result.get("out_of_scope_notes", ""),
            "artifact_details": parsed_artifact if parsed_artifact else None
        }
    except InterruptedError as e:
        return {
            "status": "success",
            "final_resolution": f"🤔 **Clarification Needed:** {str(e)}\n\n_Please reply with more details to proceed._",
            "reasoning": ["[Planner] Execution paused. Requesting human clarification."]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
