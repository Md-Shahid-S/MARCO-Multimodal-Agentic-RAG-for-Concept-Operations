# agents/planner.py
import json, os
from groq import Groq
from agents.state import MARCOState
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLANNER_SYSTEM_PROMPT = """
You are the central routing and planning agent for MARCO, an expert DevOps and Microservice Architecture alignment framework. 

Your job is to analyze the user's architectural query and determine the best retrieval strategy. 

Rules:
1. ALWAYS attempt to retrieve data and answer the user's question to the best of your ability based on the provided context.
2. If the query is completely unintelligible or fundamentally unanswerable without more information (e.g., "fix it" or "what is the best one"), set is_ambiguous to true and provide a specific clarification question.
3. If the query is answerable but lacks specific environmental context (e.g., internal vs. external traffic), you should STILL attempt to answer it generally (set is_ambiguous to false). You can include a clarifying question in the 'clarification_question' field to be asked *after* the initial answer is given.
4. Decompose the query into sub-questions optimized for vector search.

Respond strictly in the following JSON format:
{
  "is_ambiguous": boolean,
  "clarification_question": "String (Optional follow-up question, or null)",
  "sub_questions": ["List of strings optimized for semantic search"]
}
"""

import time
def run_planner(state: MARCOState) -> MARCOState:
    query   = state["original_query"]
    context = state.get("artifact_context", "")
    
    plan = {
        "is_ambiguous": False,
        "clarification_question": "",
        "sub_questions": [query]
    }

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[{"role":"user",
                           "content": PLANNER_SYSTEM_PROMPT + f"\n\nQuery: {query}\nArtifact Context: {context}"}],
                temperature=float(os.getenv("GROQ_TEMPERATURE", 0.1)),
                max_tokens=512
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json","").replace("```","").strip()
            parsed_plan = json.loads(raw)
            plan.update(parsed_plan)
            break
        except Exception as e:
            if attempt == 2:
                print(f"[Planner] Failed after 3 attempts: {e}")
            time.sleep(2)

    # Human-in-the-loop flags
    state["requires_clarification"] = plan.get("is_ambiguous", False)
    state["clarification_message"]  = plan.get("clarification_question", "")
    
    # Standard outputs
    state["intent"]              = "bidirectional" # Defaulted for downstream agents
    state["taxonomy_categories"] = ["Deployment Automation", "Observability", "Scalability", "Security", "Configuration"]
    state["sub_questions"]       = plan.get("sub_questions", [query])
    
    if "reasoning_trace" not in state:
        state["reasoning_trace"] = []
        
    state["reasoning_trace"].append(
        f"[Planner] Ambiguous: {state['requires_clarification']} | "
        f"Sub-Qs: {len(state.get('sub_questions', []))} | "
        f"Clarification Msg: {state['clarification_message']}"
    )
    return state
