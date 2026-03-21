import zipfile
import os
from pathlib import Path

def zip_project(project_name: str) -> str:
    base_dir = Path(f"./output/{project_name}")
    zip_path = Path(f"./output/{project_name}.zip")
    
    if not base_dir.exists():
        raise FileNotFoundError(f"Directory not found: {base_dir}")
        
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_full_path = Path(root) / file
                arcname = file_full_path.relative_to(base_dir)
                zf.write(file_full_path, arcname)
                
    return str(zip_path)
