def build_reviewer_prompt(file_path: str, code_content: str, task_desc: str) -> str:
    return f"""You are a Senior Code Reviewer expert in rigorous software engineering.

You will review the file below based on its task requirements.
Output ONLY valid JSON matching the exact structure below.
Do not wrap it in markdown block. Do not write any explanations outside the JSON.

JSON Structure required:
{{
  "status": "PASS" | "FIX",
  "issues": [
    {{
      "severity": "critical|warning",
      "description": "what is wrong",
      "fix": "how to fix"
    }}
  ],
  "revised_code": "full corrected file as a single string if FIX, empty string if PASS"
}}

Task description:
{task_desc}

File path: {file_path}

Code Content:
{code_content}
"""
