import json
from llm_router import route
from prompts.reviewer_prompt import build_reviewer_prompt


async def run_reviewer_agent(file_path: str, content: str, task_desc: str) -> dict:
    prompt = build_reviewer_prompt(file_path, content, task_desc)
    
    response = await route("reviewer", prompt)
    
    # Clean response
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        review_res = json.loads(cleaned)
        return review_res
    except json.JSONDecodeError as e:
        # Fallback handling just in case
        print(f"[Reviewer] JSON parse failed: {e}. Defaulting to FIX.")
        return {
            "status": "FIX",
            "issues": [{"severity": "critical", "description": "Invalid JSON from Reviewer", "fix": "Rewrite cleanly"}],
            "revised_code": content # return original back to force retry
        }
