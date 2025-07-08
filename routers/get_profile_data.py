from fastapi import APIRouter, Request
from state.user_state import UserInfo, set_user_info, get_user_config
from services.chess_api import get_profile, get_stats, get_games
from services.preprocess import preprocess_games, preprocess_profile, preprocess_stats, split_by_mode

import asyncio
import pandas as pd

router = APIRouter()

@router.post('/profile_data/{user_id}')
async def get_profile_data(user_id: str, request: Request):
    config = await get_user_config(user_id)
    if not config:
        return {'status': 'error', 'reason': 'User config not found'}

    username = config.username
    profile, stats, games = await asyncio.gather(
        get_profile(username, request),
        get_stats(username, request),
        get_games(username, config.num_days, request)
    )
    
    loop = asyncio.get_running_loop()
    df = pd.DataFrame(games)

    profile, stats, games = await asyncio.gather(
        loop.run_in_executor(None, preprocess_profile, profile),
        loop.run_in_executor(None, preprocess_stats, stats),
        loop.run_in_executor(None, preprocess_games, df, username),
    )

    games = await loop.run_in_executor(None, split_by_mode, games)
    user_info = UserInfo(profile=profile, stats=stats, games=games)
    await set_user_info(user_id, user_info)

    return {'status': 'stored'}