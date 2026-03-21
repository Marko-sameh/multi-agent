import os
import httpx
from dotenv import load_dotenv

load_dotenv()

LAPTOP_A_URL = os.getenv("LAPTOP_A_URL", "http://100.99.177.54:11434")
LAPTOP_B_URL = os.getenv("LAPTOP_B_URL", "http://100.122.244.5:11434")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.0-flash"
OLLAMA_CODER = "qwen2.5-coder:7b"
OLLAMA_PM = "qwen2.5:7b"


async def call_ollama(prompt: str, base_url: str, model: str, temperature: float) -> str:
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")


async def call_groq(prompt: str, temperature: float) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def call_gemini(prompt: str, temperature: float) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature}
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
             return data["candidates"][0]["content"]["parts"][0]["text"]
        return ""


async def route(agent: str, prompt: str) -> str:
    temperature = 0.1 if agent == "coder" else 0.2

    if agent == "pm":
        # pm: groq → gemini → ollama_b
        try:
            return await call_groq(prompt, temperature)
        except Exception as e:
            print(f"[Router] PM groq failed: {e}. Trying gemini...")
            try:
                return await call_gemini(prompt, temperature)
            except Exception as e2:
                print(f"[Router] PM gemini failed: {e2}. Trying ollama_b...")
                return await call_ollama(prompt, LAPTOP_B_URL, OLLAMA_PM, temperature)

    elif agent == "coder":
        # coder: ollama_a → groq → gemini
        try:
            return await call_ollama(prompt, LAPTOP_A_URL, OLLAMA_CODER, temperature)
        except Exception as e:
            print(f"[Router] Coder ollama_a failed: {e}. Trying groq...")
            try:
                return await call_groq(prompt, temperature)
            except Exception as e2:
                print(f"[Router] Coder groq failed: {e2}. Trying gemini...")
                return await call_gemini(prompt, temperature)

    elif agent == "reviewer":
        # reviewer: gemini → groq
        try:
            return await call_gemini(prompt, temperature)
        except Exception as e:
            print(f"[Router] Reviewer gemini failed: {e}. Trying groq...")
            return await call_groq(prompt, temperature)

    else:
        raise ValueError(f"Unknown agent: {agent}")
