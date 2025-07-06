import pandas as pd
import asyncio

from services.preprocess import preprocess_games, preprocess_profile, preprocess_stats, split_by_mode
from .test_chess_api import test_get_games, test_get_stats, test_get_profile

async def test_preprocess_games():
    games_df = pd.DataFrame(await test_get_games(365*3))
    return split_by_mode(preprocess_games(games_df, 'revamb'))

async def test_preprocess_profile():
    prof = await test_get_profile()
    return preprocess_profile(prof)

async def test_preprocess_stats():
    stats = await test_get_stats()
    return preprocess_stats(stats)

async def main():
    print(await test_preprocess_games())
    print(await test_preprocess_profile())
    print(await test_preprocess_stats())
    
if __name__ == "__main__":
    asyncio.run(main())