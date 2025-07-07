import pandas as pd
import asyncio
from datetime import datetime

from services.preprocess import preprocess_games, preprocess_profile, preprocess_stats, split_by_mode
from .test_chess_api import test_get_games, test_get_stats, test_get_profile

async def test_preprocess_games():
    games_df = pd.DataFrame(await test_get_games(365*3))
    
    processed_games = preprocess_games(games_df, 'revamb')
    assert isinstance(processed_games, pd.DataFrame)
    assert not processed_games.empty, "Processed DataFrame is empty"

    expected_columns = [
        'player_color', 'player_rating', 'opponent_rating',
        'player_accuracy', 'opponent_accuracy',
        'opponent_username', 'result', 'eco_name', 'end_time'
    ]
    for col in expected_columns:
        assert col in processed_games.columns, f"Missing expected column: {col}"

    split = split_by_mode(processed_games)
    assert isinstance(split, dict), 'Invalid split_by_mode datatype'
    assert len(split) == 4, 'Missing mode in split_by_mode'
    return split

async def test_preprocess_profile():
    profile = await test_get_profile()
    processed_profile = preprocess_profile(profile)

    assert isinstance(processed_profile, dict)
    assert "last_online" in processed_profile
    assert "joined" in processed_profile

    date_format = "%Y-%m-%d"
    try:
        datetime.strptime(processed_profile["last_online"], date_format)
        datetime.strptime(processed_profile["joined"], date_format)
    except ValueError:
        assert False, "Date fields are not properly formatted as YYYY-MM-DD"

    return processed_profile

async def test_preprocess_stats():
    stats = await test_get_stats()
    processed = preprocess_stats(stats)

    assert isinstance(processed, dict)

    def check_dates(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "date":
                    assert isinstance(v, str)
                    datetime.strptime(v, "%Y-%m-%d")
                else:
                    check_dates(v)
        elif isinstance(obj, list):
            for item in obj:
                check_dates(item)

    check_dates(processed)

    return processed


async def main():
    await test_preprocess_games()
    await test_preprocess_profile()
    await test_preprocess_stats()
    print('Preprocessing functions work correctly.')

if __name__ == "__main__":
    asyncio.run(main())