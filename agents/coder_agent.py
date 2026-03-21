from llm_router import route
from prompts.coder_prompt import build_coder_prompt


async def run_coder_agent(task: dict, project_context: str) -> dict:
    result = {"task_id": task.get("id"), "files": []}
    
    task_desc = f"{task.get('title', '')}: {task.get('description', '')}"

    for file_path in task.get("file_paths", []):
        prompt = build_coder_prompt(task_desc, file_path, project_context)
        
        response = await route("coder", prompt)
        
        # Extract purely the code, clean markdown if needed, but coder shouldn't output it
        # Sometimes coder still wraps in ```typescript ... ```
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if len(lines) > 1:
                 # Remove first line if it's ```lang
                 cleaned = "\n".join(lines[1:])
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()

        result["files"].append({
            "file_path": file_path,
            "content": cleaned
        })
        
    return result
