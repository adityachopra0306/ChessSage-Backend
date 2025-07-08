from fastapi import APIRouter
import pandas as pd
import asyncio

from state.user_state import get_user_info, get_user_results_field, set_user_results_field
from services.get_stats import get_basic_stats, get_detailed_stats

router = APIRouter()

@router.post('/basic/{user_id}')
async def basic_stats(user_id: str):
    if (cached := await get_user_results_field(user_id, 'basic_stats')):
        print('cached')
        return cached
    
    user_info = await get_user_info(user_id)

    loop = asyncio.get_running_loop()
    games = {key: pd.DataFrame(val) for key, val in user_info.games.items()}

    stats = await loop.run_in_executor(None, get_basic_stats, games, user_info.stats)
    
    await set_user_results_field(user_id, 'basic_stats', stats)
    
    return stats

@router.post('/detail/{user_id}/{mode_key}')
async def detailed_stats(user_id: str, mode_key: str):
    if (cached := await get_user_results_field(user_id, f'detailed_stats_{mode_key}')):
        print('cached')
        return cached
    
    user_info = await get_user_info(user_id)

    loop = asyncio.get_running_loop()
    games = {key: pd.DataFrame(val) for key, val in user_info.games.items()}
    
    stats = await loop.run_in_executor(None, get_detailed_stats, games, mode_key)
    await set_user_results_field(user_id, f'detailed_stats_{mode_key}', stats)
    return stats