import os
import aiofiles
from pathlib import Path

async def write_file(project_name: str, file_path: str, content: str):
    base_dir = Path("./output")
    full_path = base_dir / project_name / file_path
    
    # Create parent directories
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
        await f.write(content)
        
    print(f"✅ Written: {file_path}")
