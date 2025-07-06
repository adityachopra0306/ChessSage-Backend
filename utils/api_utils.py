import os
import random
import google.generativeai as genai

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

def check_key(key):
    genai.configure(api_key=key)

    try:
        genmodel = genai.GenerativeModel("gemini-2.0-flash")
        genmodel.generate_content("ping")
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}
    
def prompt_gemini(prompt, key):
    genai.configure(api_key=key)

    try:
        genmodel = genai.GenerativeModel("gemini-2.0-flash")
        content = genmodel.generate_content(prompt).text.strip()
        return {"valid": True, "result": content}
    except Exception as e:
        return {"valid": False, "error": str(e)}