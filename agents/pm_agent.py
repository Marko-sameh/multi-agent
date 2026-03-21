import json
from llm_router import route
from prompts.pm_prompt import build_pm_prompt


async def run_pm_agent(requirement: str) -> dict:
    prompt = build_pm_prompt(requirement)
    
    response = await route("pm", prompt)
    
    # Clean response (strip markdown fences if present)
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        plan = json.loads(cleaned)
        return plan
    except json.JSONDecodeError as e:
        raise ValueError(f"PM Agent returned invalid JSON: {e}\nRaw Response: {cleaned}")
