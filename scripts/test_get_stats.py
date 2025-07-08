import asyncio
from services.get_stats import get_basic_stats, get_detailed_stats
from .test_preprocess import test_preprocess_games, test_preprocess_stats

async def test_get_basic_stats():
    games = await test_preprocess_games()
    stats = await test_preprocess_stats()

    result = get_basic_stats(games, stats)

    assert isinstance(result, dict)

    assert "all_time_tactics_best" in result
    assert "all_time_puzzle_rush" in result

    modes = [m for m in ['rapid', 'blitz', 'bullet', 'daily'] if m in result]
    assert len(modes) > 0

    for mode in modes:
        data = result[mode]
        assert isinstance(data, dict)
        assert "white" in data and "black" in data
        assert "current" in data
        assert "loss_reason" in data

    return result

async def test_get_detailed_stats():
    games = await test_preprocess_games()
    stats = await test_preprocess_stats()
    res = {mk: get_detailed_stats(games = games, mode_key = mk) for mk in ['rapid', 'bullet', 'blitz', 'daily']}

    assert isinstance(res, dict), 'Invalid datatype'
    assert len(res) == 4, 'All modes not covered in get_detailed_stats'
    for mode_key, mode_stats in res.items():
        assert isinstance(mode_stats, dict), f'{mode_key} - Invalid datatype'
        assert len(mode_stats) == 3, f'{mode_key} - Improper output, i.e. NOT (opening, winloss, progression)'
    return res

if __name__ == "__main__":
    asyncio.run(test_get_basic_stats())
    print('Get_basic_stats works correctly.')
    asyncio.run(test_get_detailed_stats())
    print('Get_detailed_stats works correctly.')