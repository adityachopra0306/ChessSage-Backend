import asyncio
from services.gemini_api import generate_basic_stats_prompt
from utils.api_utils import select_key, prompt_gemini
from .test_get_stats import test_get_basic_stats
from .test_preprocess import test_preprocess_profile

async def test_get_gemini_basic_prompt():
    stats = await test_get_basic_stats()
    profile = await test_preprocess_profile()

    prompt_text = generate_basic_stats_prompt(
        player_profile=profile,
        basic_stats=stats,
        tone = "Be polite and motivating.",
        background = "Casual Chess player",
        length = 500,
        num_days = 365*3
    )

    response = prompt_gemini(prompt_text, select_key())

    assert isinstance(response, dict), "Response should be a dictionary"
    assert "error" not in response, f"Response returns an error: {response['error']}"
    
    result_text = response["result"]
    assert isinstance(result_text, str), "Result should be a string"
    assert len(result_text.strip()) > 20, "Result should be a meaningful coaching message"

    return response

if __name__ == "__main__":
    res = asyncio.run(test_get_gemini_basic_prompt())
    print("test_get_gemini_basic_prompt works correctly.\n")
    print(res['result'])