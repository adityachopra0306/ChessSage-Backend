import os
import random
from google import genai

from dotenv import load_dotenv
load_dotenv()


def select_key(user_key = None):
    if user_key:
        return user_key

    keys_raw = os.getenv("GEMINI_API_KEYS", "")
    keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
    
    if not keys:
        raise RuntimeError("No Gemini API keys found in environment.")
    
    return random.choice(keys)

async def check_key(key):
    if not key:
        return {"valid": False, "error": 'No key provided'}
    
    client = genai.Client(api_key = key)

    try:
        response = await client.aio.models.generate_content(
    model='gemini-2.0-flash', contents='ping'
    )
        return {"valid": True, "response": response.text.strip()}
    except Exception as e:
        return {"valid": False, "error": str(e)}
    
async def prompt_gemini(prompt, key):
    if not key:
        return {"valid": False, "error": 'No key provided'}
    
    client = genai.Client(api_key = key)

    try:
        response = await client.aio.models.generate_content(
    model='gemini-2.0-flash', contents = prompt
    )
        return {"valid": True, "response": response.text.strip()}
    except Exception as e:
        return {"valid": False, "error": str(e)}