import asyncio, json
from services.get_stats import get_basic_stats, get_detailed_stats
from .test_preprocess import test_preprocess_games, test_preprocess_stats

async def test_get_basic_stats():
    games = await test_preprocess_games()
    stats = await test_preprocess_stats()
    return get_basic_stats(games, stats)

if __name__ == "__main__":
    asyncio.run(test_get_basic_stats())