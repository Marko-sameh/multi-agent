import asyncio
from agents.pm_agent import run_pm_agent
from agents.coder_agent import run_coder_agent
from agents.reviewer_agent import run_reviewer_agent
from tools.file_writer import write_file
from tools.project_zip import zip_project

async def run_pipeline(requirement: str) -> dict:
    print("[Graph] Starting run_pipeline")
    
    # 1. Run PM Agent
    plan = await run_pm_agent(requirement)
    project_name = plan.get("project_name", "generated_project")
    tasks = plan.get("tasks", [])
    
    # 2. Print: project name + task count
    print(f"[Graph] Project: {project_name} | Tasks: {len(tasks)}")
    
    # 3. Build initial project_context
    tech_stack = plan.get("tech_stack", {})
    project_context = f"Tech Stack:\nFrontend: {tech_stack.get('frontend')}\nBackend: {tech_stack.get('backend')}\nDatabase: {tech_stack.get('database')}\n\nCompleted files:\n"
    
    files_generated = 0
    tasks_completed = 0
    
    # 4. Loop over tasks sequentially
    for task in tasks:
        task_id = task.get('id')
        task_title = task.get('title')
        print(f"[Graph] Task {task_id}: {task_title}")
        
        # Run Coder Agent
        coder_res = await run_coder_agent(task, project_context)
        
        for file_obj in coder_res.get("files", []):
            file_path = file_obj["file_path"]
            content = file_obj["content"]
            task_desc = f"{task_title}: {task.get('description')}"
            
            # Reviewer Loop
            retries = 0
            while retries < 2:
                review = await run_reviewer_agent(file_path, content, task_desc)
                status = review.get("status")
                
                if status == "PASS":
                     break
                elif status == "FIX":
                     rev_code = review.get("revised_code")
                     if rev_code:
                         content = rev_code
                     retries += 1
                else:
                     break
            
            # Write file
            await write_file(project_name, file_path, content)
            files_generated += 1
            project_context += f"- {file_path}\n"
            
        tasks_completed += 1
        
    # 5. Zip project
    loop = asyncio.get_event_loop()
    zip_path = await loop.run_in_executor(None, zip_project, project_name)
    
    # 6. Return response
    return {
        "project_name": project_name,
        "files_generated": files_generated,
        "tasks_completed": tasks_completed,
        "zip_path": zip_path
    }
